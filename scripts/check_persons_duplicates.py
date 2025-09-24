import os
from sqlalchemy import create_engine, text

url = os.environ.get("DATABASE_URL")
if not url:
    raise SystemExit("DATABASE_URL not set")

engine = create_engine(url)
with engine.connect() as conn:
    res = conn.execute(text("SELECT email, count(*) FROM persons GROUP BY email HAVING count(*)>1"))
    rows = res.fetchall()
    if not rows:
        print("No duplicate emails found in persons")
    else:
        print("Duplicate emails:")
        for r in rows:
            print(r)
