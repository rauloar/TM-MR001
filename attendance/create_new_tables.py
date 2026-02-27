from core.database import engine
from models.behavior_feature import BehaviorFeatureStore
from models.attendance_behavior import AttendanceBehavior
from models.rule_set import RuleSet
from models.rule import Rule

# Solo crea las tablas nuevas si no existen
BehaviorFeatureStore.__table__.create(bind=engine, checkfirst=True)
AttendanceBehavior.__table__.create(bind=engine, checkfirst=True)
RuleSet.__table__.create(bind=engine, checkfirst=True)
Rule.__table__.create(bind=engine, checkfirst=True)
print("Tablas nuevas creadas si no existían.")
