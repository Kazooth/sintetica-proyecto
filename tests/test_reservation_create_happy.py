from datetime import datetime, timedelta, time, UTC
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.db import SessionLocal
from app.models import Establishment, Resource, OpeningHour


client = TestClient(app)


def register_and_login(email: str, password: str) -> str:
    r = client.post(
        "/auth/register",
        json={
            "first_name": "Happy",
            "last_name": "Path",
            "email": email,
            "password": password,
        },
    )
    assert r.status_code == 201, r.text
    r2 = client.post("/auth/login", data={"username": email, "password": password})
    assert r2.status_code == 200, r2.text
    return r2.json()["access_token"]


def seed_resource() -> int:
    with SessionLocal() as s:
        est = Establishment(name=f"Est {uuid4().hex[:6]}", city_id=1)
        s.add(est)
        s.flush()
        res = Resource(
            establishment_id=est.id,
            name=f"R {uuid4().hex[:4]}",
            slot_minutes=60,
            price_per_slot=100,
            is_active=True,
        )
        s.add(res)
        s.flush()
        tomorrow = (datetime.now(UTC) + timedelta(days=1)).date()
        dow = tomorrow.isoweekday()
        s.add(
            OpeningHour(
                establishment_id=est.id, weekday=dow, open_time=time(8, 0), close_time=time(22, 0)
            )
        )
        s.commit()
        return res.id


def test_reservation_happy_create_and_list():
    res_id = seed_resource()
    token = register_and_login(f"happy+{uuid4().hex[:6]}@example.com", "Password123!")
    headers = {"Authorization": f"Bearer {token}"}

    tomorrow = (datetime.now(UTC) + timedelta(days=1)).date()
    start = datetime.combine(tomorrow, time(9, 0))
    end = start + timedelta(hours=1)

    payload = {
        "resource_id": res_id,
        "start_ts": start.isoformat(),
        "end_ts": end.isoformat(),
        "channel": "WEB",
    }
    r = client.post("/reservations", json=payload, headers=headers)
    assert r.status_code == 201, r.text
    created = r.json()
    assert created["resource_id"] == res_id

    # List reservations for that resource/day
    day = start.date().isoformat()
    rlist = client.get(f"/reservations?resource_id={res_id}&date={day}")
    assert rlist.status_code == 200, rlist.text
    items = rlist.json()
    assert any(it["id"] == created["id"] for it in items)
