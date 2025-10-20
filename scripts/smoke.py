from __future__ import annotations

import sys
from uuid import uuid4
from datetime import datetime, timedelta, time, UTC

from fastapi.testclient import TestClient

from app.main import app
from app.db import SessionLocal
from app.models import Establishment, Resource, OpeningHour


def seed_resource() -> int:
    """Create a minimal establishment/resource/opening-hours for tomorrow.

    Returns the new resource_id.
    """
    with SessionLocal() as s:
        est = Establishment(name=f"Smoke Est {uuid4().hex[:6]}", city_id=1)
        s.add(est)
        s.flush()

        res = Resource(
            establishment_id=est.id,
            name=f"Smoke R {uuid4().hex[:4]}",
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
                establishment_id=est.id,
                weekday=dow,
                open_time=time(8, 0),
                close_time=time(22, 0),
            )
        )
        s.commit()
        return res.id


def main() -> int:
    print("[smoke] starting...")
    client = TestClient(app)

    # 1) Seed minimal resource
    res_id = seed_resource()
    print(f"[smoke] seeded resource_id={res_id}")

    # 2) Register and login
    email = f"smoke+{uuid4().hex[:8]}@example.com"
    password = "Password123!"
    r = client.post(
        "/auth/register",
        json={
            "first_name": "Smoke",
            "last_name": "Test",
            "email": email,
            "password": password,
        },
    )
    if r.status_code != 201:
        print(f"[smoke][ERROR] register failed: {r.status_code} {r.text}")
        return 1
    print("[smoke] register OK")

    r2 = client.post("/auth/login", data={"username": email, "password": password})
    if r2.status_code != 200:
        print(f"[smoke][ERROR] login failed: {r2.status_code} {r2.text}")
        return 1
    token = r2.json().get("access_token")
    if not token:
        print("[smoke][ERROR] login token missing")
        return 1
    print("[smoke] login OK")

    headers = {"Authorization": f"Bearer {token}"}

    # 3) Create reservation for tomorrow 09:00 -> 10:00
    tomorrow = (datetime.now(UTC) + timedelta(days=1)).date()
    start = datetime.combine(tomorrow, time(9, 0))
    end = start + timedelta(hours=1)
    payload = {
        "resource_id": res_id,
        "start_ts": start.isoformat(),
        "end_ts": end.isoformat(),
        "channel": "WEB",
    }
    r3 = client.post("/reservations", json=payload, headers=headers)
    if r3.status_code != 201:
        print(f"[smoke][ERROR] reservation create failed: {r3.status_code} {r3.text}")
        return 1
    created = r3.json()
    print(f"[smoke] reservation created id={created.get('id')}")

    # 4) List reservations for that resource/date
    day = start.date().isoformat()
    r4 = client.get(f"/reservations?resource_id={res_id}&date={day}")
    if r4.status_code != 200:
        print(f"[smoke][ERROR] reservation list failed: {r4.status_code} {r4.text}")
        return 1
    items = r4.json()
    found = any(it.get("id") == created.get("id") for it in items)
    if not found:
        print("[smoke][ERROR] created reservation not found in list")
        return 1
    print("[smoke] list OK; reservation present")

    print("[smoke] SUCCESS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
