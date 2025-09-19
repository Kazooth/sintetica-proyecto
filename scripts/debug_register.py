from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

payload = {"email": "test_integration_user@example.com", "password": "secret123", "first_name": "Test", "last_name": "User"}
resp = client.post("/auth/register", json=payload)
print('status', resp.status_code)
try:
    print('json:', resp.json())
except Exception as e:
    print('raw:', resp.text)
