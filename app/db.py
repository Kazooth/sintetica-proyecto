from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from .config import settings

# Crea el engine y el SessionLocal
engine = create_engine(settings.DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


# Dependencia para FastAPI (inyectar sesión por request)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Ping rápido a la base de datos (usado por /health)
def ping_db():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
