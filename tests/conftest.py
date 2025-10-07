import pytest
from sqlalchemy import text

from app.db import engine


@pytest.fixture(autouse=True, scope="session")
def ensure_db_extensions():
    # Ensure btree_gist exists for migration tests
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS btree_gist;"))
        conn.commit()


@pytest.fixture(scope="function")
def db_clean():
    # Optionally, could truncate or run migrations; leave to test to manage
    yield
