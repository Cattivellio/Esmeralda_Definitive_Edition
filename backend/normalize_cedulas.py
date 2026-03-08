import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from infrastructure.models import ClienteDB

DATABASE_URL = "postgresql://postgres:cattivellio@localhost:5432/esmeralda_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Actualizar todas las cédulas que son puramente numéricas añadiendo el prefijo V-
# Pero por seguridad, lo haremos uno por uno o en pequeños bloques (aunque sean 67k)
# O mejor, una consulta SQL directa con el motor.
from sqlalchemy import text
connection = engine.connect()
print("Iniciando actualización de cédulas...")
# Identificar clientes cuya cedula es solo números
res = connection.execute(text("SELECT cedula FROM clientes WHERE cedula ~ '^[0-9]+$'"))
rows = res.fetchall()
print(f"Se encontraron {len(rows)} clientes por normalizar.")

# Para actualizar la clave primaria (cedula), debemos tener cuidado.
# Si ya existe una 'V-123' y vamos a actualizar '123' a 'V-123', fallará.
# Por lo tanto, usaremos una lógica de actualización segura.

count = 0
for row in rows:
    old_cedula = row[0]
    new_cedula = f"V-{old_cedula}"
    
    # Verificar si el destino ya existe
    exists = connection.execute(text("SELECT 1 FROM clientes WHERE cedula = :new"), {"new": new_cedula}).fetchone()
    if not exists:
        connection.execute(text("UPDATE clientes SET cedula = :new WHERE cedula = :old"), {"new": new_cedula, "old": old_cedula})
        count += 1
    else:
        # Si ya existe, tal vez deberíamos fusionar? 
        # Por ahora, simplemente eliminamos el viejo si el nuevo ya tiene datos?
        # O lo dejamos así.
        print(f"Conflicto: ya existe {new_cedula}, saltando {old_cedula}")

connection.commit()
connection.close()
print(f"Actualización completada. {count} registros actualizados.")
