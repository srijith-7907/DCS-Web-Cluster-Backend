from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime

from app.database import Base


class EventStatus(str, enum.Enum):
    UPCOMING = "UPCOMING"
    ACTIVE = "ACTIVE"
    STARTED = "STARTED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text)
    city = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    event_datetime = Column(DateTime(timezone=True), nullable=False, index=True)
    ticket_price = Column(Float, nullable=False)
    total_capacity = Column(Integer, nullable=False)
    remaining_capacity = Column(Integer, nullable=False)
    status = Column(Enum(EventStatus), default=EventStatus.UPCOMING, nullable=False, index=True)
    organizer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    organizer = relationship("User", back_populates="events")
    bookings = relationship("Booking", back_populates="event", cascade="all, delete-orphan")
