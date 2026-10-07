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
def test_attendee_booking(client: TestClient):
    token_o = create_organizer(client, "obo@test.com")
    token_a = create_attendee(client, "attb@test.com")
    future = datetime.utcnow() + timedelta(days=1)
    res = client.post(
        "/events/",
        headers={"Authorization": f"Bearer {token_o}"},
        json={
            "title": "Concert",
            "city": "Chennai",
            "category": "Music",
            "event_datetime": future.isoformat(),
            "ticket_price": 200.0,
            "total_capacity": 10,
        },
    )
    event_id = res.json()["id"]
    res = client.post(
        "/bookings/",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"event_id": event_id, "quantity": 2},
    )
    assert res.status_code == 201
    assert res.json()["quantity"] == 2


def test_invalid_booking_zero_quantity(client: TestClient):
    token_o = create_organizer(client, "obz@test.com")
    token_a = create_attendee(client, "attz@test.com")
    future = datetime.utcnow() + timedelta(days=1)
    res = client.post(
        "/events/",
        headers={"Authorization": f"Bearer {token_o}"},
        json={
            "title": "Show",
            "city": "Chennai",
            "category": "Music",
            "event_datetime": future.isoformat(),
            "ticket_price": 100.0,
            "total_capacity": 5,
        },
    )
    event_id = res.json()["id"]
    res = client.post(
        "/bookings/",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"event_id": event_id, "quantity": 0},
    )
    assert res.status_code == 422


def test_booking_insufficient_capacity(client: TestClient):
    token_o = create_organizer(client, "obi@test.com")
    token_a = create_attendee(client, "atti@test.com")
    token_a2 = create_attendee(client, "atti2@test.com")
    future = datetime.utcnow() + timedelta(days=1)
    res = client.post(
        "/events/",
        headers={"Authorization": f"Bearer {token_o}"},
        json={
            "title": "Limited",
            "city": "Chennai",
            "category": "Music",
            "event_datetime": future.isoformat(),
            "ticket_price": 100.0,
            "total_capacity": 2,
        },
    )
    event_id = res.json()["id"]
    res = client.post(
        "/bookings/",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"event_id": event_id, "quantity": 2},
    )
    assert res.status_code == 201
    res = client.post(
        "/bookings/",
        headers={"Authorization": f"Bearer {token_a2}"},
        json={"event_id": event_id, "quantity": 1},
    )
    assert res.status_code == 400


def test_booking_cancelled_event(client: TestClient):
    token_o = create_organizer(client, "obc@test.com")
    token_a = create_attendee(client, "attc@test.com")
    future = datetime.utcnow() + timedelta(days=1)
    res = client.post(
        "/events/",
        headers={"Authorization": f"Bearer {token_o}"},
        json={
            "title": "CancelEvt",
            "city": "Chennai",
            "category": "Music",
            "event_datetime": future.isoformat(),
            "ticket_price": 100.0,
            "total_capacity": 5,
        },
    )
    event_id = res.json()["id"]
    client.post(f"/events/{event_id}/cancel", headers={"Authorization": f"Bearer {token_o}"})
    res = client.post(
        "/bookings/",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"event_id": event_id, "quantity": 1},
    )
    assert res.status_code == 400
