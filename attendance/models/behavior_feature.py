from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    Date,
    DateTime
)
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class BehaviorFeatureStore(Base):
    __tablename__ = "behavior_feature_store"

    id = Column(Integer, primary_key=True)
    user_identifier = Column(String(15), index=True, nullable=False)

    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)

    avg_daily_minutes = Column(Float)
    median_daily_minutes = Column(Float)
    std_daily_minutes = Column(Float)
    underwork_rate = Column(Float)
    overwork_rate = Column(Float)
    coefficient_variation = Column(Float)
    inconsistency_count = Column(Integer)
    trend_slope_minutes = Column(Float)
    volatility_index = Column(Float)
    sudden_drop_flag = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow)