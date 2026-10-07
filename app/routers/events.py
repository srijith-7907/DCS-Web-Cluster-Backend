from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.database import get_db
from app.models.user import User, UserRole
from app.models.event import Event, EventStatus
from app.dependencies import require_organizer
from app.auth.utils import get_current_active_user
from app.schemas.event import EventCreate, EventUpdate, EventResponse, EventListResponse
from app.services.event_service import EventService
from math import ceil

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("/", response_model=EventResponse, status_code=201)
def create_event(
    event_data: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer),
):
    return EventService.create_event(db, event_data, current_user)


@router.get("/", response_model=EventListResponse)
def list_events(
    db: Session = Depends(get_db),
    category: Optional[str] = Query(None, description="Filter by category"),
    city: Optional[str] = Query(None, description="Filter by city"),
    start_date: Optional[datetime] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="End date (ISO format)"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
):
    query = db.query(Event).filter(Event.status != EventStatus.CANCELLED)
    query = query.filter(Event.event_datetime > datetime.utcnow())

    if category:
        query = query.filter(Event.category.ilike(f"%{category}%"))
    if city:
        query = query.filter(Event.city.ilike(f"%{city}%"))
    if start_date:
        query = query.filter(Event.event_datetime >= start_date)
    if end_date:
        query = query.filter(Event.event_datetime <= end_date)
    if min_price is not None:
        query = query.filter(Event.ticket_price >= min_price)
    if max_price is not None:
        query = query.filter(Event.ticket_price <= max_price)

    total = query.count()
    events = query.order_by(Event.event_datetime).offset((page - 1) * size).limit(size).all()
    pages = ceil(total / size) if size > 0 else 0
    return EventListResponse(items=events, total=total, page=page, size=size, pages=pages)


@router.get("/{event_id}", response_model=EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    return EventService.get_event(db, event_id)


@router.put("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: int,
    event_data: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer),
):
    return EventService.update_event(db, event_id, event_data, current_user)


@router.delete("/{event_id}")
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer),
):
    return EventService.delete_event(db, event_id, current_user)


@router.post("/{event_id}/cancel")
def cancel_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer),
):
    return EventService.cancel_event(db, event_id, current_user)
