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
def test_booking_for_started_event(client: TestClient):
    token_o = create_organizer(client, "obs@test.com")
    token_a = create_attendee(client, "atts@test.com")
    past = datetime.utcnow() - timedelta(hours=1)
    res = client.post(
        "/events/",
        headers={"Authorization": f"Bearer {token_o}"},
        json={
            "title": "PastEvt",
            "city": "Chennai",
            "category": "Music",
            "event_datetime": past.isoformat(),
            "ticket_price": 100.0,
            "total_capacity": 5,
        },
    )
    event_id = res.json()["id"]
    res = client.post(
        "/bookings/",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"event_id": event_id, "quantity": 1},
    )
    assert res.status_code == 400


def test_booking_cancellation(client: TestClient):
    token_o = create_organizer(client, "obcc@test.com")
    token_a = create_attendee(client, "attcc@test.com")
    future = datetime.utcnow() + timedelta(days=1)
    res = client.post(
        "/events/",
        headers={"Authorization": f"Bearer {token_o}"},
        json={
            "title": "Evt",
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
        json={"event_id": event_id, "quantity": 2},
    )
    booking_id = res.json()["id"]
    res = client.post(f"/bookings/{booking_id}/cancel", headers={"Authorization": f"Bearer {token_a}"})
    assert res.status_code == 200


def test_event_cancellation(client: TestClient):
    token_o = create_organizer(client, "obec@test.com")
    token_a = create_attendee(client, "attec@test.com")
    future = datetime.utcnow() + timedelta(days=1)
    res = client.post(
        "/events/",
        headers={"Authorization": f"Bearer {token_o}"},
        json={
            "title": "EvtC",
            "city": "Chennai",
            "category": "Music",
            "event_datetime": future.isoformat(),
            "ticket_price": 100.0,
            "total_capacity": 5,
        },
    )
    event_id = res.json()["id"]
    client.post(
        "/bookings/",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"event_id": event_id, "quantity": 1},
    )
    res = client.post(f"/events/{event_id}/cancel", headers={"Authorization": f"Bearer {token_o}"})
    assert res.status_code == 200


def test_organizer_booking_access_and_sales(client: TestClient):
    token_o = create_organizer(client, "obsales@test.com")
    token_a = create_attendee(client, "attsales@test.com")
    future = datetime.utcnow() + timedelta(days=1)
    res = client.post(
        "/events/",
        headers={"Authorization": f"Bearer {token_o}"},
        json={
            "title": "SalesEvt",
            "city": "Chennai",
            "category": "Music",
            "event_datetime": future.isoformat(),
            "ticket_price": 150.0,
            "total_capacity": 10,
        },
    )
    event_id = res.json()["id"]
    client.post(
        "/bookings/",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"event_id": event_id, "quantity": 3},
    )
    res = client.get(f"/organizer/events/{event_id}/bookings", headers={"Authorization": f"Bearer {token_o}"})
    assert res.status_code == 200
    res = client.get(f"/organizer/events/{event_id}/sales", headers={"Authorization": f"Bearer {token_o}"})
    assert res.status_code == 200
    assert res.json()["tickets_sold"] == 3
    assert res.json()["revenue"] == 450.0
