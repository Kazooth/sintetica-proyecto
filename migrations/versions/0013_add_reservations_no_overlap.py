"""
Add exclusion constraint to prevent overlapping reservations per resource
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0013_add_reservations_no_overlap'
down_revision = '0012_0012_reservas_ventas_demo'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Ensure btree_gist extension for mixing integer and range exclusion
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist;")
    # Add exclusion constraint using tstzrange on start_ts/end_ts
    op.execute(
        "ALTER TABLE reservations ADD CONSTRAINT reservations_no_overlap EXCLUDE USING gist (resource_id WITH =, tstzrange(start_ts, end_ts, '[)') WITH &&);"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE reservations DROP CONSTRAINT IF EXISTS reservations_no_overlap;")
