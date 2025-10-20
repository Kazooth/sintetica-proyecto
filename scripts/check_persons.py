import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

url = os.environ.get("DATABASE_URL")
print("DATABASE_URL:", url)
if not url:
    raise SystemExit("DATABASE_URL not set in environment")

# create engine (SQLAlchemy should accept the URL format used in the app)
engine = create_engine(url)

try:
    with engine.connect() as conn:
        print("\nTables in public schema:")
        res = conn.execute(
            text("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname='public';")
        )
        tables = [r[0] for r in res.fetchall()]
        print(tables)

        print("\nCheck for persons table:")
        if "persons" in tables:
            cnt = conn.execute(text("SELECT COUNT(*) FROM persons")).scalar()
            print("persons count =", cnt)
            sample = conn.execute(
                text("SELECT id, first_name, last_name, email FROM persons ORDER BY id LIMIT 5")
            ).fetchall()
            print("sample persons:", sample)
        else:
            print("persons table NOT found")

        print("\nCheck users.person_id column and population:")
        # check columns in users
        cols = conn.execute(
            text(
                "SELECT column_name FROM information_schema.columns WHERE table_name='users' AND table_schema='public';"
            )
        ).fetchall()
        cols = [c[0] for c in cols]
        print("users columns:", cols)
        if "person_id" in cols:
            nulls = conn.execute(
                text("SELECT COUNT(*) FROM users WHERE person_id IS NULL")
            ).scalar()
            total = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
            print(f"users total={total}  person_id NULLs={nulls}")
            samples = conn.execute(
                text("SELECT id, email, person_id FROM users ORDER BY id LIMIT 10")
            ).fetchall()
            print("sample users:", samples)
        else:
            print("users.person_id column NOT found")

except SQLAlchemyError as e:
    print("SQLAlchemyError:", e)
    raise

print("\nDone")
