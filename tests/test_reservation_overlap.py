import json
from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from app.main import app

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


def test_reservation_overlap():
    token = register_and_login("overlap@example.com", "password123")
    headers = {"Authorization": f"Bearer {token}"}

    # Create a resource and opening hours via endpoints if needed; assume demo data exists
    # For simplicity, attempt two overlapping reservations on resource_id 1
    now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    start = now + timedelta(days=1, hours=10)
    end = start + timedelta(hours=1)

    payload = {
        "resource_id": 1,
        "start_ts": start.isoformat(),
        "end_ts": end.isoformat(),
        "channel": "WEB",
    }

    r1 = client.post("/reservations", json=payload, headers=headers)
    assert r1.status_code == 201

    # overlapping
    payload2 = payload.copy()
    payload2["start_ts"] = (start + timedelta(minutes=30)).isoformat()
    payload2["end_ts"] = (end + timedelta(minutes=30)).isoformat()

    r2 = client.post("/reservations", json=payload2, headers=headers)
    assert r2.status_code == 409
