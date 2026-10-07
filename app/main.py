from fastapi import FastAPI
from app.database import engine, Base
from app.routers import auth, users, events, bookings, organizer

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Event Ticketing API",
    description="Backend API for Event Ticketing Platform - Attendees and Organizers",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(events.router)
app.include_router(bookings.router)
app.include_router(organizer.router)


@app.get("/")
def root():
    return {"message": "Event Ticketing API", "docs": "/docs"}
