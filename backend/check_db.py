no quiero import sys
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_dir, "src"))

from infrastructure.database import SessionLocal, engine, Base
from infrastructure.models import HabitacionDB, User, ConfiguracionDB
from sqlalchemy import text

db = SessionLocal()
try:
    print(f"Habitaciones count: {db.query(HabitacionDB).count()}")
    print(f"Usuarios count: {db.query(User).count()}")
    print(f"Configuraciones count: {db.query(ConfiguracionDB).count()}")
except Exception as e:
    print(f"Error checking DB: {e}")
finally:
    db.close()
