# migrations/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# 👇 importa tu Base y settings
from app.models import Base
from app.config import settings

# Alembic Config, lee alembic.ini
config = context.config

# Logging de Alembic
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata de tus modelos para autogenerate
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Modo offline: genera SQL sin conectarse."""
    url = settings.DATABASE_URL  # carga desde tu .env a través de pydantic-settings
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Modo online: se conecta y ejecuta."""
    cfg_section = config.get_section(config.config_ini_section)
    # inyecta la URL de tu app (ignora la de alembic.ini si fuera distinta)
    cfg_section["sqlalchemy.url"] = settings.DATABASE_URL

    connectable = engine_from_config(
        cfg_section, prefix="sqlalchemy.", poolclass=pool.NullPool
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            render_as_batch=False,  # True solo si usas SQLite legacy
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
