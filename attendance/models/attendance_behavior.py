from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    Date,
    DateTime
)
from datetime import datetime
from .base import Base


class AttendanceBehavior(Base):
    __tablename__ = "attendance_behavior"

    id = Column(Integer, primary_key=True)
    user_identifier = Column(String(15), index=True, nullable=False)

    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)

    score = Column(Float)
    risk = Column(String(20))

    created_at = Column(DateTime, default=datetime.utcnow)