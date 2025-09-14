from alembic import op

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None

def upgrade():
    op.execute("""
    -- Estado y ciudad: Cundinamarca / Girardot
    INSERT INTO states (name)
    VALUES ('Cundinamarca')
    ON CONFLICT (name) DO NOTHING;

    INSERT INTO cities (name, state_id)
    SELECT 'Girardot', s.id
    FROM states s WHERE s.name='Cundinamarca'
    ON CONFLICT (name, state_id) DO NOTHING;

    -- Establecimiento
    INSERT INTO establishments (city_id, owner_user_id, name, phone, address)
    SELECT c.id, NULL, 'Canchas Sintéticas La Nariño', '3053992501',
           'Calle 31 #9-12, Barrio La Nariño'
    FROM cities c
    WHERE c.name='Girardot'
    ON CONFLICT (name, city_id) DO NOTHING;
    """)
