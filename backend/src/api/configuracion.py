import requests
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from ..infrastructure.database import get_db
from ..infrastructure.models import (
    ConfiguracionDB, MetodoPagoDB, HabitacionDB, User, InspeccionDB
)

router = APIRouter(prefix="/api/configuracion", tags=["configuracion"])

# --- SCHEMAS ---
class ConfigUpdate(BaseModel):
    valor: str

class MetodoPagoSchema(BaseModel):
    id: Optional[int] = None
    nombre: str
    moneda: str
    color: str = "#ffffff"
    activo: bool

class HabitacionUpdate(BaseModel):
    tipo: str
    precio_parcial: float
    precio_hospedaje: float
    capacidad: int = 2
    observaciones: Optional[str] = None
    descripcion: Optional[str] = None
    nfc_code: Optional[str] = None

class UsuarioSchema(BaseModel):
    id: Optional[int] = None
    username: str # Usaremos username como cédula/identificador por ahora
    nombre: Optional[str] = None
    rol: str # Cargo/Rol

class UsuarioCreate(UsuarioSchema):
    password: str

class VoucherSchema(BaseModel):
    codigo: str
    tipo: str
    valor: float
    activo: bool

class InspeccionSchema(BaseModel):
    id: Optional[int] = None
    habitacion_id: int
    usuario_id: int
    fecha: Optional[datetime] = None
    telefono: str
    televisor: str
    aire_acondicionado: str
    luces: str
    cama: str
    ducha_agua: str
    observaciones: Optional[str] = None
    foto_url: Optional[str] = None

# --- ENDPOINTS ---

# 1. Configuraciones Globales
@router.get("/settings/{clave}")
def get_setting(clave: str, db: Session = Depends(get_db)):
    setting = db.query(ConfiguracionDB).filter(ConfiguracionDB.clave == clave).first()
    if not setting:
        # Default para horas parcial si no existe
        if clave == "horas_parcial":
            return {"clave": "horas_parcial", "valor": "6"}
        if clave == "hora_checkin":
            return {"clave": "hora_checkin", "valor": "13:00"}
        if clave == "hora_checkout":
            return {"clave": "hora_checkout", "valor": "12:00"}
        if clave == "bcv":
            return {"clave": "bcv", "valor": "0"}
        raise HTTPException(status_code=404, detail="Configuración no encontrada")
    return setting

@router.put("/settings/{clave}")
def update_setting(clave: str, request: ConfigUpdate, db: Session = Depends(get_db)):
    setting = db.query(ConfiguracionDB).filter(ConfiguracionDB.clave == clave).first()
    if not setting:
        setting = ConfiguracionDB(clave=clave, valor=request.valor)
        db.add(setting)
    else:
        setting.valor = request.valor
    db.commit()
    return {"status": "success"}

@router.post("/refresh-bcv")
def refresh_bcv_rate(db: Session = Depends(get_db)):
    url = "https://ve.dolarapi.com/v1/dolares/oficial"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        price = data.get("promedio")
        
        if not price:
             raise HTTPException(status_code=500, detail="No se pudo obtener el promedio del API.")

        # Update or create in DB
        setting = db.query(ConfiguracionDB).filter(ConfiguracionDB.clave == "bcv").first()
        if not setting:
            setting = ConfiguracionDB(clave="bcv", valor=str(price), descripcion="Tasa BCV del Dolar")
            db.add(setting)
        else:
            setting.valor = str(price)
        
        db.commit()

        return {"price": price, "status": "success"}

    except requests.exceptions.RequestException as e:
        print(f"Error BCV Sync: {e}")
        raise HTTPException(status_code=500, detail=f"No se pudo conectar con el API: {e}")
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

# 2. Métodos de Pago
@router.get("/metodos_pago", response_model=List[MetodoPagoSchema])
def get_metodos_pago(db: Session = Depends(get_db)):
    return db.query(MetodoPagoDB).all()

@router.post("/metodos_pago")
def create_metodo_pago(metodo: MetodoPagoSchema, db: Session = Depends(get_db)):
    nuevo = MetodoPagoDB(nombre=metodo.nombre, moneda=metodo.moneda, color=metodo.color, activo=metodo.activo)
    db.add(nuevo)
    db.commit()
    return {"status": "success"}

@router.put("/metodos_pago/{id}")
def update_metodo_pago(id: int, metodo: MetodoPagoSchema, db: Session = Depends(get_db)):
    db_metodo = db.query(MetodoPagoDB).filter(MetodoPagoDB.id == id).first()
    if not db_metodo:
        raise HTTPException(status_code=404, detail="Método de pago no encontrado")
    db_metodo.nombre = metodo.nombre
    db_metodo.moneda = metodo.moneda
    db_metodo.color = metodo.color
    db_metodo.activo = metodo.activo
    db.commit()
    return {"status": "success"}

@router.delete("/metodos_pago/{id}")
def delete_metodo_pago(id: int, db: Session = Depends(get_db)):
    db_metodo = db.query(MetodoPagoDB).filter(MetodoPagoDB.id == id).first()
    if not db_metodo:
        raise HTTPException(status_code=404, detail="Método de pago no encontrado")
    db.delete(db_metodo)
    db.commit()
    return {"status": "success"}

# 3. Habitaciones (Solo precios)
@router.put("/habitaciones/{id}/precios")
def update_habitacion_config(id: int, request: HabitacionUpdate, db: Session = Depends(get_db)):
    hab = db.query(HabitacionDB).filter(HabitacionDB.id == id).first()
    if not hab:
        raise HTTPException(status_code=404, detail="Habitación no encontrada")
    hab.tipo = request.tipo
    hab.precio_parcial = request.precio_parcial
    hab.precio_hospedaje = request.precio_hospedaje
    hab.capacidad = request.capacidad
    hab.observaciones = request.observaciones
    hab.descripcion = request.descripcion
    hab.nfc_code = request.nfc_code
    db.commit()
    return {"status": "success"}

# 4. CRUD Usuarios
@router.get("/usuarios", response_model=List[UsuarioSchema])
def get_usuarios(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.post("/usuarios")
def create_usuario(user: UsuarioCreate, db: Session = Depends(get_db)):
    nuevo = User(username=user.username, nombre=user.nombre, password_hash=user.password, rol=user.rol)
    # Nota: Aquí deberíamos hashear la password, pero por simplicidad en este entorno legacy seguimos el patrón actual
    db.add(nuevo)
    db.commit()
    return {"status": "success"}

@router.put("/usuarios/{id}")
def update_usuario(id: int, user: UsuarioSchema, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db_user.username = user.username
    db_user.nombre = user.nombre
    db_user.rol = user.rol
    db.commit()
    return {"status": "success"}

@router.delete("/usuarios/{id}")
def delete_usuario(id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(db_user)
    db.commit()
    return {"status": "success"}

# 5. Vouchers
@router.get("/vouchers/{codigo}", response_model=VoucherSchema)
def get_voucher(codigo: str, db: Session = Depends(get_db)):
    from ..infrastructure.models import VoucherDB
    v = db.query(VoucherDB).filter(VoucherDB.codigo == codigo, VoucherDB.activo == True).first()
    if not v:
        raise HTTPException(status_code=404, detail="Cupón no válido o inactivo")
    return v

# 6. Inspecciones
@router.get("/inspecciones")
def get_inspecciones(db: Session = Depends(get_db)):
    from sqlalchemy import func
    # Obtenemos la última inspección por habitación
    subquery = db.query(
        InspeccionDB.habitacion_id,
        func.max(InspeccionDB.fecha).label('max_fecha')
    ).group_by(InspeccionDB.habitacion_id).subquery()

    inspecciones = db.query(InspeccionDB).join(
        subquery,
        (InspeccionDB.habitacion_id == subquery.c.habitacion_id) &
        (InspeccionDB.fecha == subquery.c.max_fecha)
    ).all()
    
    res = []
    for ins in inspecciones:
        res.append({
            "id": ins.id,
            "habitacion_numero": ins.habitacion.numero,
            "inspector_nombre": ins.usuario.nombre or ins.usuario.username,
            "fecha": ins.fecha,
            "telefono": ins.telefono,
            "televisor": ins.televisor,
            "aire_acondicionado": ins.aire_acondicionado,
            "luces": ins.luces,
            "cama": ins.cama,
            "ducha_agua": ins.ducha_agua,
            "observaciones": ins.observaciones,
            "foto_url": ins.foto_url
        })
    return res

@router.post("/inspecciones")
def create_inspeccion(req: InspeccionSchema, db: Session = Depends(get_db)):
    nueva = InspeccionDB(
        habitacion_id=req.habitacion_id,
        usuario_id=req.usuario_id,
        fecha=datetime.utcnow(),
        telefono=req.telefono,
        televisor=req.televisor,
        aire_acondicionado=req.aire_acondicionado,
        luces=req.luces,
        cama=req.cama,
        ducha_agua=req.ducha_agua,
        observaciones=req.observaciones,
        foto_url=req.foto_url
    )
    db.add(nueva)
    db.commit()
    return {"status": "success"}
