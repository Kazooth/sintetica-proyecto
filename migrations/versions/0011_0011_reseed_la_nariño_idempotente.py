"""0011 reseed La Nariño (idempotente)

Revision ID: 0011
Revises: 0010
Create Date: 2025-09-09 02:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0011"
down_revision: Union[str, Sequence[str], None] = "0010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Seed idempotente para:
      - Estado y ciudad (Cundinamarca / Girardot)
      - Establecimiento 'Canchas Sintéticas La Nariño'
      - Usuarios (OWNER, ADMIN, STAFF, CLIENTES)
      - Recursos (2 x 5v5, 1 x 8v8)
      - Horarios L-D 08:00–23:30
      - Regla de precio pico 18:00–22:00 (+10k)
      - Categorías y productos
      - Inventario inicial (vía inventory_tx) con created_at=NOW()
      - Asignación del staff al establecimiento
    Además, se asegura el índice único requerido por el trigger de inventory_tx:
      CREATE UNIQUE INDEX IF NOT EXISTS uq_inventory_stock_product_id ON inventory_stock(product_id);
    """

    op.execute(
        """
-- =========================================================
-- 1) Geografía: Cundinamarca / Girardot
-- =========================================================
INSERT INTO states(name)
SELECT 'Cundinamarca'
WHERE NOT EXISTS (SELECT 1 FROM states WHERE name='Cundinamarca');

INSERT INTO cities(name, state_id)
SELECT 'Girardot', s.id
FROM states s
WHERE s.name='Cundinamarca'
  AND NOT EXISTS (SELECT 1 FROM cities c WHERE c.name='Girardot' AND c.state_id=s.id);

-- =========================================================
-- 2) Establecimiento
-- =========================================================
INSERT INTO establishments(city_id, owner_user_id, name, phone, address)
SELECT c.id, NULL, 'Canchas Sintéticas La Nariño', '3053992501', 'Calle 31 #9-12, Barrio La Nariño'
FROM cities c
WHERE c.name='Girardot'
  AND NOT EXISTS (
    SELECT 1 FROM establishments e
    WHERE e.name='Canchas Sintéticas La Nariño' AND e.city_id=c.id
  );

-- =========================================================
-- 3) Usuarios (OWNER/STAFF/CLIENTES)
-- =========================================================
-- personas + usuarios (owner)
INSERT INTO persons(first_name, last_name, email)
SELECT 'Luis','Herrera','owner@lanarino.local'
WHERE NOT EXISTS (SELECT 1 FROM persons WHERE email='owner@lanarino.local');

INSERT INTO users(email, password_hash, person_id, role)
SELECT 'owner@lanarino.local','hash-demo', p.id,'OWNER'
FROM persons p WHERE p.email='owner@lanarino.local'
  AND NOT EXISTS (SELECT 1 FROM users WHERE email='owner@lanarino.local');

INSERT INTO persons(first_name, last_name, email)
SELECT 'Paula','Martínez','cajero1@lanarino.local'
WHERE NOT EXISTS (SELECT 1 FROM persons WHERE email='cajero1@lanarino.local');

INSERT INTO users(email, password_hash, person_id, role)
SELECT 'cajero1@lanarino.local','hash-demo', p.id,'STAFF'
FROM persons p WHERE p.email='cajero1@lanarino.local'
  AND NOT EXISTS (SELECT 1 FROM users WHERE email='cajero1@lanarino.local');

INSERT INTO persons(first_name, last_name, email)
SELECT 'Diego','Gómez','cajero2@lanarino.local'
WHERE NOT EXISTS (SELECT 1 FROM persons WHERE email='cajero2@lanarino.local');

INSERT INTO users(email, password_hash, person_id, role)
SELECT 'cajero2@lanarino.local','hash-demo', p.id,'STAFF'
FROM persons p WHERE p.email='cajero2@lanarino.local'
  AND NOT EXISTS (SELECT 1 FROM users WHERE email='cajero2@lanarino.local');

INSERT INTO persons(first_name, last_name, email)
SELECT 'Andrea','Suárez','admin@lanarino.local'
WHERE NOT EXISTS (SELECT 1 FROM persons WHERE email='admin@lanarino.local');

INSERT INTO users(email, password_hash, person_id, role)
SELECT 'admin@lanarino.local','hash-demo', p.id,'ADMIN'
FROM persons p WHERE p.email='admin@lanarino.local'
  AND NOT EXISTS (SELECT 1 FROM users WHERE email='admin@lanarino.local');

INSERT INTO persons(first_name, last_name, email)
SELECT 'Camilo','Rojas','cliente1@lanarino.local'
WHERE NOT EXISTS (SELECT 1 FROM persons WHERE email='cliente1@lanarino.local');

INSERT INTO users(email, password_hash, person_id, role)
SELECT 'cliente1@lanarino.local','hash-demo', p.id,'CUSTOMER'
FROM persons p WHERE p.email='cliente1@lanarino.local'
  AND NOT EXISTS (SELECT 1 FROM users WHERE email='cliente1@lanarino.local');

INSERT INTO persons(first_name, last_name, email)
SELECT 'Laura','Rivera','cliente2@lanarino.local'
WHERE NOT EXISTS (SELECT 1 FROM persons WHERE email='cliente2@lanarino.local');

INSERT INTO users(email, password_hash, person_id, role)
SELECT 'cliente2@lanarino.local','hash-demo', p.id,'CUSTOMER'
FROM persons p WHERE p.email='cliente2@lanarino.local'
  AND NOT EXISTS (SELECT 1 FROM users WHERE email='cliente2@lanarino.local');

INSERT INTO persons(first_name, last_name, email)
SELECT 'Julián','Pardo','cliente3@lanarino.local'
WHERE NOT EXISTS (SELECT 1 FROM persons WHERE email='cliente3@lanarino.local');

INSERT INTO users(email, password_hash, person_id, role)
SELECT 'cliente3@lanarino.local','hash-demo', p.id,'CUSTOMER'
FROM persons p WHERE p.email='cliente3@lanarino.local'
  AND NOT EXISTS (SELECT 1 FROM users WHERE email='cliente3@lanarino.local');

INSERT INTO persons(first_name, last_name, email)
SELECT 'Sofía','López','cliente4@lanarino.local'
WHERE NOT EXISTS (SELECT 1 FROM persons WHERE email='cliente4@lanarino.local');

INSERT INTO users(email, password_hash, person_id, role)
SELECT 'cliente4@lanarino.local','hash-demo', p.id,'CUSTOMER'
FROM persons p WHERE p.email='cliente4@lanarino.local'
  AND NOT EXISTS (SELECT 1 FROM users WHERE email='cliente4@lanarino.local');

INSERT INTO persons(first_name, last_name, email)
SELECT 'Manuel','Torres','cliente5@lanarino.local'
WHERE NOT EXISTS (SELECT 1 FROM persons WHERE email='cliente5@lanarino.local');

INSERT INTO users(email, password_hash, person_id, role)
SELECT 'cliente5@lanarino.local','hash-demo', p.id,'CUSTOMER'
FROM persons p WHERE p.email='cliente5@lanarino.local'
  AND NOT EXISTS (SELECT 1 FROM users WHERE email='cliente5@lanarino.local');

-- set owner al establecimiento
UPDATE establishments e
SET owner_user_id = u.id
FROM users u
WHERE e.name='Canchas Sintéticas La Nariño' AND u.email='owner@lanarino.local'
  AND (e.owner_user_id IS NULL OR e.owner_user_id <> u.id);

-- =========================================================
-- 4) Recursos (2 de 5v5 a 80k, 1 de 8v8 a 180k)
-- =========================================================
INSERT INTO resources(establishment_id, name, kind, capacity, slot_minutes, price_per_slot, currency, is_active)
SELECT e.id, 'Cancha 5v5 - A', 'cancha_5', 10, 60, 80000, 'COP', TRUE
FROM establishments e
WHERE e.name='Canchas Sintéticas La Nariño'
  AND NOT EXISTS (SELECT 1 FROM resources r WHERE r.establishment_id=e.id AND r.name='Cancha 5v5 - A');

INSERT INTO resources(establishment_id, name, kind, capacity, slot_minutes, price_per_slot, currency, is_active)
SELECT e.id, 'Cancha 5v5 - B', 'cancha_5', 10, 60, 80000, 'COP', TRUE
FROM establishments e
WHERE e.name='Canchas Sintéticas La Nariño'
  AND NOT EXISTS (SELECT 1 FROM resources r WHERE r.establishment_id=e.id AND r.name='Cancha 5v5 - B');

INSERT INTO resources(establishment_id, name, kind, capacity, slot_minutes, price_per_slot, currency, is_active)
SELECT e.id, 'Cancha 8v8', 'cancha_8', 16, 60, 180000, 'COP', TRUE
FROM establishments e
WHERE e.name='Canchas Sintéticas La Nariño'
  AND NOT EXISTS (SELECT 1 FROM resources r WHERE r.establishment_id=e.id AND r.name='Cancha 8v8');

-- =========================================================
-- 5) Horarios L-D 08:00–23:30
-- =========================================================
DO $$
DECLARE d int; est_id int;
BEGIN
  SELECT id INTO est_id FROM establishments WHERE name='Canchas Sintéticas La Nariño' LIMIT 1;
  FOR d IN 0..6 LOOP
    IF NOT EXISTS (SELECT 1 FROM opening_hours WHERE establishment_id=est_id AND weekday=d) THEN
      INSERT INTO opening_hours(establishment_id, weekday, open_time, close_time)
      VALUES (est_id, d, '08:00', '23:30');
    END IF;
  END LOOP;
END$$;

-- =========================================================
-- 6) Regla precio pico 18:00–22:00 (+10k)
-- =========================================================
INSERT INTO pricing_rules (establishment_id, resource_id, weekday, start_time, end_time, price_per_slot, priority)
SELECT e.id, NULL, NULL, '18:00', '22:00', 10000, 10
FROM establishments e
WHERE e.name='Canchas Sintéticas La Nariño'
  AND NOT EXISTS (
    SELECT 1 FROM pricing_rules pr
    WHERE pr.establishment_id=e.id AND pr.resource_id IS NULL
      AND pr.weekday IS NULL AND pr.start_time='18:00'::time
      AND pr.end_time='22:00'::time AND pr.price_per_slot=10000 AND pr.priority=10
  );

-- =========================================================
-- 7) Categorías y productos
-- =========================================================
INSERT INTO product_categories (name, is_active)
SELECT 'Bebidas', TRUE WHERE NOT EXISTS (SELECT 1 FROM product_categories WHERE name='Bebidas');

INSERT INTO product_categories (name, is_active)
SELECT 'Snacks', TRUE WHERE NOT EXISTS (SELECT 1 FROM product_categories WHERE name='Snacks');

INSERT INTO products (establishment_id, category_id, name, price, tax_rate, is_active)
SELECT e.id, c.id, 'Agua 600ml', 3000, 0.00, TRUE
FROM establishments e, product_categories c
WHERE e.name='Canchas Sintéticas La Nariño' AND c.name='Bebidas'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.establishment_id=e.id AND p.name='Agua 600ml');

INSERT INTO products (establishment_id, category_id, name, price, tax_rate, is_active)
SELECT e.id, c.id, 'Gaseosa 400ml', 4500, 0.00, TRUE
FROM establishments e, product_categories c
WHERE e.name='Canchas Sintéticas La Nariño' AND c.name='Bebidas'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.establishment_id=e.id AND p.name='Gaseosa 400ml');

INSERT INTO products (establishment_id, category_id, name, price, tax_rate, is_active)
SELECT e.id, c.id, 'Gatorade 500ml', 6000, 0.00, TRUE
FROM establishments e, product_categories c
WHERE e.name='Canchas Sintéticas La Nariño' AND c.name='Bebidas'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.establishment_id=e.id AND p.name='Gatorade 500ml');

INSERT INTO products (establishment_id, category_id, name, price, tax_rate, is_active)
SELECT e.id, c.id, 'Papas de limón 25g', 3000, 0.00, TRUE
FROM establishments e, product_categories c
WHERE e.name='Canchas Sintéticas La Nariño' AND c.name='Snacks'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.establishment_id=e.id AND p.name='Papas de limón 25g');

INSERT INTO products (establishment_id, category_id, name, price, tax_rate, is_active)
SELECT e.id, c.id, 'Chocoramo', 3500, 0.00, TRUE
FROM establishments e, product_categories c
WHERE e.name='Canchas Sintéticas La Nariño' AND c.name='Snacks'
  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.establishment_id=e.id AND p.name='Chocoramo');

-- =========================================================
-- 7.1) Índice único para inventory_stock (soporte ON CONFLICT en trigger)
-- =========================================================
CREATE UNIQUE INDEX IF NOT EXISTS uq_inventory_stock_product_id
  ON inventory_stock(product_id);

-- =========================================================
-- 8) Inventario inicial (solo created_at con NOW()) idempotente
-- =========================================================
INSERT INTO inventory_tx (product_id, qty, tx_type, reason, created_at)
SELECT p.id, 48, 'IN', 'Carga inicial', NOW()
FROM products p
JOIN establishments e ON e.id = p.establishment_id
WHERE e.name = 'Canchas Sintéticas La Nariño' AND p.name = 'Agua 600ml'
  AND NOT EXISTS (SELECT 1 FROM inventory_stock s WHERE s.product_id = p.id);

INSERT INTO inventory_tx (product_id, qty, tx_type, reason, created_at)
SELECT p.id, 36, 'IN', 'Carga inicial', NOW()
FROM products p
JOIN establishments e ON e.id = p.establishment_id
WHERE e.name = 'Canchas Sintéticas La Nariño' AND p.name = 'Gaseosa 400ml'
  AND NOT EXISTS (SELECT 1 FROM inventory_stock s WHERE s.product_id = p.id);

INSERT INTO inventory_tx (product_id, qty, tx_type, reason, created_at)
SELECT p.id, 24, 'IN', 'Carga inicial', NOW()
FROM products p
JOIN establishments e ON e.id = p.establishment_id
WHERE e.name = 'Canchas Sintéticas La Nariño' AND p.name = 'Gatorade 500ml'
  AND NOT EXISTS (SELECT 1 FROM inventory_stock s WHERE s.product_id = p.id);

INSERT INTO inventory_tx (product_id, qty, tx_type, reason, created_at)
SELECT p.id, 40, 'IN', 'Carga inicial', NOW()
FROM products p
JOIN establishments e ON e.id = p.establishment_id
WHERE e.name = 'Canchas Sintéticas La Nariño' AND p.name = 'Papas de limón 25g'
  AND NOT EXISTS (SELECT 1 FROM inventory_stock s WHERE s.product_id = p.id);

INSERT INTO inventory_tx (product_id, qty, tx_type, reason, created_at)
SELECT p.id, 30, 'IN', 'Carga inicial', NOW()
FROM products p
JOIN establishments e ON e.id = p.establishment_id
WHERE e.name = 'Canchas Sintéticas La Nariño' AND p.name = 'Chocoramo'
  AND NOT EXISTS (SELECT 1 FROM inventory_stock s WHERE s.product_id = p.id);

-- =========================================================
-- 9) Asignar staff a establecimiento
-- =========================================================
INSERT INTO establishment_staff(establishment_id, user_id)
SELECT e.id, u.id
FROM establishments e, users u
WHERE e.name='Canchas Sintéticas La Nariño'
  AND u.email IN ('cajero1@lanarino.local','cajero2@lanarino.local')
  AND NOT EXISTS (
    SELECT 1 FROM establishment_staff es
    WHERE es.establishment_id=e.id AND es.user_id=u.id
  );

"""
    )


def downgrade() -> None:
    """
    Downgrade: limpiamos los datos seed específicos de 'Canchas Sintéticas La Nariño'
    ADVERTENCIA: esto borra datos insertados por esta migración.
    """
    op.execute(
        """
-- Borrado idempotente de datos relacionados al seed de 'Canchas Sintéticas La Nariño'
DO $$
DECLARE est_id INT;
BEGIN
  SELECT id INTO est_id FROM establishments WHERE name='Canchas Sintéticas La Nariño' LIMIT 1;

  IF est_id IS NOT NULL THEN
    -- Elimina asignaciones de staff
    DELETE FROM establishment_staff
    WHERE establishment_id = est_id;

    -- Elimina inventario relacionado a productos del establecimiento
    DELETE FROM inventory_tx
    WHERE product_id IN (
      SELECT id FROM products WHERE establishment_id = est_id
    );

    DELETE FROM inventory_stock
    WHERE product_id IN (
      SELECT id FROM products WHERE establishment_id = est_id
    );

    -- Elimina productos y categorías si no tienen más productos
    DELETE FROM products
    WHERE establishment_id = est_id;

    DELETE FROM product_categories c
    WHERE NOT EXISTS (SELECT 1 FROM products p WHERE p.category_id = c.id);

    -- Elimina reglas de precio, horarios y recursos
    DELETE FROM pricing_rules WHERE establishment_id = est_id;
    DELETE FROM opening_hours WHERE establishment_id = est_id;
    DELETE FROM resources WHERE establishment_id = est_id;

    -- Desasigna owner y elimina establecimiento
    UPDATE establishments SET owner_user_id = NULL WHERE id = est_id;
    DELETE FROM establishments WHERE id = est_id;
  END IF;

  -- Elimina usuarios del seed si no están relacionados a otros
  DELETE FROM users WHERE email IN (
    'owner@lanariño.local',
    'cajero1@lanariño.local',
    'cajero2@lanariño.local',
    'admin@lanariño.local',
    'cliente1@lanariño.local',
    'cliente2@lanariño.local',
    'cliente3@lanariño.local',
    'cliente4@lanariño.local',
    'cliente5@lanariño.local'
  );
END$$;

-- No eliminamos el índice único, no hace daño y podría ser requerido por el trigger:
-- DROP INDEX IF EXISTS uq_inventory_stock_product_id;
"""
    )
