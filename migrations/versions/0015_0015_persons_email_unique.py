"""make persons.email unique

Revision ID: 0015
Revises: 0014
Create Date: 2025-09-19 02:20:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '0015'
down_revision = '0014'
branch_labels = None
depends_on = None


def upgrade():
    # add unique constraint on persons.email only if it does not already exist
    # PostgreSQL doesn't support IF NOT EXISTS for ADD CONSTRAINT, so use a DO block
    op.execute(
        sa.text(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint
                    WHERE conname = 'uq_persons_email'
                ) THEN
                    ALTER TABLE persons
                        ADD CONSTRAINT uq_persons_email UNIQUE (email);
                END IF;
            END$$;
            """
        )
    )


def downgrade():
    # Drop constraint defensively in case it was created outside this migration
    op.execute(sa.text("ALTER TABLE persons DROP CONSTRAINT IF EXISTS uq_persons_email;"))
