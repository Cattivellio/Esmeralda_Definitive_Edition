import sys
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_dir, "src"))

from infrastructure.database import engine, Base
from sqlalchemy import text

def migrate():
    with engine.connect() as conn:
        print("Checking for missing columns...")
        try:
            conn.execute(text("ALTER TABLE usuarios ADD COLUMN nombre VARCHAR(100);"))
            conn.commit()
            print("Added 'nombre' to 'usuarios'.")
        except Exception as e:
            print(f"Note: {e}")
            
        print("Schema update attempt finished.")

if __name__ == "__main__":
    migrate()
