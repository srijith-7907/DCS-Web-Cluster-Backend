from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import threading
import queue


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
def test_concurrent_booking_race(client: TestClient):
    # Create organizer and event with only 1 seat remaining
    token_o = create_organizer(client, "orgconc@test.com")
    token_a1 = create_attendee(client, "a1@test.com")
    token_a2 = create_attendee(client, "a2@test.com")
    future = datetime.utcnow() + timedelta(days=1)
    res = client.post(
        "/events/",
        headers={"Authorization": f"Bearer {token_o}"},
        json={
            "title": "LastSeat",
            "city": "Chennai",
            "category": "Music",
            "event_datetime": future.isoformat(),
            "ticket_price": 100.0,
            "total_capacity": 1,
        },
    )
    assert res.status_code == 201
    event_id = res.json()["id"]

    results = queue.Queue()

    def attempt_booking(token):
        try:
            r = client.post(
                "/bookings/",
                headers={"Authorization": f"Bearer {token}"},
                json={"event_id": event_id, "quantity": 1},
            )
            results.put(r.status_code)
        except Exception as e:
            results.put(500)

    t1 = threading.Thread(target=attempt_booking, args=(token_a1,))
    t2 = threading.Thread(target=attempt_booking, args=(token_a2,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    # Collect results
    r1 = results.get()
    r2 = results.get()
    success_count = sum(1 for s in [r1, r2] if s == 201)
    # Under concurrent access, only one should succeed (race protection with DB locking)
    assert success_count <= 1
