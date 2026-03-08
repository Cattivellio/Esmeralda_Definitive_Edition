import sys
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_dir, "src"))

from infrastructure.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
tables = inspector.get_table_names()
print(f"Tables in DB: {tables}")

if "registro_persona_hotel" in tables:
    print("SUCCESS: registro_persona_hotel exists.")
else:
    print("FAILURE: registro_persona_hotel DOES NOT exist.")
    # Attempt to create
    from infrastructure.models import Base
    Base.metadata.create_all(bind=engine)
    print("Attempted to create tables.")
    tables = inspect(engine).get_table_names()
    print(f"Tables now: {tables}")
