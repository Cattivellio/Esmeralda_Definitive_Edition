from src.infrastructure.database import SessionLocal
from src.infrastructure.models import User, RegistroPersonaHotel

db = SessionLocal()
try:
    print("--- MAIDS IN USERS ---")
    camareras = db.query(User).filter(User.rol == "camarera").all()
    for c in camareras:
         print(f"User: {c.username}, Name: {c.nombre}")
    
    print("\n--- HOTEL REGISTRY ---")
    regs = db.query(RegistroPersonaHotel).filter(RegistroPersonaHotel.cargo.ilike('%camarera%')).all()
    for r in regs:
        print(f"Name: {r.nombre}, State: {r.estado}")

finally:
    db.close()
