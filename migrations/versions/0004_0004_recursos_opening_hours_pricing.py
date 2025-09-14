from alembic import op

revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None

def upgrade():
    op.execute("""
    -- Recursos
    INSERT INTO resources (establishment_id, name, kind, capacity, slot_minutes, price_per_slot, currency, is_active)
    SELECT e.id, 'Cancha 5v5 - A', 'cancha_5', 10, 60, 80000, 'COP', TRUE
    FROM establishments e WHERE e.name='Canchas Sintéticas La Nariño'
    ON CONFLICT (establishment_id, name) DO NOTHING;

    INSERT INTO resources (establishment_id, name, kind, capacity, slot_minutes, price_per_slot, currency, is_active)
    SELECT e.id, 'Cancha 5v5 - B', 'cancha_5', 10, 60, 80000, 'COP', TRUE
    FROM establishments e WHERE e.name='Canchas Sintéticas La Nariño'
    ON CONFLICT (establishment_id, name) DO NOTHING;

    INSERT INTO resources (establishment_id, name, kind, capacity, slot_minutes, price_per_slot, currency, is_active)
    SELECT e.id, 'Cancha 8v8', 'cancha_8', 16, 60, 180000, 'COP', TRUE
    FROM establishments e WHERE e.name='Canchas Sintéticas La Nariño'
    ON CONFLICT (establishment_id, name) DO NOTHING;

    -- Horarios 8:00–23:30 L-D
    DO $$
    DECLARE d int; est_id int;
    BEGIN
      SELECT id INTO est_id FROM establishments WHERE name='Canchas Sintéticas La Nariño' LIMIT 1;
      FOR d IN 0..6 LOOP
        INSERT INTO opening_hours(establishment_id, weekday, open_time, close_time)
        VALUES (est_id, d, '08:00', '23:30')
        ON CONFLICT (establishment_id, weekday) DO NOTHING;
      END LOOP;
    END$$;

    -- Regla pico para todas las canchas +10k de 18:00–22:00
    INSERT INTO pricing_rules (establishment_id, resource_id, weekday, start_time, end_time, price_per_slot, priority)
    SELECT e.id, NULL, NULL, '18:00', '22:00', 10000, 10
    FROM establishments e
    WHERE e.name='Canchas Sintéticas La Nariño'
      AND NOT EXISTS (
        SELECT 1 FROM pricing_rules pr
        WHERE pr.establishment_id = e.id
          AND pr.resource_id IS NULL
          AND pr.weekday IS NULL
          AND pr.start_time='18:00'::time AND pr.end_time='22:00'::time
          AND pr.price_per_slot = 10000 AND pr.priority = 10
      );
    """)
