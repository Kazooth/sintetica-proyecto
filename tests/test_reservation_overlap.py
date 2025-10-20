import json
from datetime import datetime, timedelta, time, UTC
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.db import SessionLocal
from app.models import Establishment, Resource, OpeningHour

client = TestClient(app)


def register_and_login(email: str, password: str):
    r = client.post(
        "/auth/register",
        json={
            "first_name": "Test",
            "last_name": "User",
            "email": email,
            "password": password,
        },
    )
    assert r.status_code == 201
    r = client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )
    assert r.status_code == 200
    return r.json()["access_token"]


def setup_demo_resource():
    # Insert establishment, resource and opening hour directly in DB for deterministic test
    with SessionLocal() as s:
        est_name = f"Test Est {uuid4().hex[:8]}"
        est = Establishment(name=est_name, city_id=1)
        s.add(est)
        s.flush()
        res_name = f"Cancha {uuid4().hex[:6]}"
        res = Resource(
            establishment_id=est.id,
            name=res_name,
            slot_minutes=60,
            price_per_slot=100,
            is_active=True,
        )
        s.add(res)
        s.flush()
        # Weekday of tomorrow and deterministic opening hours
        tomorrow = (datetime.now(UTC) + timedelta(days=1)).date()
        dow = tomorrow.isoweekday()
        oh = OpeningHour(
            establishment_id=est.id,
            weekday=dow,
            open_time=time(8, 0, 0),
            close_time=time(22, 0, 0),
        )
        s.add(oh)
        s.commit()
        return res.id


def test_reservation_overlap():
    resource_id = setup_demo_resource()
    unique_email = f"overlap+{uuid4().hex[:6]}@example.com"
    token = register_and_login(unique_email, "password123")
    headers = {"Authorization": f"Bearer {token}"}

    # Build a deterministic start (tomorrow at 10:00) and 1 hour duration
    tomorrow_date = (datetime.now(UTC) + timedelta(days=1)).date()
    start = datetime.combine(tomorrow_date, time(10, 0, 0))
    end = start + timedelta(hours=1)

    payload = {
        "resource_id": resource_id,
        "start_ts": start.isoformat(),
        "end_ts": end.isoformat(),
        "channel": "WEB",
    }

    r1 = client.post("/reservations", json=payload, headers=headers)
    assert r1.status_code == 201, r1.text

    # overlapping
    payload2 = payload.copy()
    payload2["start_ts"] = (start + timedelta(minutes=30)).isoformat()
    payload2["end_ts"] = (end + timedelta(minutes=30)).isoformat()

    r2 = client.post("/reservations", json=payload2, headers=headers)
    assert r2.status_code == 409, r2.text
