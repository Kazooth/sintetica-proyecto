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
    -- 1) personas (idempotente por email)
    INSERT INTO persons (first_name, last_name, email)
    SELECT d.first_name, d.last_name, d.email
    FROM (
      VALUES
        ('Luis',   'Herrera',  'owner@lanarino.local'),
        ('Paula',  'Martínez', 'cajero1@lanarino.local'),
        ('Diego',  'Gómez',    'cajero2@lanarino.local'),
        ('Andrea', 'Suárez',   'admin@lanarino.local'),
        ('Camilo', 'Rojas',    'cliente1@lanarino.local'),
        ('Laura',  'Rivera',   'cliente2@lanarino.local'),
        ('Julián', 'Pardo',    'cliente3@lanarino.local'),
        ('Sofía',  'López',    'cliente4@lanarino.local'),
        ('Manuel', 'Torres',   'cliente5@lanarino.local')
    ) AS d(first_name, last_name, email)
    ON CONFLICT (email) DO NOTHING;

    -- 2) usuarios (idempotente por email)
    INSERT INTO users (email, password_hash, person_id, role)
    SELECT u.email, 'hash-demo', p.id, u.role
    FROM (
      VALUES
        ('owner@lanarino.local',   'OWNER'),
        ('cajero1@lanarino.local', 'STAFF'),
        ('cajero2@lanarino.local', 'STAFF'),
        ('admin@lanarino.local',   'ADMIN'),
        ('cliente1@lanarino.local','CUSTOMER'),
        ('cliente2@lanarino.local','CUSTOMER'),
        ('cliente3@lanarino.local','CUSTOMER'),
        ('cliente4@lanarino.local','CUSTOMER'),
        ('cliente5@lanarino.local','CUSTOMER')
    ) AS u(email, role)
    JOIN persons p ON p.email = u.email
    ON CONFLICT (email) DO NOTHING;

    -- asignar owner a establecimiento (si no se asignó aún)
    UPDATE establishments e
    SET owner_user_id = (SELECT id FROM users WHERE email='owner@lanarino.local')
    WHERE e.name='Canchas Sintéticas La Nariño' AND e.owner_user_id IS NULL;
    """
    )
