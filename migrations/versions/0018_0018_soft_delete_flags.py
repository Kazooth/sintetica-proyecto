"""0018 add soft delete flags

Revision ID: 0018
Revises: 0017_merge_cleanup
Create Date: 2025-10-20 22:10:00

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "0018"
down_revision = "0017_merge_cleanup"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
DO $$
BEGIN
  -- establishments.is_active
  BEGIN
    IF NOT EXISTS (
      SELECT 1 FROM information_schema.columns
      WHERE table_name = 'establishments' AND column_name = 'is_active'
    ) THEN
      ALTER TABLE establishments ADD COLUMN is_active BOOLEAN DEFAULT TRUE;
      UPDATE establishments SET is_active = TRUE WHERE is_active IS NULL;
    END IF;
  EXCEPTION WHEN OTHERS THEN NULL; END;

  -- product_categories.is_active
  BEGIN
    IF NOT EXISTS (
      SELECT 1 FROM information_schema.columns
      WHERE table_name = 'product_categories' AND column_name = 'is_active'
    ) THEN
      ALTER TABLE product_categories ADD COLUMN is_active BOOLEAN DEFAULT TRUE;
      UPDATE product_categories SET is_active = TRUE WHERE is_active IS NULL;
    END IF;
  EXCEPTION WHEN OTHERS THEN NULL; END;
END$$;
        """
    )


def downgrade() -> None:
    # No quitamos columnas en downgrade para no romper datos; operación segura no destructiva.
    pass
