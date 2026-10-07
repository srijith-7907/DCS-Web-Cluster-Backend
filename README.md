# Event Ticketing Platform - Backend

A complete FastAPI backend for an Event Ticketing Platform supporting Attendees and Organizers with JWT authentication, role-based authorization, secure booking with database-level concurrency protection (SELECT ... FOR UPDATE), booking/event cancellations, refunds, organizer sales, SMTP email confirmations, and Swagger/OpenAPI documentation.

## Technology Stack

- Python 3.11
- FastAPI
- PostgreSQL
- SQLAlchemy (ORM)
- Pydantic (Validation)
- JWT (Authentication)
- Passlib + Bcrypt (Password Hashing)
- aiosmtplib (SMTP Email)
- Pytest (Testing)
- Docker & Docker Compose

## Project Structure

\\\
app/
  main.py
  database.py
  config.py
  dependencies.py
  models/
    __init__.py
    user.py
    event.py
    booking.py
  schemas/
    __init__.py
    user.py
    event.py
    booking.py
    token.py
  routers/
    __init__.py
    auth.py
    users.py
    events.py
    bookings.py
    organizer.py
  services/
    __init__.py
    auth_service.py
    event_service.py
    booking_service.py
    email_service.py
tests/
  __init__.py
  conftest.py
  test_auth.py
  test_events.py
  test_bookings.py
  test_concurrency.py
Dockerfile
docker-compose.yml
requirements.txt
.env.example
README.md
\\\

## Prerequisites

- Python 3.11+ (for local development)
- PostgreSQL 15+ (for local development)
- Docker & Docker Compose (recommended)

## Environment Variables

Copy \.env.example\ to \.env\ and update values:

\\\
cp .env.example .env
\\\

Required variables:
- DATABASE_URL: PostgreSQL connection string
- JWT_SECRET_KEY: Secret key for JWT signing (change in production)
- JWT_ALGORITHM: HS256
- ACCESS_TOKEN_EXPIRE_MINUTES: Token expiry (default 30)
- SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SMTP_FROM_EMAIL, SMTP_USE_TLS
- APP_NAME, APP_ENV

## Database Setup & Migrations

This project uses SQLAlchemy's \create_all\ for simple initialization. Tables are created automatically on app startup. For production, consider Alembic for migrations.

### Local
Ensure PostgreSQL is running and DATABASE_URL points to it. Tables auto-create on startup.

### Docker
Tables auto-create on startup via \pp.database.Base.metadata.create_all\.

## Running Locally

1. Create virtual environment:
\\\
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
\\\

2. Install dependencies:
\\\
pip install -r requirements.txt
\\\

3. Set up environment:
\\\
cp .env.example .env
# Edit .env as needed
\\\

4. Start PostgreSQL and ensure DATABASE_URL is correct

5. Run the server:
\\\
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
\\\

API will be available at http://localhost:8000

## Running with Docker

\\\
docker-compose up --build
\\\

This starts PostgreSQL and FastAPI. API at http://localhost:8000. For MailHog testing, run MailHog separately on port 1025/8025 if desired.

## Swagger / OpenAPI Documentation

Swagger UI: http://localhost:8000/docs
OpenAPI JSON: http://localhost:8000/openapi.json

All endpoints are documented with request/response schemas, auth requirements, and possible error codes.

## Authentication

- Register with role ATTENDEE or ORGANIZER
- Login to get JWT access token
- Include token in Authorization header: \Bearer <token>\
- Role-based authorization enforced on protected endpoints
- Ownership checks prevent cross-user/organizer access

## Main API Endpoints

### Auth
- POST /auth/register - Register user
- POST /auth/login - Login (OAuth2 password flow)
- GET /users/me - Current user profile

### Events
- GET /events/ - List upcoming events (public; supports filtering, pagination)
- GET /events/{event_id} - Get event details
- POST /events/ - Create event (ORGANIZER only)
- PUT /events/{event_id} - Update event (ORGANIZER owner only; cannot update if started)
- DELETE /events/{event_id} - Delete event (ORGANIZER owner only)
- POST /events/{event_id}/cancel - Cancel event (ORGANIZER owner only)

### Bookings
- POST /bookings/ - Book tickets (ATTENDEE only; atomic, concurrency-safe)
- GET /bookings/me - My bookings (ATTENDEE)
- GET /bookings/{booking_id} - Get booking (owner only)
- POST /bookings/{booking_id}/cancel - Cancel booking (ATTENDEE owner only)

### Organizer
- GET /organizer/events - My events (ORGANIZER)
- GET /organizer/events/{event_id}/bookings - Bookings for my event (ORGANIZER owner only)
- GET /organizer/events/{event_id}/sales - Sales summary (ORGANIZER owner only)

## Business Rules

- Events cannot be modified if already started
- Bookings not allowed for started or cancelled events
- Zero/negative quantities disallowed; cannot exceed capacity
- Only one booking gets last seat under concurrent requests (DB-level locking)
- Attendees can only cancel their own bookings within allowed window
- Organizers can only manage their own events/bookings
- Passwords are hashed; no plaintext storage
- All inputs validated with Pydantic

## Concurrency / Last-Seat Handling

Booking uses a transaction with SELECT ... FOR UPDATE on the Event row. Capacity check and decrement happen atomically inside the transaction. This prevents race conditions when multiple users book the last remaining seat simultaneously. Only one succeeds; others get 400/insufficient capacity. See code comments and \	ests/test_concurrency.py\.

## Error Handling

Consistent JSON errors with appropriate HTTP codes (400, 401, 403, 404, 409, 422). Sensitive data never exposed.

## SMTP Email

On successful booking, confirmation email sent via SMTP using env vars. If email fails, the error is logged and booking still succeeds (non-blocking to avoid corrupting transaction). Configurable for MailHog/local SMTP.

## Testing

Run all tests:
\\\
pytest -v
\\\

Tests cover auth, events, bookings, authorization, validation, cancellations, and a real concurrent booking race test (\	est_concurrent_booking_race\).

## Security Considerations

- Bcrypt password hashing
- JWT access tokens with expiry
- Role-based and ownership authorization
- Input validation on all endpoints
- No hardcoded secrets (.env.example only)
- Safe error messages
- Protection against overbooking and unauthorized access

## Limitations

- Simple table creation (no Alembic migrations) - suitable for assignment
- Email sending is best-effort (doesn't retry on transient failures)
- No refresh tokens (not requested)
- No Redis/caching/background jobs (intentionally omitted per requirements)
