## Resumen

Este PR fortalece la calidad, pruebas e infraestructura local del backend. Incluye tooling (Ruff, MyPy, pre-commit), migraciones para evitar solapes de reservas, pruebas de integración clave y un smoke end-to-end para validar el flujo principal (registro/login/reserva/listado) en Windows con Postgres vía Docker.

## Cambios principales

- Calidad/CI
  - Configuración de Ruff (lint + format) y MyPy (con plugin de SQLAlchemy).
  - Ajustes en `ruff.toml` para ignorar casos específicos en `admin/tests/scripts` y excluir `get-pip.py`.
  - README ampliado y script `scripts/run.ps1` para arranque local en Windows.
- Base de datos y migraciones
  - Constraint de exclusión parcial para impedir reservas solapadas por recurso cuando `status='CONFIRMED'`.
  - Migración de limpieza (“merge”) para linearizar el head de Alembic.
- Pruebas de integración
  - `tests/test_auth_register_login.py`: registro (201) y login (200).
  - `tests/test_reservation_create_happy.py`: flujo feliz de creación y listado.
  - `tests/test_reservation_overlap.py`: validación determinista de solape (201 → 409).
- Scripts y utilidades
  - `scripts/smoke.ps1` + `scripts/smoke.py`: ejecutan seed → register → login → reservar → listar, contra DB local.
  - `docker-compose.yml` con Postgres 15 y healthcheck.
- Otros
  - Migración a Pydantic v2 en `app/schemas.py` (uso de `ConfigDict(from_attributes=True)`).
  - `app/config.py` ajustado para lectura de `.env`/variables y compatibilidad con MyPy (`TYPE_CHECKING`).

## Cómo probar

1) Levantar DB (opcional, el smoke lo hace si es posible):

```powershell
docker compose up -d db
```

2) Ejecutar smoke end-to-end:

```powershell
./scripts/smoke.ps1 -DatabaseUrl "postgresql+psycopg://user:sintetica@localhost:5432/girardot"
```

Esperado: mensajes “[smoke] register OK”, “[smoke] login OK”, “reservation created …”, “list OK; reservation present” y “SUCCESS”.

3) Pruebas, lint y tipos:

```powershell
pytest -q
ruff check .
mypy --config-file mypy.ini app tests
```

## Notas

- El warning de `passlib/bcrypt` puede aparecer en algunos entornos; no afecta el flujo.
- La API de desarrollo usa host `127.0.0.1` por seguridad (comentado en `app/main.py`).

## Checklist

- [x] Lint PASS
- [x] Types PASS
- [x] Tests PASS
- [x] Smoke PASS
