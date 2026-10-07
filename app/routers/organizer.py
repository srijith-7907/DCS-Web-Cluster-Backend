from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User, UserRole
from app.models.event import Event, EventStatus
from app.models.booking import Booking, BookingStatus
from app.dependencies import require_organizer
from app.schemas.event import EventResponse
from app.schemas.booking import BookingResponse
from app.auth.utils import get_current_active_user

router = APIRouter(prefix="/organizer", tags=["Organizer"])


@router.get("/events", response_model=List[EventResponse])
def get_my_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer),
):
    events = db.query(Event).filter(Event.organizer_id == current_user.id).all()
    return events


@router.get("/events/{event_id}/bookings", response_model=List[BookingResponse])
def get_event_bookings(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer),
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view bookings for this event")
    bookings = db.query(Booking).filter(Booking.event_id == event_id).all()
    return bookings


@router.get("/events/{event_id}/sales")
def get_event_sales(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer),
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view sales for this event")
    bookings = db.query(Booking).filter(
        Booking.event_id == event_id,
        Booking.booking_status != BookingStatus.CANCELLED,
    ).all()
    tickets_sold = sum(b.quantity for b in bookings)
    revenue = sum(b.total_amount for b in bookings)
    return {
        "event_id": event_id,
        "event_title": event.title,
        "tickets_sold": tickets_sold,
        "revenue": revenue,
        "remaining_capacity": event.remaining_capacity,
        "total_capacity": event.total_capacity,
    }
