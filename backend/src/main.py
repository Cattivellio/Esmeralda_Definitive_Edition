from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .infrastructure.database import engine, Base, SessionLocal
from .infrastructure import models
from .infrastructure.models import ConfiguracionDB, User
from src.api import habitaciones, clientes, configuracion, acceso, turnos, novedades

# Crear tablas en base de datos si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Esmeralda Backend API")

@app.on_event("startup")
def startup_event():
    # Inicialización rápida
    with SessionLocal() as db:
        try:
            # 1. Resetear tasa
            bcv = db.query(ConfiguracionDB).filter(ConfiguracionDB.clave == "bcv").first()
            if not bcv:
                db.add(ConfiguracionDB(clave="bcv", valor="0", descripcion="Tasa BCV"))
            else:
                bcv.valor = "0"
            db.commit()
            print("BCV reset to 0")
        except Exception as e:
            print(f"Startup warning: {e}")

# Configurar CORS para permitir que Next.js consuma la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar Routers
app.include_router(habitaciones.router)
app.include_router(clientes.router)
app.include_router(configuracion.router)
app.include_router(acceso.router)
app.include_router(turnos.router)
app.include_router(novedades.router)

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API del Sistema Esmeralda"}
# Force reload trigger
