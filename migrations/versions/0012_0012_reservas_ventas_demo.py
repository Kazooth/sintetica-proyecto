"""0012 reservas + ventas demo

Revision ID: 0012
Revises: 0011
Create Date: 2025-09-09 15:13:56.510095

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "0012"
down_revision = "0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
-- =========================================================
-- 0012: RESERVAS + VENTAS DEMO (idempotente)
--  - Preámbulo: asegurar defaults de columnas NOT NULL
--  - Reservas de clientes y ventas ligadas a reservation_id
--  - Ítems de venta generan movimientos de inventario por trigger
-- =========================================================

-- 0) Asegurar defaults a nivel servidor (idempotente)
DO $$
BEGIN
  -- inventory_tx.created_at -> default NOW()
  BEGIN
    ALTER TABLE inventory_tx ALTER COLUMN created_at SET DEFAULT NOW();
  EXCEPTION WHEN OTHERS THEN
    -- Si ya está, o columna no existe, ignorar
    NULL;
  END;

  -- sales.created_at -> default NOW()
  BEGIN
    ALTER TABLE sales ALTER COLUMN created_at SET DEFAULT NOW();
  EXCEPTION WHEN OTHERS THEN
    NULL;
  END;

  -- sales.status -> default 'OK'
  BEGIN
    ALTER TABLE sales ALTER COLUMN status SET DEFAULT 'OK';
  EXCEPTION WHEN OTHERS THEN
    NULL;
  END;
END$$;

-- =========================================================
--  - Reservas + Ventas Demo (idempotente)
-- =========================================================
DO $$
DECLARE
  est_id INT;
  -- Usuarios
  u1 INT; u2 INT; u3 INT;
  caj1 INT; caj2 INT;

  -- Recursos
  r5a INT; r5b INT; r8 INT;

  -- Reservas
  res1 INT; res2 INT; res3 INT;

  -- Productos y precios/impuestos
  p_agua INT;     pr_agua INT;     tx_agua NUMERIC(4,2);
  p_papas INT;    pr_papas INT;    tx_papas NUMERIC(4,2);
  p_gaseosa INT;  pr_gaseosa INT;  tx_gaseosa NUMERIC(4,2);
  p_choco INT;    pr_choco INT;    tx_choco NUMERIC(4,2);
  p_gatorade INT; pr_gatorade INT; tx_gatorade NUMERIC(4,2);

  -- Ventas
  sale1 INT; sale2 INT; sale3 INT;

  -- Totales auxiliares
  s_subtotal INT; s_tax INT; s_total INT;
BEGIN
  -- Establecimiento
  SELECT id INTO est_id FROM establishments
   WHERE name='Canchas Sintéticas La Nariño'
   LIMIT 1;

  -- Usuarios clientes
  SELECT id INTO u1 FROM users WHERE email='cliente1@lanarino.local' LIMIT 1;
  SELECT id INTO u2 FROM users WHERE email='cliente2@lanarino.local' LIMIT 1;
  SELECT id INTO u3 FROM users WHERE email='cliente3@lanarino.local' LIMIT 1;

  -- Cajeros (staff)
  SELECT id INTO caj1 FROM users WHERE email='cajero1@lanarino.local' LIMIT 1;
  SELECT id INTO caj2 FROM users WHERE email='cajero2@lanarino.local' LIMIT 1;

  -- Recursos (canchas)
  SELECT id INTO r5a FROM resources WHERE name='Cancha 5v5 - A' LIMIT 1;
  SELECT id INTO r5b FROM resources WHERE name='Cancha 5v5 - B' LIMIT 1;
  SELECT id INTO r8  FROM resources WHERE name='Cancha 8v8'     LIMIT 1;

  -- Productos y sus precios / impuestos
  SELECT id, price, tax_rate INTO p_agua, pr_agua, tx_agua
    FROM products WHERE name='Agua 600ml' LIMIT 1;

  SELECT id, price, tax_rate INTO p_papas, pr_papas, tx_papas
    FROM products WHERE name='Papas de limón 25g' LIMIT 1;

  SELECT id, price, tax_rate INTO p_gaseosa, pr_gaseosa, tx_gaseosa
    FROM products WHERE name='Gaseosa 400ml' LIMIT 1;

  SELECT id, price, tax_rate INTO p_choco, pr_choco, tx_choco
    FROM products WHERE name='Chocoramo' LIMIT 1;

  SELECT id, price, tax_rate INTO p_gatorade, pr_gatorade, tx_gatorade
    FROM products WHERE name='Gatorade 500ml' LIMIT 1;

  --------------------------------------------------------------------
  -- RESERVA #1: Cliente1 en Cancha 5v5 - A, 2025-09-14 19:00-20:00
  --------------------------------------------------------------------
  IF NOT EXISTS (
    SELECT 1 FROM reservations
     WHERE resource_id = r5a
       AND user_id     = u1
       AND start_ts    = '2025-09-14 19:00'::timestamptz
  ) THEN
    INSERT INTO reservations (resource_id, user_id, start_ts, end_ts, status, total_price, channel, notes)
    VALUES (r5a, u1, '2025-09-14 19:00', '2025-09-14 20:00', 'CONFIRMED', 80000, 'WEB', 'Reserva demo r5a c1')
    RETURNING id INTO res1;
  ELSE
    SELECT id INTO res1 FROM reservations
     WHERE resource_id = r5a AND user_id = u1
       AND start_ts='2025-09-14 19:00'::timestamptz
     ORDER BY id LIMIT 1;
  END IF;

  -- VENTA #1: 2x Agua + 1x Papas (ligada a res1)
  IF NOT EXISTS (SELECT 1 FROM sales WHERE reservation_id = res1) THEN
    s_subtotal := pr_agua*2 + pr_papas*1;
    s_tax := COALESCE(ROUND(pr_agua*2*tx_agua), 0)
          + COALESCE(ROUND(pr_papas*1*tx_papas), 0);
    s_total := s_subtotal + s_tax;

    INSERT INTO sales (
      establishment_id, cashier_user_id, reservation_id, payment_method,
      subtotal, tax_total, grand_total, status, created_at
    )
    VALUES (est_id, caj1, res1, 'EFECTIVO', s_subtotal, s_tax, s_total, 'OK', NOW())
    RETURNING id INTO sale1;

    INSERT INTO sale_items (sale_id, product_id, qty, unit_price, tax_rate, line_total)
    VALUES (sale1, p_agua, 2, pr_agua, tx_agua, pr_agua*2 + COALESCE(ROUND(pr_agua*2*tx_agua),0));

    INSERT INTO sale_items (sale_id, product_id, qty, unit_price, tax_rate, line_total)
    VALUES (sale1, p_papas, 1, pr_papas, tx_papas, pr_papas*1 + COALESCE(ROUND(pr_papas*1*tx_papas),0));
  END IF;

  --------------------------------------------------------------------
  -- RESERVA #2: Cliente2 en Cancha 5v5 - B, 2025-09-14 20:00-21:00
  --------------------------------------------------------------------
  IF NOT EXISTS (
    SELECT 1 FROM reservations
     WHERE resource_id = r5b
       AND user_id     = u2
       AND start_ts    = '2025-09-14 20:00'::timestamptz
  ) THEN
    INSERT INTO reservations (resource_id, user_id, start_ts, end_ts, status, total_price, channel, notes)
    VALUES (r5b, u2, '2025-09-14 20:00', '2025-09-14 21:00', 'CONFIRMED', 80000, 'WEB', 'Reserva demo r5b c2')
    RETURNING id INTO res2;
  ELSE
    SELECT id INTO res2 FROM reservations
     WHERE resource_id = r5b AND user_id = u2
       AND start_ts='2025-09-14 20:00'::timestamptz
     ORDER BY id LIMIT 1;
  END IF;

  -- VENTA #2: 1x Gaseosa + 1x Chocoramo (ligada a res2)
  IF NOT EXISTS (SELECT 1 FROM sales WHERE reservation_id = res2) THEN
    s_subtotal := pr_gaseosa*1 + pr_choco*1;
    s_tax := COALESCE(ROUND(pr_gaseosa*1*tx_gaseosa), 0)
          + COALESCE(ROUND(pr_choco*1*tx_choco), 0);
    s_total := s_subtotal + s_tax;

    INSERT INTO sales (
      establishment_id, cashier_user_id, reservation_id, payment_method,
      subtotal, tax_total, grand_total, status, created_at
    )
    VALUES (est_id, caj2, res2, 'TRANSFERENCIA', s_subtotal, s_tax, s_total, 'OK', NOW())
    RETURNING id INTO sale2;

    INSERT INTO sale_items (sale_id, product_id, qty, unit_price, tax_rate, line_total)
    VALUES (sale2, p_gaseosa, 1, pr_gaseosa, tx_gaseosa, pr_gaseosa*1 + COALESCE(ROUND(pr_gaseosa*1*tx_gaseosa),0));

    INSERT INTO sale_items (sale_id, product_id, qty, unit_price, tax_rate, line_total)
    VALUES (sale2, p_choco, 1, pr_choco, tx_choco, pr_choco*1 + COALESCE(ROUND(pr_choco*1*tx_choco),0));
  END IF;

  --------------------------------------------------------------------
  -- RESERVA #3: Cliente3 en Cancha 8v8, 2025-09-15 18:00-19:00
  --------------------------------------------------------------------
  IF NOT EXISTS (
    SELECT 1 FROM reservations
     WHERE resource_id = r8
       AND user_id     = u3
       AND start_ts    = '2025-09-15 18:00'::timestamptz
  ) THEN
    INSERT INTO reservations (resource_id, user_id, start_ts, end_ts, status, total_price, channel, notes)
    VALUES (r8, u3, '2025-09-15 18:00', '2025-09-15 19:00', 'CONFIRMED', 180000, 'WEB', 'Reserva demo r8 c3')
    RETURNING id INTO res3;
  ELSE
    SELECT id INTO res3 FROM reservations
     WHERE resource_id = r8 AND user_id = u3
       AND start_ts='2025-09-15 18:00'::timestamptz
     ORDER BY id LIMIT 1;
  END IF;

  -- VENTA #3: 3x Gatorade (ligada a res3)
  IF NOT EXISTS (SELECT 1 FROM sales WHERE reservation_id = res3) THEN
    s_subtotal := pr_gatorade*3;
    s_tax := COALESCE(ROUND(pr_gatorade*3*tx_gatorade), 0);
    s_total := s_subtotal + s_tax;

    INSERT INTO sales (
      establishment_id, cashier_user_id, reservation_id, payment_method,
      subtotal, tax_total, grand_total, status, created_at
    )
    VALUES (est_id, caj1, res3, 'EFECTIVO', s_subtotal, s_tax, s_total, 'OK', NOW())
    RETURNING id INTO sale3;

    INSERT INTO sale_items (sale_id, product_id, qty, unit_price, tax_rate, line_total)
    VALUES (sale3, p_gatorade, 3, pr_gatorade, tx_gatorade, pr_gatorade*3 + COALESCE(ROUND(pr_gatorade*3*tx_gatorade),0));
  END IF;

END$$;
        """
    )


def downgrade() -> None:
    op.execute(
        """
DO $$
DECLARE
  r_ids INT[];
BEGIN
  -- Obtiene IDs de reservas demo por 'notes'
  SELECT ARRAY(
    SELECT id FROM reservations
     WHERE notes IN ('Reserva demo r5a c1','Reserva demo r5b c2','Reserva demo r8 c3')
  ) INTO r_ids;

  -- Borra ítems y ventas ligadas a esas reservas
  DELETE FROM sale_items
   WHERE sale_id IN (SELECT id FROM sales WHERE reservation_id = ANY (r_ids));

  DELETE FROM sales
   WHERE reservation_id = ANY (r_ids);

  -- Borra reservas demo
  DELETE FROM reservations
   WHERE id = ANY (r_ids);
END$$;
        """
    )