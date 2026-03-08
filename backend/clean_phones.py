import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:cattivellio@localhost:5432/esmeralda_db"
engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    print("Iniciando limpieza de números de teléfono inválidos...")
    
    # Condición 1: Menos de 5 dígitos
    # Condición 2: Contiene caracteres no numéricos
    # Nota: Usamos ~ '^[0-9]+$' para verificar que sea puramente numérico
    query = text("""
        UPDATE clientes 
        SET telefono = NULL 
        WHERE (length(telefono) < 5 OR telefono !~ '^[0-9]+$')
        AND telefono IS NOT NULL;
    """)
    result = conn.execute(query)
    conn.commit()
    print(f"Limpieza completada. {result.rowcount} registros actualizados.")
