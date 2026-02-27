from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Ruta absoluta y creación segura del directorio attendance/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.abspath(os.path.join(BASE_DIR, '../attendance'))
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, 'attendance.db')
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)

# Importar Base unificada
from attendance.models.base import Base