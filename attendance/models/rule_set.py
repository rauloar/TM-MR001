from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime
)
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class RuleSet(Base):
    __tablename__ = "rule_sets"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    version = Column(Integer, nullable=False)

    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date)

    created_at = Column(DateTime, default=datetime.utcnow)

    rules = relationship("Rule", back_populates="rule_set")