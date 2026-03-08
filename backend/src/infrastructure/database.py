from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Cambiamos a SQLite para la instancia local
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL or not DATABASE_URL.startswith("sqlite"):
    DATABASE_URL = "sqlite:///./esmeralda.db"

# check_same_thread=False es necesario para SQLite con FastAPI
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# OPTIMIZACIÓN: Activar modo WAL para permitir lectura/escritura simultánea
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependencia para FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
