import getpass
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from core.security import hash_password
from models.user import AuthUser

print("=== Herramienta de cambio de usuario y contraseña para SRTime ===")
print("Esta herramienta permite crear o actualizar un usuario en la base de datos.")
usuario = input("Ingrese el nombre de usuario: ").strip()
while not usuario:
    usuario = input("El usuario no puede estar vacío. Ingrese el nombre de usuario: ").strip()
contraseña = getpass.getpass("Ingrese la nueva contraseña: ").strip()
while not contraseña:
    contraseña = getpass.getpass("La contraseña no puede estar vacía. Ingrese la nueva contraseña: ").strip()

engine = create_engine("sqlite:///attendance.db")
session = Session(bind=engine)
user = session.query(AuthUser).filter_by(username=usuario).first()
if not user:
    user = AuthUser(username=usuario, password_hash=hash_password(contraseña))
    session.add(user)
    print(f"Usuario '{usuario}' creado.")
else:
    user.password_hash = hash_password(contraseña)
    print(f"Contraseña de '{usuario}' actualizada.")
session.commit()
session.close()
print("Hash guardado correctamente. Puedes iniciar sesión con el usuario y contraseña nuevos.")
