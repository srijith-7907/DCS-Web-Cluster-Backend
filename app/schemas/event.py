from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from app.models.event import EventStatus


class EventBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    city: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., min_length=1, max_length=100)
    event_datetime: datetime
    ticket_price: float = Field(..., ge=0)
    total_capacity: int = Field(..., gt=0)


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    event_datetime: Optional[datetime] = None
    ticket_price: Optional[float] = Field(None, ge=0)
    total_capacity: Optional[int] = Field(None, gt=0)


class EventResponse(EventBase):
    id: int
    remaining_capacity: int
    status: EventStatus
    organizer_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class EventListResponse(BaseModel):
    items: List[EventResponse]
    total: int
    page: int
    size: int
    pages: int
