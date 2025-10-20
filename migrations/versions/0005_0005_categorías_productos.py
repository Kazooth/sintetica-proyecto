from alembic import op

revision = '0005'
down_revision = '0004'
branch_labels = None
depends_on = None

def upgrade():
    op.execute("""
    INSERT INTO product_categories (name, is_active) VALUES ('Bebidas', TRUE)
    ON CONFLICT (name) DO NOTHING;

    INSERT INTO product_categories (name, is_active) VALUES ('Snacks', TRUE)
    ON CONFLICT (name) DO NOTHING;

    -- Productos para La Nariño
    INSERT INTO products (establishment_id, category_id, name, price, tax_rate, is_active)
    SELECT e.id, c.id, 'Agua 600ml', 3000, 0.00, TRUE
    FROM establishments e, product_categories c
    WHERE e.name='Canchas Sintéticas La Nariño' AND c.name='Bebidas'
    ON CONFLICT (establishment_id, name) DO NOTHING;

    INSERT INTO products (establishment_id, category_id, name, price, tax_rate, is_active)
    SELECT e.id, c.id, 'Gaseosa 400ml', 4500, 0.00, TRUE
    FROM establishments e, product_categories c
    WHERE e.name='Canchas Sintéticas La Nariño' AND c.name='Bebidas'
    ON CONFLICT (establishment_id, name) DO NOTHING;

    INSERT INTO products (establishment_id, category_id, name, price, tax_rate, is_active)
    SELECT e.id, c.id, 'Gatorade 500ml', 6000, 0.00, TRUE
    FROM establishments e, product_categories c
    WHERE e.name='Canchas Sintéticas La Nariño' AND c.name='Bebidas'
    ON CONFLICT (establishment_id, name) DO NOTHING;

    INSERT INTO products (establishment_id, category_id, name, price, tax_rate, is_active)
    SELECT e.id, c.id, 'Papas de limón 25g', 3000, 0.00, TRUE
    FROM establishments e, product_categories c
    WHERE e.name='Canchas Sintéticas La Nariño' AND c.name='Snacks'
    ON CONFLICT (establishment_id, name) DO NOTHING;

    INSERT INTO products (establishment_id, category_id, name, price, tax_rate, is_active)
    SELECT e.id, c.id, 'Chocoramo', 3500, 0.00, TRUE
    FROM establishments e, product_categories c
    WHERE e.name='Canchas Sintéticas La Nariño' AND c.name='Snacks'
    ON CONFLICT (establishment_id, name) DO NOTHING;
    """)
