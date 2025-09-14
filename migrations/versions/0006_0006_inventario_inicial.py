from alembic import op

revision = '0006'
down_revision = '0005'
branch_labels = None
depends_on = None

def upgrade():
    op.execute("""
    -- Carga inicial si no existe stock
    INSERT INTO inventory_tx (product_id, qty, tx_type, reason)
    SELECT p.id, 48, 'IN', 'Carga inicial'
    FROM products p
    JOIN establishments e ON e.id = p.establishment_id
    WHERE e.name='Canchas Sintéticas La Nariño' AND p.name='Agua 600ml'
      AND NOT EXISTS (SELECT 1 FROM inventory_stock s WHERE s.product_id=p.id);

    INSERT INTO inventory_tx (product_id, qty, tx_type, reason)
    SELECT p.id, 36, 'IN', 'Carga inicial'
    FROM products p
    JOIN establishments e ON e.id = p.establishment_id
    WHERE e.name='Canchas Sintéticas La Nariño' AND p.name='Gaseosa 400ml'
      AND NOT EXISTS (SELECT 1 FROM inventory_stock s WHERE s.product_id=p.id);

    INSERT INTO inventory_tx (product_id, qty, tx_type, reason)
    SELECT p.id, 24, 'IN', 'Carga inicial'
    FROM products p
    JOIN establishments e ON e.id = p.establishment_id
    WHERE e.name='Canchas Sintéticas La Nariño' AND p.name='Gatorade 500ml'
      AND NOT EXISTS (SELECT 1 FROM inventory_stock s WHERE s.product_id=p.id);

    INSERT INTO inventory_tx (product_id, qty, tx_type, reason)
    SELECT p.id, 40, 'IN', 'Carga inicial'
    FROM products p
    JOIN establishments e ON e.id = p.establishment_id
    WHERE e.name='Canchas Sintéticas La Nariño' AND p.name='Papas de limón 25g'
      AND NOT EXISTS (SELECT 1 FROM inventory_stock s WHERE s.product_id=p.id);

    INSERT INTO inventory_tx (product_id, qty, tx_type, reason)
    SELECT p.id, 30, 'IN', 'Carga inicial'
    FROM products p
    JOIN establishments e ON e.id = p.establishment_id
    WHERE e.name='Canchas Sintéticas La Nariño' AND p.name='Chocoramo'
      AND NOT EXISTS (SELECT 1 FROM inventory_stock s WHERE s.product_id=p.id);
    """)
