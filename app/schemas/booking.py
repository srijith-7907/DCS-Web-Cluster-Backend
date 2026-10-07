from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from app.models.booking import BookingStatus, RefundStatus


class BookingCreate(BaseModel):
    event_id: int
    quantity: int = Field(..., gt=0, description="Number of tickets (must be > 0)")


class BookingResponse(BaseModel):
    id: int
    attendee_id: int
    event_id: int
    quantity: int
    total_amount: float
    booking_status: BookingStatus
    refund_status: RefundStatus
    created_at: datetime
    cancelled_at: Optional[datetime]

    class Config:
        from_attributes = True


class BookingCancelResponse(BaseModel):
    message: str
    booking_id: int
    booking_status: BookingStatus
