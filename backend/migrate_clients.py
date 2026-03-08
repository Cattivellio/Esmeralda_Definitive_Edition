import json
import os
import sys
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Añadir el directorio src al path para poder importar los modelos
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from infrastructure.models import ClienteDB, Reputacion, Base

def migrate():
    # Cargar .env
    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        DATABASE_URL = "postgresql://postgres:cattivellio@localhost:5432/esmeralda_db"
    
    print(f"Conectando a {DATABASE_URL}...")
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    json_path = r"C:\Users\walter\Downloads\clientes_202603072127.json"
    
    if not os.path.exists(json_path):
        print(f"Error: No se encontró el archivo en {json_path}")
        return

    print(f"Leyendo archivo {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    clientes = data.get("clientes", [])
    total = len(clientes)
    print(f"Se encontraron {total} clientes para migrar.")

    count = 0
    errors = 0
    
    for i, item in enumerate(clientes):
        cedula = str(item.get("cedula")).strip()
        if not cedula:
            continue
        
        # Normalizar: si es solo números, asumimos V-
        if cedula.isdigit():
            cedula = f"V-{cedula}"
            
        try:
            # Buscar si ya existe
            existing = db.query(ClienteDB).filter(ClienteDB.cedula == cedula).first()
            
            # Formatear fecha si existe
            fecha_nac = item.get("fecha_nacimiento")
            if fecha_nac:
                try:
                    fecha_nac = datetime.strptime(fecha_nac, "%Y-%m-%d")
                except:
                    fecha_nac = None
            else:
                fecha_nac = None
            
            # Mapear reputación
            reputacion_val = item.get("reputacion", "positivo")
            if reputacion_val not in ["positivo", "negativo"]:
                reputacion_val = "positivo"
            
            # Limpiar observaciones si tienen el formato [Visitas previas: X]
            obs = item.get("observaciones")
            if obs and "[" in obs and "]" in obs:
                obs = None

            # Validar teléfono
            telefono_raw = str(item.get("telefono")).strip()
            if len(telefono_raw) < 5 or not telefono_raw.isdigit():
                telefono_val = None
            else:
                telefono_val = telefono_raw

            if existing:
                # Actualizar
                existing.nombre = item.get("nombre")
                existing.fecha_nacimiento = fecha_nac
                existing.nacionalidad = item.get("nacionalidad")
                existing.estado_civil = item.get("estado_civil")
                existing.direccion = item.get("direccion")
                existing.telefono = telefono_val
                existing.profesion = item.get("profesion")
                existing.reputacion = reputacion_val
                existing.observaciones = obs
            else:
                # Crear nuevo
                nuevo = ClienteDB(
                    cedula=cedula,
                    nombre=item.get("nombre"),
                    fecha_nacimiento=fecha_nac,
                    nacionalidad=item.get("nacionalidad"),
                    estado_civil=item.get("estado_civil"),
                    direccion=item.get("direccion"),
                    telefono=telefono_val,
                    profesion=item.get("profesion"),
                    reputacion=reputacion_val,
                    observaciones=obs
                )
                db.add(nuevo)
            
            count += 1
            if count % 100 == 0:
                db.commit()
                print(f"Procesados {count}/{total}...")
                
        except Exception as e:
            print(f"Error procesando cédula {cedula}: {e}")
            errors += 1
            db.rollback()

    db.commit()
    db.close()
    print(f"Migración completada. {count} exitosos, {errors} errores.")

if __name__ == "__main__":
    migrate()
