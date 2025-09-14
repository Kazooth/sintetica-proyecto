from alembic import op

revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None

def upgrade():
    op.execute("""
    -- Roles (si tu app los usa)
    INSERT INTO roles (name, description) VALUES
    ('ADMIN', 'Administrador del sistema'),
    ('OWNER', 'Propietario del establecimiento'),
    ('STAFF', 'Empleado de la sede'),
    ('CUSTOMER', 'Cliente final')
    ON CONFLICT (name) DO NOTHING;

    -- Usuarios (hash o texto simulado)
    INSERT INTO users (email, password_hash, first_name, last_name, role)
    VALUES 
      ('owner@lanarino.local',   'hash-demo', 'Luis',   'Herrera', 'OWNER'),
      ('cajero1@lanarino.local', 'hash-demo', 'Paula',  'Martínez','STAFF'),
      ('cajero2@lanarino.local', 'hash-demo', 'Diego',  'Gómez',   'STAFF'),
      ('admin@lanarino.local',   'hash-demo', 'Andrea', 'Suárez',  'ADMIN'),
      ('cliente1@lanarino.local','hash-demo', 'Camilo', 'Rojas',   'CUSTOMER'),
      ('cliente2@lanarino.local','hash-demo', 'Laura',  'Rivera',  'CUSTOMER'),
      ('cliente3@lanarino.local','hash-demo', 'Julián', 'Pardo',   'CUSTOMER'),
      ('cliente4@lanarino.local','hash-demo', 'Sofía',  'López',   'CUSTOMER'),
      ('cliente5@lanarino.local','hash-demo', 'Manuel', 'Torres',  'CUSTOMER')
    ON CONFLICT (email) DO NOTHING;

    -- asignar owner a establecimiento (si no se asignó aún)
    UPDATE establishments e
    SET owner_user_id = (SELECT id FROM users WHERE email='owner@lanarino.local')
    WHERE e.name='Canchas Sintéticas La Nariño' AND e.owner_user_id IS NULL;
    """)
