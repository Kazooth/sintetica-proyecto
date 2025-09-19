import os
import json
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db import SessionLocal
from app.models import User, Person

client = TestClient(app)

TEST_EMAIL = "test_integration_user@example.com"
TEST_PW = "secret123"


def teardown_module(module):
    # clean up any created test rows
    db = SessionLocal()
    try:
        u = db.query(User).filter(User.email == TEST_EMAIL).first()
        if u:
            # also delete associated person if exists
            pid = getattr(u, 'person_id', None)
            db.delete(u)
            db.commit()
            if pid:
                p = db.get(Person, pid)
                if p:
                    db.delete(p)
                    db.commit()
    finally:
        db.close()


def test_register_creates_person_and_user():
    # Ensure no existing test user
    db = SessionLocal()
    try:
        assert db.query(User).filter(User.email == TEST_EMAIL).first() is None
    finally:
        db.close()

    payload = {"email": TEST_EMAIL, "password": TEST_PW, "first_name": "Test", "last_name": "User"}
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == TEST_EMAIL
    assert data.get("first_name") == "Test"
    assert data.get("last_name") == "User"

    # subsequent registration with same email should fail
    resp2 = client.post("/auth/register", json=payload)
    assert resp2.status_code == 409

    # cleanup (delete user and person)
    db = SessionLocal()
    try:
        u = db.query(User).filter(User.email == TEST_EMAIL).first()
        if u:
            pid = getattr(u, 'person_id', None)
            db.delete(u)
            db.commit()
            if pid:
                p = db.get(Person, pid)
                if p:
                    db.delete(p)
                    db.commit()
    finally:
        db.close()
