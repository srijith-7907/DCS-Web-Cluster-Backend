from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
from sqlalchemy import select
from app.models.event import Event, EventStatus
from app.models.booking import Booking, BookingStatus, RefundStatus
from app.models.user import User
from app.schemas.booking import BookingCreate


class BookingService:
    @staticmethod
    def book_tickets(db: Session, booking_data: BookingCreate, attendee: User):
        # Get event with row-level lock to prevent overbooking (concurrency protection)
        # We lock the event row for update to ensure atomic capacity check/update
        stmt = select(Event).where(Event.id == booking_data.event_id).with_for_update()
        event = db.execute(stmt).scalar_one_or_none()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        if event.status == EventStatus.CANCELLED:
            raise HTTPException(status_code=400, detail="Cannot book tickets for cancelled event")
        if event.status == EventStatus.STARTED or event.status == EventStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Cannot book tickets for event that has started")

        now = datetime.utcnow()
        event_dt = event.event_datetime
        if event_dt.tzinfo is not None:
            event_dt = event_dt.replace(tzinfo=None)
        if event_dt <= now:
            raise HTTPException(status_code=400, detail="Event has already started")

        if booking_data.quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be greater than 0")

        if event.remaining_capacity < booking_data.quantity:
            raise HTTPException(status_code=400, detail="Insufficient capacity")

        total_amount = event.ticket_price * booking_data.quantity
        event.remaining_capacity -= booking_data.quantity

        booking = Booking(
            attendee_id=attendee.id,
            event_id=event.id,
            quantity=booking_data.quantity,
            total_amount=total_amount,
            booking_status=BookingStatus.CONFIRMED,
            refund_status=RefundStatus.NONE,
        )
        db.add(booking)
        db.commit()
        db.refresh(booking)
        db.refresh(event)
        return booking

    @staticmethod
    def cancel_booking(db: Session, booking_id: int, attendee: User):
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        if booking.attendee_id != attendee.id:
            raise HTTPException(status_code=403, detail="Not authorized to cancel this booking")
        if booking.booking_status == BookingStatus.CANCELLED:
            raise HTTPException(status_code=400, detail="Booking already cancelled")
        event = db.query(Event).filter(Event.id == booking.event_id).first()
        if event and event.status != EventStatus.CANCELLED:
            event.remaining_capacity += booking.quantity
        booking.booking_status = BookingStatus.CANCELLED
        booking.refund_status = RefundStatus.PENDING
        booking.cancelled_at = datetime.utcnow()
        db.commit()
        db.refresh(booking)
        return booking

    @staticmethod
    def get_booking(db: Session, booking_id: int, user: User):
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        if user.role == "ATTENDEE" and booking.attendee_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        if user.role == "ORGANIZER":
            event = db.query(Event).filter(Event.id == booking.event_id).first()
            if not event or event.organizer_id != user.id:
                raise HTTPException(status_code=403, detail="Not authorized")
        return booking
