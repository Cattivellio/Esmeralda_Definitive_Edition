import sys
import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
import uuid

# Configuración de rutas
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_dir, "src"))

from infrastructure.database import Base
from infrastructure.models import (
    User, HabitacionDB, ClienteDB, EstanciaDB, EstanciaHabitacion, 
    EstanciaHuesped, MetodoPagoDB, VoucherDB, PagoDB, IngresoExtraDB, 
    LogDB, ConfiguracionDB, TurnoDB, HistorialAcceso, RegistroPersonaHotel, NovedadDB
)

# URLs de conexión
POSTGRES_URL = "postgresql://postgres:cattivellio@localhost:5432/esmeralda_db"
SQLITE_URL = "sqlite:///./esmeralda.db"

def migrate():
    print("--- Iniciando Migración de Postgres a SQLite ---")
    
    # Motores y Sesiones
    pg_engine = create_engine(POSTGRES_URL)
    sqlite_engine = create_engine(SQLITE_URL)
    
    PgSession = sessionmaker(bind=pg_engine)
    SqliteSession = sessionmaker(bind=sqlite_engine)
    
    pg_db = PgSession()
    sqlite_db = SqliteSession()
    
    try:
        # 1. Crear tablas en SQLite
        print("Creando tablas en SQLite...")
        Base.metadata.create_all(bind=sqlite_engine)
        
        # Orden de migración para respetar llaves foráneas
        models = [
            User, MetodoPagoDB, VoucherDB, ClienteDB, ConfiguracionDB, 
            HistorialAcceso, RegistroPersonaHotel, NovedadDB, 
            HabitacionDB, EstanciaDB, EstanciaHabitacion, EstanciaHuesped, 
            PagoDB, IngresoExtraDB, LogDB, TurnoDB
        ]
        
        for model in models:
            name = model.__tablename__
            print(f"Migrando tabla: {name}...", end=" ", flush=True)
            
            # Obtener datos de Postgres
            items = pg_db.query(model).all()
            total = len(items)
            
            if total == 0:
                print("Vacía.")
                continue
                
            # Limpiar tabla en SQLite antes (por si acaso)
            sqlite_db.query(model).delete()
            
            # Insertar en SQLite
            for item in items:
                # Convertir el objeto de Postgres a uno nuevo para SQLite
                data = {c.name: getattr(item, c.name) for c in item.__table__.columns}
                new_item = model(**data)
                sqlite_db.add(new_item)
            
            sqlite_db.commit()
            print(f"OK ({total} registros).")
            
        print("\n--- ¡Migración Exitosa! ---")
        print(f"Base de datos guardada en: {os.path.abspath('./esmeralda.db')}")
        
    except Exception as e:
        print(f"\nERROR durante la migración: {e}")
        sqlite_db.rollback()
    finally:
        pg_db.close()
        sqlite_db.close()

if __name__ == "__main__":
    migrate()
