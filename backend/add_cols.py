from src.infrastructure.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    db.execute(text("ALTER TABLE habitaciones ADD COLUMN observaciones TEXT;"))
    db.commit()
    print("Columns added: observaciones")
except Exception as e:
    print("Err observaciones:", e)

try:
    db.execute(text("ALTER TABLE habitaciones ADD COLUMN descripcion TEXT;"))
    db.commit()
    print("Columns added: descripcion")
except Exception as e:
    print("Err descripcion:", e)

try:
    db.execute(text("ALTER TABLE habitaciones ADD COLUMN amenities TEXT;"))
    db.commit()
    print("Columns added: amenities")
except Exception as e:
    print("Err amenities:", e)

db.close()
