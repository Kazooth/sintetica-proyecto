# v0.1.0 – Backend endurecido, CI verde y reproducible

Fecha: 2025-10-20

## Cambios destacados

- Endurecimiento de autenticación y hashing
  - Pin de bcrypt a 3.2.2 para compatibilidad estable con passlib 1.7.4.
  - Contexto de Passlib con fallback a `bcrypt_sha256` para contraseñas >72 bytes.
  - Nuevas pruebas: `tests/test_security_hash.py`.
- Reglas de negocio críticas con TDD
  - Prevención de solapes de reservas con `tstzrange` + `EXCLUDE USING gist`.
  - Pruebas: `tests/test_reservation_overlap.py` y caso feliz `test_reservation_create_happy.py`.
- Migraciones robustas e idempotentes
  - Extensión `btree_gist` asegurada.
  - Eliminación de CTE transversal, creación condicional de índices/constraints, NO-OP para mantener historia lineal.
- CI más fiable y rápido (GitHub Actions)
  - PostgreSQL instalado en el runner (evita pulls frágiles).
  - Pipeline: ruff → ruff-format → pre-commit (mypy, EoF, whitespace) → mypy (app) → alembic → pytest.
  - `constraints.txt` integrado para instalaciones reproducibles.
- Pre-commit en local/CI
  - `.pre-commit-config.yaml` con ruff, ruff-format, mypy + deps necesarios.
  - Auto-fix de fin de archivo y espacios finales.
- Mejor DX y documentación
  - `README.md` actualizado con instalación usando `-c constraints.txt` y notas de pre-commit.
  - Scripts: `scripts/run.ps1` y `scripts/smoke.ps1`/`smoke.py`.
  - Cuerpo de PR en `docs/PR_BODY_chore-ci-lint-typecheck.md` y guía paso a paso.

## Requisitos/Versiones

- Python 3.11
- PostgreSQL 16
- Paquetes fijados en `requirements.txt` y `constraints.txt` (pines críticos: passlib 1.7.4, bcrypt 3.2.2, httpx 0.27.2)

## Pasos de actualización

1) Actualiza dependencias con constraints para entornos locales:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt -c constraints.txt
pip install -r requirements-dev.txt -c constraints.txt  # opcional para desarrollo
```

2) Variables de entorno (ver `.env.example`) y base de datos:

```powershell
$env:DATABASE_URL = "postgresql+psycopg://user:sintetica@localhost:5432/girardot"
```

3) Ejecuta migraciones y pruebas rápidas:

```powershell
alembic upgrade head
pytest -q
```

## Notas

- Si usas contraseñas largas, `bcrypt_sha256` evita el límite de 72 bytes.
- El admin basado en `sqladmin` se tipa de forma laxa para no bloquear el tipado del núcleo del dominio.
- La release se genera automáticamente al crear un tag `v*`.

---

Gracias por usar este backend. Si detectas incidencias, abre un issue o PR con una rama y CI en verde.
