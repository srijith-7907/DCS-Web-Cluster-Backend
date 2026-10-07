from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base


class UserRole(str, enum.Enum):
    ATTENDEE = "ATTENDEE"
    ORGANIZER = "ORGANIZER"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    events = relationship("Event", back_populates="organizer")
    bookings = relationship("Booking", back_populates="attendee")
