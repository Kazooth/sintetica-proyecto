from uuid import uuid4
from datetime import datetime, timedelta, time, UTC

from fastapi.testclient import TestClient

from app.main import app
from app.db import SessionLocal
from app.models import Establishment, Product, ProductCategory, Resource, OpeningHour, User
from app.security import hash_password

client = TestClient(app)


def create_user(email: str, role: str = "CUSTOMER") -> User:
    with SessionLocal() as s:
        u = User(email=email, password_hash=hash_password("Pass123!"), person_id=1, role=role)
        s.add(u)
        s.commit()
        s.refresh(u)
        return u


def auth_headers(user: User):
    from app.security import create_access_token

    token = create_access_token({"sub": str(user.id)})
    return {"Authorization": f"Bearer {token}"}


def test_products_pagination_headers():
    with SessionLocal() as s:
        est = Establishment(name=f"E{uuid4().hex[:4]}", city_id=1)
        s.add(est)
        s.flush()
        cat = ProductCategory(name=f"C{uuid4().hex[:4]}")
        s.add(cat)
        s.flush()
        for i in range(30):
            s.add(
                Product(
                    establishment_id=est.id,
                    category_id=cat.id,
                    name=f"P{i}",
                    price=100,
                    tax_rate=0.19,
                    is_active=True,
                )
            )
        s.commit()
        est_id = est.id

    r = client.get(f"/products?establishment_id={est_id}&limit=10&offset=0")
    assert r.status_code == 200
    assert r.headers.get("X-Total-Count") == "30"
    items = r.json()
    assert len(items) == 10


def test_reservation_cancel_rbac_customer_only_own():
    # seed resource + opening hour for tomorrow
    with SessionLocal() as s:
        est = Establishment(name=f"E{uuid4().hex[:4]}", city_id=1)
        s.add(est)
        s.flush()
        res = Resource(
            establishment_id=est.id,
            name=f"R{uuid4().hex[:4]}",
            slot_minutes=60,
            price_per_slot=100,
            is_active=True,
        )
        s.add(res)
        s.flush()
        tomorrow = (datetime.now(UTC) + timedelta(days=1)).date()
        s.add(
            OpeningHour(
                establishment_id=est.id,
                weekday=tomorrow.isoweekday(),
                open_time=time(8, 0),
                close_time=time(22, 0),
            )
        )
        s.commit()
        res_id = res.id

    # create two users
    u1 = create_user(f"u1+{uuid4().hex[:6]}@example.com", role="CUSTOMER")
    u2 = create_user(f"u2+{uuid4().hex[:6]}@example.com", role="CUSTOMER")

    # u1 creates a reservation via API
    start = datetime.combine((datetime.now(UTC) + timedelta(days=1)).date(), time(9, 0))
    end = start + timedelta(hours=1)
    payload = {
        "resource_id": res_id,
        "start_ts": start.isoformat(),
        "end_ts": end.isoformat(),
        "channel": "WEB",
    }
    r1 = client.post("/reservations", json=payload, headers=auth_headers(u1))
    assert r1.status_code == 201, r1.text
    rid = r1.json()["id"]

    # u2 tries to cancel u1 reservation -> 403
    r2 = client.post(f"/reservations/{rid}/cancel", headers=auth_headers(u2))
    assert r2.status_code == 403, r2.text

    # owner can cancel
    owner = create_user(f"owner+{uuid4().hex[:6]}@example.com", role="OWNER")
    r3 = client.post(f"/reservations/{rid}/cancel", headers=auth_headers(owner))
    assert r3.status_code == 200


def test_products_delete_requires_owner_or_admin():
    # seed product
    with SessionLocal() as s:
        est = Establishment(name=f"E{uuid4().hex[:4]}", city_id=1)
        s.add(est)
        s.flush()
        cat = ProductCategory(name=f"C{uuid4().hex[:4]}")
        s.add(cat)
        s.flush()
        p = Product(
            establishment_id=est.id,
            category_id=cat.id,
            name="PX",
            price=100,
            tax_rate=0.19,
            is_active=True,
        )
        s.add(p)
        s.commit()
        pid = p.id

    customer = create_user(f"c+{uuid4().hex[:6]}@example.com", role="CUSTOMER")
    r1 = client.delete(f"/products/{pid}", headers=auth_headers(customer))
    assert r1.status_code == 403

    admin = create_user(f"a+{uuid4().hex[:6]}@example.com", role="ADMIN")
    r2 = client.delete(f"/products/{pid}", headers=auth_headers(admin))
    assert r2.status_code == 204
