from fastapi.testclient import TestClient
from datetime import datetime, timedelta


def create_organizer(client: TestClient, email="org@test.com"):
    try:
        client.post(
            "/auth/register",
            json={"email": email, "password": "password123", "full_name": "Org", "role": "ORGANIZER"},
        )
    except:
        pass
    res = client.post("/auth/login", data={"username": email, "password": "password123"})
    return res.json()["access_token"]


def create_attendee(client: TestClient, email="att@test.com"):
    try:
        client.post(
            "/auth/register",
            json={"email": email, "password": "password123", "full_name": "Att", "role": "ATTENDEE"},
        )
    except:
        pass
    res = client.post("/auth/login", data={"username": email, "password": "password123"})
    return res.json()["access_token"]


def test_create_event_organizer(client: TestClient):
    token = create_organizer(client)
    future = datetime.utcnow() + timedelta(days=1)
    res = client.post(
        "/events/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test Event",
            "description": "desc",
            "city": "Chennai",
            "category": "Tech",
            "event_datetime": future.isoformat(),
            "ticket_price": 100.0,
            "total_capacity": 50,
        },
    )
    assert res.status_code == 201
    assert res.json()["title"] == "Test Event"


def test_attendee_cannot_create_event(client: TestClient):
    token = create_attendee(client)
    future = datetime.utcnow() + timedelta(days=1)
    res = client.post(
        "/events/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Bad",
            "city": "Chennai",
            "category": "Tech",
            "event_datetime": future.isoformat(),
            "ticket_price": 100.0,
            "total_capacity": 50,
        },
    )
    assert res.status_code == 403


def test_list_events_filtering(client: TestClient):
    token = create_organizer(client, "orgf@test.com")
    future = datetime.utcnow() + timedelta(days=1)
    client.post(
        "/events/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Tech Conf",
            "city": "Chennai",
            "category": "Tech",
            "event_datetime": future.isoformat(),
            "ticket_price": 100.0,
            "total_capacity": 50,
        },
    )
    res = client.get("/events/?city=Chennai&category=Tech")
    assert res.status_code == 200
    assert res.json()["total"] >= 1


def test_organizer_ownership_restriction(client: TestClient):
    token1 = create_organizer(client, "o1@test.com")
    token2 = create_organizer(client, "o2@test.com")
    future = datetime.utcnow() + timedelta(days=1)
    res = client.post(
        "/events/",
        headers={"Authorization": f"Bearer {token1}"},
        json={
            "title": "E1",
            "city": "Chennai",
            "category": "Tech",
            "event_datetime": future.isoformat(),
            "ticket_price": 100.0,
            "total_capacity": 50,
        },
    )
    event_id = res.json()["id"]
    res = client.put(
        f"/events/{event_id}",
        headers={"Authorization": f"Bearer {token2}"},
        json={"title": "Hacked"},
    )
    assert res.status_code == 403
