import sys
import os

# Configuración de rutas
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_dir, "src"))

from infrastructure.database import SessionLocal, engine, Base
from infrastructure.models import (
    HabitacionDB, EstanciaDB, EstanciaHabitacion, 
    EstanciaHuesped, PagoDB, IngresoExtraDB, EstadoHabitacion
)
from sqlalchemy import text

def reset_all_to_zero():
    db = SessionLocal()
    try:
        print("--- Iniciando Reset Total ---")
        
        # 1. Limpiar todas las tablas transaccionales (en orden por FK)
        print("Borrando transacciones (pagos, extras, estancias)...")
        db.query(PagoDB).delete()
        db.query(IngresoExtraDB).delete()
        db.query(EstanciaHuesped).delete()
        db.query(EstanciaHabitacion).delete()
        
        # Desvincular estancias de habitaciones antes de borrar estancias
        db.query(HabitacionDB).update({HabitacionDB.estancia_actual_id: None, HabitacionDB.estado: EstadoHabitacion.libre})
        db.commit()
        
        db.query(EstanciaDB).delete()
        print("Tablas de estancias limpias.")

        # 2. Asegurar que todas las habitaciones estén Libres
        print("Reseteando todas las habitaciones a estado 'libre'...")
        db.query(HabitacionDB).update({
            HabitacionDB.estado: EstadoHabitacion.libre,
            HabitacionDB.estancia_actual_id: None
        })
        
        db.commit()
        print("--- ÉXITO: Todo el hotel está vacío y libre ---")
        
    except Exception as e:
        print(f"Error durante el reset: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_all_to_zero()
