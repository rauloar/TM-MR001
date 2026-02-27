from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    ForeignKey
)
from sqlalchemy.orm import relationship
from .base import Base


class Rule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True)
    rule_set_id = Column(Integer, ForeignKey("rule_sets.id"))

    metric_name = Column(String, nullable=False)
    operator = Column(String, nullable=False)
    threshold = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)

    rule_set = relationship("RuleSet", back_populates="rules")