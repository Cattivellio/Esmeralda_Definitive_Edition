from src.infrastructure.database import SessionLocal
from src.infrastructure.models import RegistroPersonaHotel, ClienteDB

db = SessionLocal()
print("--- CHEQUEO DE COINCIDENCIAS ---")
clientes = db.query(ClienteDB).all()
for c in clientes:
    ced = c.cedula
    reg = db.query(RegistroPersonaHotel).filter(RegistroPersonaHotel.cedula == ced).first()
    if reg:
        print(f"Cliente: {ced} | REGISTRO ENCONTRADO! Estado: {reg.estado}")
    else:
        print(f"Cliente: {ced} | REGISTRO NO ENCONTRADO EN RegistroPersonaHotel")

registros = db.query(RegistroPersonaHotel).all()
print("\n--- TODOS LOS REGISTROS EN RegistroPersonaHotel ---")
for r in registros:
    print(f"[{r.cedula}] - {r.estado}")
db.close()
