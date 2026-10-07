from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User, UserRole
from app.models.booking import Booking
from app.dependencies import require_attendee
from app.auth.utils import get_current_active_user
from app.schemas.booking import BookingCreate, BookingResponse, BookingCancelResponse
from app.services.booking_service import BookingService
from app.services.email_service import email_service

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("/", response_model=BookingResponse, status_code=201)
async def book_tickets(
    booking_data: BookingCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_attendee),
):
    booking = BookingService.book_tickets(db, booking_data, current_user)
    try:
        from app.models.event import Event

        event = db.query(Event).filter(Event.id == booking.event_id).first()
        if event:
            background_tasks.add_task(
                email_service.send_booking_confirmation,
                to_email=current_user.email,
                attendee_name=current_user.full_name,
                event_name=event.title,
                event_datetime=str(event.event_datetime),
                quantity=booking.quantity,
                total_amount=booking.total_amount,
                booking_id=booking.id,
            )
    except Exception:
        pass
    return booking


@router.get("/me", response_model=List[BookingResponse])
def get_my_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_attendee),
):
    bookings = db.query(Booking).filter(Booking.attendee_id == current_user.id).all()
    return bookings


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return BookingService.get_booking(db, booking_id, current_user)


@router.post("/{booking_id}/cancel", response_model=BookingCancelResponse)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_attendee),
):
    booking = BookingService.cancel_booking(db, booking_id, current_user)
    return BookingCancelResponse(
        message="Booking cancelled successfully",
        booking_id=booking.id,
        booking_status=booking.booking_status,
    )
