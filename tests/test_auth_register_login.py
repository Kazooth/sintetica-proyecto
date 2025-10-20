from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_register_and_login_flow():
    email = f"user+{uuid4().hex[:8]}@example.com"
    password = "Password123!"

    r = client.post(
        "/auth/register",
        json={
            "first_name": "Test",
            "last_name": "User",
            "email": email,
            "password": password,
        },
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["email"].lower() == email.lower()

    r2 = client.post("/auth/login", data={"username": email, "password": password})
    assert r2.status_code == 200, r2.text
    tok = r2.json().get("access_token")
    assert tok and isinstance(tok, str)
