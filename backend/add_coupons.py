import sys
import os
from sqlalchemy.orm import Session

# Configuración de rutas para que Python encuentre los módulos
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_dir, "src"))

from infrastructure.database import SessionLocal
from infrastructure.models import VoucherDB

def add_coupons():
    db = SessionLocal()
    try:
        coupons = [
            {"codigo": "PROMO10", "tipo": "porcentaje", "valor": 10.0, "activo": True},
            {"codigo": "VIP20", "tipo": "porcentaje", "valor": 20.0, "activo": True},
            {"codigo": "REGALO5", "tipo": "monto", "valor": 5.0, "activo": True},
        ]
        
        for c in coupons:
            existing = db.query(VoucherDB).filter(VoucherDB.codigo == c["codigo"]).first()
            if not existing:
                db.add(VoucherDB(**c))
                print(f"Cupón {c['codigo']} creado.")
            else:
                existing.tipo = c["tipo"]
                existing.valor = c["valor"]
                existing.activo = c["activo"]
                print(f"Cupón {c['codigo']} actualizado.")
        
        db.commit()
        print("Cupones listos.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_coupons()
