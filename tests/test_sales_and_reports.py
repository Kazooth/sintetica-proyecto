from datetime import datetime, timedelta, UTC
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.db import SessionLocal
from app.models import Establishment, Product, ProductCategory, User
from app.security import create_access_token, hash_password

client = TestClient(app)


def make_headers(role: str = "ADMIN"):
    with SessionLocal() as s:
        u = User(email=f"{role.lower()}+{uuid4().hex[:6]}@example.com", password_hash=hash_password("Pass123!"), person_id=1, role=role)
        s.add(u)
        s.commit()
        s.refresh(u)
        token = create_access_token({"sub": str(u.id)})
    return {"Authorization": f"Bearer {token}"}


def seed_product(establishment_id: int | None = None) -> tuple[int, int]:
    with SessionLocal() as s:
        if establishment_id is None:
            est = Establishment(name=f"E{uuid4().hex[:4]}", city_id=1)
            s.add(est)
            s.flush()
            establishment_id = est.id
        cat = ProductCategory(name=f"C{uuid4().hex[:4]}")
        s.add(cat)
        s.flush()
        p = Product(establishment_id=establishment_id, category_id=cat.id, name=f"P{uuid4().hex[:4]}", price=100, tax_rate=0.19, is_active=True)
        s.add(p)
        s.commit()
        return establishment_id, p.id


def test_create_sale_happy_and_report_summary():
    est_id, prod_id = seed_product()
    headers = make_headers("ADMIN")

    payload = {
        "establishment_id": est_id,
        "payment_method": "CASH",
        "reservation_id": None,
        "items": [{"product_id": prod_id, "qty": 2}],
    }
    r = client.post("/sales", json=payload, headers=headers)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["grand_total"] > 0
    assert len(body["items"]) == 1

    # report in a range that captures NOW()
    now = datetime.now(UTC)
    r2 = client.get(
        f"/reports/sales/summary?date_from={(now - timedelta(days=1)).isoformat()}&date_to={(now + timedelta(days=1)).isoformat()}",
        headers=headers,
    )
    assert r2.status_code == 200, r2.text
    rows = r2.json()
    assert isinstance(rows, list)
    assert any(row.get("count", 0) >= 1 for row in rows)


def test_create_sale_cross_establishment_rejected():
    # product in est1, sale targets est2 -> 400
    est1, prod_id = seed_product()
    est2, _ = seed_product()
    headers = make_headers("ADMIN")

    payload = {
        "establishment_id": est2,
        "payment_method": "CASH",
        "reservation_id": None,
        "items": [{"product_id": prod_id, "qty": 1}],
    }
    r = client.post("/sales", json=payload, headers=headers)
    assert r.status_code == 400, r.text
