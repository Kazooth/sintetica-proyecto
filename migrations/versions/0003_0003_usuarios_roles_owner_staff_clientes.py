from alembic import op

revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
    -- Roles (si tu app los usa)
    INSERT INTO roles (name, description) VALUES
    ('ADMIN', 'Administrador del sistema'),
    ('OWNER', 'Propietario del establecimiento'),
    ('STAFF', 'Empleado de la sede'),
    ('CUSTOMER', 'Cliente final')
    ON CONFLICT (name) DO NOTHING;

    -- Seed personas y usuarios (schema actual usa persons + users.person_id)
    WITH data(email, first_name, last_name, role) AS (
      VALUES
        ('owner@lanarino.local',   'Luis',   'Herrera',  'OWNER'),
        ('cajero1@lanarino.local', 'Paula',  'Martínez', 'STAFF'),
        ('cajero2@lanarino.local', 'Diego',  'Gómez',    'STAFF'),
        ('admin@lanarino.local',   'Andrea', 'Suárez',   'ADMIN'),
        ('cliente1@lanarino.local','Camilo', 'Rojas',    'CUSTOMER'),
        ('cliente2@lanarino.local','Laura',  'Rivera',   'CUSTOMER'),
        ('cliente3@lanarino.local','Julián', 'Pardo',    'CUSTOMER'),
        ('cliente4@lanarino.local','Sofía',  'López',    'CUSTOMER'),
        ('cliente5@lanarino.local','Manuel', 'Torres',   'CUSTOMER')
    )
    -- 1) personas (idempotente por email)
    INSERT INTO persons (first_name, last_name, email)
    SELECT d.first_name, d.last_name, d.email
    FROM data d
    ON CONFLICT (email) DO NOTHING;

    -- 2) usuarios (idempotente por email)
    INSERT INTO users (email, password_hash, person_id, role)
    SELECT d.email, 'hash-demo', p.id, d.role
    FROM data d
    JOIN persons p ON p.email = d.email
    ON CONFLICT (email) DO NOTHING;

    -- asignar owner a establecimiento (si no se asignó aún)
    UPDATE establishments e
    SET owner_user_id = (SELECT id FROM users WHERE email='owner@lanarino.local')
    WHERE e.name='Canchas Sintéticas La Nariño' AND e.owner_user_id IS NULL;
    """
    )
