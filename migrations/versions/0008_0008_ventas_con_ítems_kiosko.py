from alembic import op

revision = '0008'
down_revision = '0007'
branch_labels = None
depends_on = None

def upgrade():
    op.execute("""
    DO $$
    DECLARE est_id INT; res_id INT; cajero INT; sale_id INT;
            agua INT; gaseosa INT; papas INT; gatorade INT; choco INT;
    BEGIN
      SELECT id INTO est_id FROM establishments WHERE name='Canchas Sintéticas La Nariño';
      SELECT id INTO cajero FROM users WHERE email='cajero1@lanarino.local';
      SELECT id INTO res_id FROM reservations 
      WHERE status='CONFIRMED'
      ORDER BY id ASC LIMIT 1;

      SELECT id INTO agua FROM products WHERE establishment_id=est_id AND name='Agua 600ml';
      SELECT id INTO gaseosa FROM products WHERE establishment_id=est_id AND name='Gaseosa 400ml';
      SELECT id INTO papas FROM products WHERE establishment_id=est_id AND name='Papas de limón 25g';
      SELECT id INTO gatorade FROM products WHERE establishment_id=est_id AND name='Gatorade 500ml';
      SELECT id INTO choco FROM products WHERE establishment_id=est_id AND name='Chocoramo';

      -- Venta asociada a esa reserva
      IF NOT EXISTS (SELECT 1 FROM sales s WHERE s.reservation_id = res_id) THEN
  INSERT INTO sales (establishment_id, cashier_user_id, reservation_id, payment_method, subtotal, tax_total, grand_total, status, created_at)
  VALUES (est_id, cajero, res_id, 'EFECTIVO', 0, 0, 0, 'OK', NOW()) RETURNING id INTO sale_id;

        INSERT INTO sale_items (sale_id, product_id, qty, unit_price, tax_rate, line_total)
        SELECT sale_id, agua, 3, p.price, p.tax_rate, 3*p.price FROM products p WHERE p.id=agua;
        INSERT INTO sale_items (sale_id, product_id, qty, unit_price, tax_rate, line_total)
        SELECT sale_id, papas, 2, p.price, p.tax_rate, 2*p.price FROM products p WHERE p.id=papas;
        INSERT INTO sale_items (sale_id, product_id, qty, unit_price, tax_rate, line_total)
        SELECT sale_id, gaseosa, 2, p.price, p.tax_rate, 2*p.price FROM products p WHERE p.id=gaseosa;

        UPDATE sales
        SET subtotal = (SELECT COALESCE(SUM(line_total),0) FROM sale_items WHERE sale_items.sale_id=sales.id),
            tax_total=0,
            grand_total = (SELECT COALESCE(SUM(line_total),0) FROM sale_items WHERE sale_items.sale_id=sales.id)
        WHERE sales.id = sale_id;
      END IF;

      -- Venta libre (sin reserva)
      sale_id := NULL;
  INSERT INTO sales (establishment_id, cashier_user_id, reservation_id, payment_method, subtotal, tax_total, grand_total, status, created_at)
  VALUES (est_id, cajero, NULL, 'TRANSFERENCIA', 0, 0, 0, 'OK', NOW()) RETURNING id INTO sale_id;

      INSERT INTO sale_items (sale_id, product_id, qty, unit_price, tax_rate, line_total)
      SELECT sale_id, gatorade, 2, p.price, p.tax_rate, 2*p.price FROM products p WHERE p.id=gatorade;
      INSERT INTO sale_items (sale_id, product_id, qty, unit_price, tax_rate, line_total)
      SELECT sale_id, choco, 1, p.price, p.tax_rate, 1*p.price FROM products p WHERE p.id=choco;

      UPDATE sales
      SET subtotal = (SELECT COALESCE(SUM(line_total),0) FROM sale_items WHERE sale_items.sale_id=sales.id),
          tax_total=0,
          grand_total = (SELECT COALESCE(SUM(line_total),0) FROM sale_items WHERE sale_items.sale_id=sales.id)
      WHERE sales.id = sale_id;
    END$$;
    """)
