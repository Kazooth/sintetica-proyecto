from alembic import op

revision = '0010'
down_revision = '0009'
branch_labels = None
depends_on = None

def upgrade():
    op.execute("""
    INSERT INTO establishment_staff (establishment_id, user_id)
    SELECT e.id, u.id
    FROM establishments e, users u
    WHERE e.name='Canchas Sintéticas La Nariño'
      AND u.email IN ('cajero1@lanarino.local','cajero2@lanarino.local')
    ON CONFLICT (establishment_id, user_id) DO NOTHING;
    """)
