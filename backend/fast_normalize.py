import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:cattivellio@localhost:5432/esmeralda_db"
engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    print("Iniciando actualización masiva de cédulas...")
    query = text("""
        UPDATE clientes 
        SET cedula = 'V-' || clientes.cedula 
        WHERE clientes.cedula ~ '^[0-9]+$' 
        AND NOT EXISTS (
            SELECT 1 FROM clientes c2 
            WHERE c2.cedula = 'V-' || clientes.cedula
        );
    """)
    result = conn.execute(query)
    conn.commit()
    print(f"Actualización completada. {result.rowcount} registros normalizados.")
