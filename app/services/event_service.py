from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime

from app.models.user import User, UserRole
from app.models.event import Event, EventStatus
from app.schemas.event import EventCreate, EventUpdate


class EventService:
    @staticmethod
    def create_event(db: Session, event_data: EventCreate, organizer: User):
        event = Event(
            title=event_data.title,
            description=event_data.description,
            city=event_data.city,
            category=event_data.category,
            event_datetime=event_data.event_datetime,
            ticket_price=event_data.ticket_price,
            total_capacity=event_data.total_capacity,
            remaining_capacity=event_data.total_capacity,
            organizer_id=organizer.id,
            status=EventStatus.UPCOMING,
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def get_event(db: Session, event_id: int):
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        return event

    @staticmethod
    def update_event(db: Session, event_id: int, event_data: EventUpdate, organizer: User):
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        if event.organizer_id != organizer.id:
            raise HTTPException(status_code=403, detail="Not authorized to update this event")
        now = datetime.utcnow()
        if event.event_datetime.tzinfo is None:
            event_dt = event.event_datetime
        else:
            event_dt = event.event_datetime.replace(tzinfo=None)
        if event_dt <= datetime.utcnow():
            pass
        if event.status == EventStatus.STARTED or event.status == EventStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Cannot modify event once started")
        if event.status == EventStatus.CANCELLED:
            raise HTTPException(status_code=400, detail="Cannot modify cancelled event")

        if event_data.title is not None:
            event.title = event_data.title
        if event_data.description is not None:
            event.description = event_data.description
        if event_data.city is not None:
            event.city = event_data.city
        if event_data.category is not None:
            event.category = event_data.category
        if event_data.event_datetime is not None:
            event.event_datetime = event_data.event_datetime
        if event_data.ticket_price is not None:
            event.ticket_price = event_data.ticket_price
        if event_data.total_capacity is not None:
            if event_data.total_capacity < (event.total_capacity - event.remaining_capacity):
                raise HTTPException(status_code=400, detail="Cannot reduce capacity below tickets sold")
            event.remaining_capacity = event.remaining_capacity + (event_data.total_capacity - event.total_capacity)
            event.total_capacity = event_data.total_capacity

        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def delete_event(db: Session, event_id: int, organizer: User):
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        if event.organizer_id != organizer.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this event")
        db.delete(event)
        db.commit()
        return {"message": "Event deleted successfully"}

    @staticmethod
    def cancel_event(db: Session, event_id: int, organizer: User):
        from app.models.booking import Booking, BookingStatus, RefundStatus

        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        if event.organizer_id != organizer.id:
            raise HTTPException(status_code=403, detail="Not authorized to cancel this event")
        if event.status == EventStatus.CANCELLED:
            raise HTTPException(status_code=400, detail="Event already cancelled")
        event.status = EventStatus.CANCELLED
        bookings = db.query(Booking).filter(Booking.event_id == event_id).all()
        for booking in bookings:
            if booking.booking_status != BookingStatus.CANCELLED:
                booking.booking_status = BookingStatus.CANCELLED
                booking.refund_status = RefundStatus.PENDING
                booking.cancelled_at = datetime.utcnow()
        db.commit()
        db.refresh(event)
        return {"message": "Event cancelled successfully", "event_id": event_id}
