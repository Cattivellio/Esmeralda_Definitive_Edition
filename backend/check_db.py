from src.infrastructure.database import engine
from sqlalchemy import inspect
import os

inspector = inspect(engine)
columns = [c['name'] for c in inspector.get_columns('estancias')]
print(f"Columns in 'estancias': {columns}")
