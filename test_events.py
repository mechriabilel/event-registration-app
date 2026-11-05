import pytest
from fastapi.testclient import TestClient
from app import app, Base, engine

client = TestClient(app)

def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def test_prevent_overbooking():
    response = client.post("/api/events", json={"name": "DevOps Workshop", "capacity": 1})
    assert response.status_code == 201
    event_id = response.json()["id"]

    res1 = client.post("/api/registrations", json={"event_id": event_id, "attendee": "Alice"})
    assert res1.status_code == 201
    assert "id" in res1.json()

    res2 = client.post("/api/registrations", json={"event_id": event_id, "attendee": "Bob"})
    assert res2.status_code == 400
    assert "Error" in res2.json()["detail"]