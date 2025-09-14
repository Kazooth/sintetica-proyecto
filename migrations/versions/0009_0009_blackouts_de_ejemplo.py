from alembic import op

revision = '0009'
down_revision = '0008'
branch_labels = None
depends_on = None

def upgrade():
    op.execute("""
    DO $$
    DECLARE est_id INT; r5a INT; r8 INT;
    BEGIN
      SELECT id INTO est_id FROM establishments WHERE name='Canchas Sintéticas La Nariño';
      SELECT id INTO r5a FROM resources WHERE establishment_id=est_id AND name='Cancha 5v5 - A';
      SELECT id INTO r8  FROM resources WHERE establishment_id=est_id AND name='Cancha 8v8';

      -- Blackout general por mantenimiento mañana 14:00–16:00
      IF NOT EXISTS (
        SELECT 1 FROM blackouts b WHERE b.establishment_id=est_id
        AND b.reason='Mantenimiento general'
      ) THEN
        INSERT INTO blackouts (establishment_id, start_ts, end_ts, reason)
        VALUES (est_id, date_trunc('day', now() + interval '1 day') + interval '14 hour',
                      date_trunc('day', now() + interval '1 day') + interval '16 hour',
                      'Mantenimiento general');
      END IF;

      -- Blackout solo para 8v8 por evento 17:00–19:00 mismo día
      IF NOT EXISTS (
        SELECT 1 FROM blackouts b WHERE b.resource_id=r8
        AND b.reason='Evento interno'
      ) THEN
        INSERT INTO blackouts (establishment_id, resource_id, start_ts, end_ts, reason)
        VALUES (est_id, r8,
                date_trunc('day', now() + interval '1 day') + interval '17 hour',
                date_trunc('day', now() + interval '1 day') + interval '19 hour',
                'Evento interno');
      END IF;
    END$$;
    """)
