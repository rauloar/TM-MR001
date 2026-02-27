from core.database import engine, Base
from attendance import models  # Importa todos los modelos y los registra una sola vez
from sqlalchemy.orm import Session
from core.security import hash_password

def init_database():
    Base.metadata.create_all(bind=engine)
    session = Session(bind=engine)

    admin = session.query(models.AuthUser).filter_by(username="admin").first()
    if not admin:
        admin = models.AuthUser(
            username="admin",
            password_hash=hash_password("admin")
        )
        session.add(admin)
        session.commit()
    else:
        admin.password_hash = hash_password("admin")
        session.commit()

    session.close()