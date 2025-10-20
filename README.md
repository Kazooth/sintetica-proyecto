# Sintética API

Backend en FastAPI + SQLAlchemy + Alembic + PostgreSQL. Este repo incluye tooling de calidad (Ruff, MyPy, pre-commit) y CI en GitHub Actions.

## Requisitos

- Python 3.11+
- PostgreSQL 15 (local o Docker)
- Opcional: virtualenv (recomendado)

## Variables de entorno

Config en `app/config.py` vía Pydantic Settings. Usa un archivo `.env` en la raíz o variables del entorno del sistema.

Clona `./.env.example` a `./.env` y ajusta los valores:

```
DATABASE_URL=postgresql+psycopg://user:sintetica@localhost:5432/girardot
CORS_ORIGINS=http://localhost:5173
SECRET_KEY=please_change_me
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

En PowerShell (Windows) puedes exportar temporalmente:

```powershell
$env:DATABASE_URL = "postgresql+psycopg://user:sintetica@localhost:5432/girardot"
$env:CORS_ORIGINS = "http://localhost:5173"
$env:SECRET_KEY = "please_change_me"
$env:ACCESS_TOKEN_EXPIRE_MINUTES = "60"
```

## Instalación (dev)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -r requirements.txt -c constraints.txt
pip install -r requirements-dev.txt -c constraints.txt
pre-commit install
```

## Base de datos y migraciones

- Revisa `alembic.ini` y `migrations/` para ver el historial completo.
- Para aplicar todas las migraciones:

```powershell
.\.venv\Scripts\Activate.ps1
python -m alembic upgrade head
```

- Para crear una nueva migración (después de editar modelos):

```powershell
python -m alembic revision -m "<tu mensaje>" --autogenerate
```

## Ejecutar la API

```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Atajo (Windows):

```powershell
./scripts/run.ps1
```

## Usar Docker Compose (solo DB)

Levanta PostgreSQL 15 localmente en 5432:

```powershell
docker compose up -d db
$env:DATABASE_URL = "postgresql+psycopg://user:sintetica@localhost:5432/girardot"
python -m alembic upgrade head
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

- Salud: GET `http://127.0.0.1:8000/health`
- Panel admin: registrado vía `sqladmin` en `app/admin.py` cuando la app arranca

Nota: En `app/main.py` fijamos `--host 127.0.0.1` para desarrollo local seguro (regla Ruff S104).

## Pruebas, Lint, Types

- Lint (Ruff) y formato:

```powershell
ruff check .
ruff format .
```

- Type-check (MyPy):

```powershell
mypy --config-file mypy.ini app tests
```

- Pruebas:

```powershell
pytest -q
```

MyPy está configurado con el plugin de SQLAlchemy; los módulos externos sin stubs (por ejemplo `jose`, `passlib`) se silencian en `app/security.py` con comentarios `# type: ignore[import-untyped]`.

## CI (GitHub Actions)

Workflow en `.github/workflows/ci.yml`:

1. Instala dependencias con `constraints.txt` (incluye `requirements-dev.txt`).
2. Corre Ruff (lint y format-check).
3. Corre MyPy.
3.5 Corre `pre-commit run --all-files` para alinear con hooks locales.
4. Levanta PostgreSQL 15 como servicio.
5. Espera a que el DB esté listo y exporta `DATABASE_URL`.
6. Corre migraciones Alembic `upgrade head`.
7. Ejecuta `pytest`.

## Convenciones de desarrollo

- Estilo: controlado por `ruff.toml` y `.editorconfig` (longitud 100, comillas dobles, etc.).
- Tipos: `mypy.ini` habilita `check_untyped_defs` y el plugin de SQLAlchemy; excluye `migrations/`.
- Pre-commit: hooks para Ruff, MyPy y checks básicos (`.pre-commit-config.yaml`).
- Branching: trabajar en `feature/*`, `chore/*`, `fix/*` y abrir PR hacia `main` (protegida). CI debe pasar antes de merge.

## Estructura relevante

- `app/` código de la API (routers, modelos, seguridad, admin, config).
- `migrations/` migraciones Alembic (historial versionado).
- `tests/` pruebas (cuando existan).
- `scripts/` utilidades locales (si aplican).

## Notas sobre decisiones y documentación añadida

- Comentarios explicativos:
  - `app/main.py`: comentario para justificar `host=127.0.0.1` (seguridad en dev y cumplimiento de Ruff S104).
  - `app/admin.py`: comentarios y anotaciones `ClassVar[...]` para dejar claro el contrato con `sqladmin` y evitar falsos positivos de MyPy; comentario sobre por qué se usan nombres de columna como strings en `UserAdmin`.
  - `app/security.py`: se documenta el motivo de `type: ignore` en imports no tipados; constantes `ALGORITHM`/`SECRET_KEY` y expiración provienen de `settings`.
- Tooling de documentación:
  - `ruff.toml`: incluye lista de reglas activas/ignoradas y justifica algunas excepciones (p. ej., `B008`, `E501`, `RUF00x` por contenido en español).
  - `mypy.ini`: explica exclusiones (`migrations/`), plugin de SQLAlchemy y excepciones por paquete.
  - `.editorconfig`: normaliza saltos de línea/indentación y límites por tipo de archivo.
  - `.pre-commit-config.yaml`: estandariza que todo commit pase por lint/format/types.
- `.env.example` agregado para documentar claramente las variables esperadas por `Settings`.

## Siguientes pasos sugeridos

- Añadir más pruebas de integración (registro/login, reservas, ventas).
- Documentar endpoints con ejemplos en README o usar `OpenAPI` generado por FastAPI (`/docs`).
- Añadir seeds/fixtures reproducibles como comandos o scripts.

---


