import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:cattivellio@localhost:5432/esmeralda_db"
engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    print("Iniciando limpieza de observaciones con historial de visitas...")
    # Buscamos las que contienen corchetes
    query = text("""
        UPDATE clientes 
        SET observaciones = NULL 
        WHERE observaciones LIKE '%[%]%';
    """)
    result = conn.execute(query)
    conn.commit()
    print(f"Limpieza completada. {result.rowcount} registros actualizados.")
