from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base


class BookingStatus(str, enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"
    EXPIRED = "EXPIRED"


class RefundStatus(str, enum.Enum):
    NONE = "NONE"
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    attendee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    total_amount = Column(Float, nullable=False)
    booking_status = Column(Enum(BookingStatus), default=BookingStatus.CONFIRMED, nullable=False)
    refund_status = Column(Enum(RefundStatus), default=RefundStatus.NONE, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    cancelled_at = Column(DateTime(timezone=True), nullable=True)

    attendee = relationship("User", back_populates="bookings")
    event = relationship("Event", back_populates="bookings")
