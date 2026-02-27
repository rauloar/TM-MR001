import sqlalchemy
from core.database import engine, Base

# List of tables to truncate (excluding 'auth_user')
tables_to_truncate = [
    'attendance_log',
    'users',
]

def truncate_tables():
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            for table in tables_to_truncate:
                try:
                    conn.execute(sqlalchemy.text(f"DELETE FROM {table}"))
                except Exception as e:
                    print(f"Warning: No se pudo truncar {table}: {e}")
                # Only reset sqlite_sequence if it exists
                try:
                    result = conn.execute(sqlalchemy.text("SELECT name FROM sqlite_master WHERE type='table' AND name='sqlite_sequence'"))
                    if result.fetchone():
                        conn.execute(sqlalchemy.text(f"DELETE FROM sqlite_sequence WHERE name='{table}'"))
                except Exception:
                    pass
            trans.commit()
        except Exception as e:
            trans.rollback()
            print(f"Error truncating tables: {e}")
        else:
            print("Tables truncated successfully.")

if __name__ == "__main__":
    truncate_tables()
