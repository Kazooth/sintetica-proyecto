from alembic import op

revision = '0007'
down_revision = '0006'
branch_labels = None
depends_on = None

def upgrade():
    op.execute("""
    DO $$
    DECLARE est_id INT; r5a INT; r5b INT; r8 INT;
            u1 INT; u2 INT; u3 INT; u4 INT; u5 INT;
            start_ts timestamptz; end_ts timestamptz;
    BEGIN
      SELECT id INTO est_id FROM establishments WHERE name='Canchas Sintéticas La Nariño';
      SELECT id INTO r5a FROM resources WHERE establishment_id=est_id AND name='Cancha 5v5 - A';
      SELECT id INTO r5b FROM resources WHERE establishment_id=est_id AND name='Cancha 5v5 - B';
      SELECT id INTO r8  FROM resources WHERE establishment_id=est_id AND name='Cancha 8v8';

      SELECT id INTO u1 FROM users WHERE email='cliente1@lanarino.local';
      SELECT id INTO u2 FROM users WHERE email='cliente2@lanarino.local';
      SELECT id INTO u3 FROM users WHERE email='cliente3@lanarino.local';
      SELECT id INTO u4 FROM users WHERE email='cliente4@lanarino.local';
      SELECT id INTO u5 FROM users WHERE email='cliente5@lanarino.local';

      -- Reserva hoy +1 día 19:00–20:00 en 5v5 A (Camilo)
      start_ts := date_trunc('day', now() + interval '1 day') + interval '19 hours';
      end_ts   := start_ts + interval '1 hour';
      IF NOT EXISTS (SELECT 1 FROM reservations WHERE resource_id=r5a AND tstzrange(start_ts,end_ts,'[)') && time_range) THEN
        INSERT INTO reservations (resource_id, user_id, start_ts, end_ts, status, total_price, channel, notes)
        VALUES (r5a, u1, start_ts, end_ts, 'CONFIRMED', 80000, 'WEB', 'Liga amigos');
      END IF;

      -- Reserva hoy +2 días 20:00–21:00 en 5v5 B (Laura)
      start_ts := date_trunc('day', now() + interval '2 day') + interval '20 hours';
      end_ts   := start_ts + interval '1 hour';
      IF NOT EXISTS (SELECT 1 FROM reservations WHERE resource_id=r5b AND tstzrange(start_ts,end_ts,'[)') && time_range) THEN
        INSERT INTO reservations (resource_id, user_id, start_ts, end_ts, status, total_price, channel, notes)
        VALUES (r5b, u2, start_ts, end_ts, 'CONFIRMED', 80000, 'WEB', 'Equipo barrio');
      END IF;

      -- Reserva hoy +3 días 18:00–19:00 en 8v8 (Julián)
      start_ts := date_trunc('day', now() + interval '3 day') + interval '18 hours';
      end_ts   := start_ts + interval '1 hour';
      IF NOT EXISTS (SELECT 1 FROM reservations WHERE resource_id=r8 AND tstzrange(start_ts,end_ts,'[)') && time_range) THEN
        INSERT INTO reservations (resource_id, user_id, start_ts, end_ts, status, total_price, channel, notes)
        VALUES (r8, u3, start_ts, end_ts, 'CONFIRMED', 180000, 'PHONE', 'Partido universidad');
      END IF;
    END$$;
    """)
