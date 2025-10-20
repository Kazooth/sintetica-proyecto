"""
0016: Add exclusion constraint to prevent overlapping reservations per resource
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0016'
down_revision = '0015'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Ensure btree_gist extension for mixing integer and range exclusion
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist;")

    # Pre-clean: cancel later overlapping CONFIRMED reservations to allow adding the constraint
    op.execute(
        """
        UPDATE reservations r1
        SET status = 'CANCELLED'
        FROM reservations r2
        WHERE r1.id > r2.id
          AND r1.resource_id = r2.resource_id
          AND r1.status = 'CONFIRMED' AND r2.status = 'CONFIRMED'
          AND tstzrange(r1.start_ts, r1.end_ts, '[)') && tstzrange(r2.start_ts, r2.end_ts, '[)');
        """
    )

    # Add exclusion constraint using tstzrange on start_ts/end_ts, only for active (CONFIRMED) reservations
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'reservations_no_overlap'
            ) THEN
                ALTER TABLE reservations ADD CONSTRAINT reservations_no_overlap
                EXCLUDE USING gist (
                    resource_id WITH =,
                    tstzrange(start_ts, end_ts, '[)') WITH &&
                )
                WHERE (status = 'CONFIRMED');
            END IF;
        END$$;
        """
    )


def downgrade() -> None:
    op.execute("ALTER TABLE reservations DROP CONSTRAINT IF EXISTS reservations_no_overlap;")
