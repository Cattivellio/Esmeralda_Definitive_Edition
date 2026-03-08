from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..infrastructure.database import get_db
from ..infrastructure.models import ClienteDB, EstanciaHuesped, EstanciaDB, EstanciaHabitacion, HabitacionDB, RegistroPersonaHotel
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter(prefix="/api/clientes", tags=["clientes"])

class ClienteResponse(BaseModel):
    cedula: str
    tipo_cedula: str = "V-"
    nombre: str
    fecha_nacimiento: Optional[str] = None
    nacionalidad: Optional[str] = None
    estado_civil: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    codigo_telefono: str = "+58"
    profesion: Optional[str] = None
    observaciones: Optional[str] = None
    reputacion: str
    visitas: int
    estado: str = "ausente"
    ultima_entrada: Optional[str] = None
    ultima_salida: Optional[str] = None

@router.get("/{cedula}", response_model=ClienteResponse)
def get_cliente(cedula: str, db: Session = Depends(get_db)):
    cliente = db.query(ClienteDB).filter(ClienteDB.cedula == cedula).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Contar visitas
    visitas = db.query(EstanciaHuesped).filter(EstanciaHuesped.cliente_id == cedula).count()
    
    # Obtener estado de RegistroPersonaHotel
    registro = db.query(RegistroPersonaHotel).filter(RegistroPersonaHotel.cedula == cedula.strip()).first()
    estado = "ausente"
    ultima_entrada = None
    ultima_salida = None
    if registro:
        estado = registro.estado
        ultima_entrada = registro.ultima_entrada.isoformat() + "Z" if registro.ultima_entrada else None
        ultima_salida = registro.ultima_salida.isoformat() + "Z" if registro.ultima_salida else None

    # Separar tipo de cédula
    tipo = "V-"
    cedula_num = cliente.cedula
    for pref in ["V-", "E-", "J-", "G-", "P-"]:
        if cliente.cedula.startswith(pref):
            tipo = pref
            cedula_num = cliente.cedula[len(pref):]
            break
    
    # Separar código de teléfono
    cod_tel = "+58"
    tel_num = cliente.telefono or ""
    for pref in ["+58", "+1", "+57", "+34", "+54"]:
        if tel_num.startswith(pref):
            cod_tel = pref
            tel_num = tel_num[len(pref):]
            break

    return ClienteResponse(
        cedula=cedula_num,
        tipo_cedula=tipo,
        nombre=cliente.nombre,
        fecha_nacimiento=cliente.fecha_nacimiento.date().isoformat() if cliente.fecha_nacimiento else None,
        nacionalidad=cliente.nacionalidad,
        estado_civil=cliente.estado_civil,
        direccion=cliente.direccion,
        telefono=tel_num,
        codigo_telefono=cod_tel,
        profesion=cliente.profesion,
        observaciones=cliente.observaciones,
        reputacion=cliente.reputacion.value if hasattr(cliente.reputacion, 'value') else cliente.reputacion,
        visitas=visitas,
        estado=estado,
        ultima_entrada=ultima_entrada,
        ultima_salida=ultima_salida
    )

class ReputacionUpdate(BaseModel):
    reputacion: str

@router.patch("/{cedula}/reputacion")
def update_reputacion(cedula: str, request: ReputacionUpdate, db: Session = Depends(get_db)):
    cliente = db.query(ClienteDB).filter(ClienteDB.cedula == cedula).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    cliente.reputacion = request.reputacion
    db.commit()
    return {"status": "success", "reputacion": cliente.reputacion}

class EstanciaHistorialResponse(BaseModel):
    id: str
    fecha_entrada: str
    fecha_salida: Optional[str] = None
    tipo_estadia: str
    habitacion: str
    procedencia: Optional[str] = None
    destino: Optional[str] = None
    pagos: dict[str, float] = {}

@router.get("/{cedula}/historial", response_model=List[EstanciaHistorialResponse])
def get_historial_cliente(cedula: str, db: Session = Depends(get_db)):
    from ..infrastructure.models import PagoDB, MetodoPagoDB
    # Buscar todas las estancias donde participó el cliente
    estancias_huesped = db.query(EstanciaHuesped).filter(EstanciaHuesped.cliente_id == cedula).all()
    estancia_ids = [eh.estancia_id for eh in estancias_huesped]
    
    if not estancia_ids:
        return []
    
    # Obtener detalles de las estancias
    estancias = db.query(EstanciaDB).filter(EstanciaDB.id.in_(estancia_ids)).order_by(EstanciaDB.fecha_entrada.desc()).all()
    
    historial = []
    for e in estancias:
        # Buscar la habitación (o la última habitación si hubo cambios)
        movimiento = db.query(EstanciaHabitacion).filter(EstanciaHabitacion.estancia_id == e.id).order_by(EstanciaHabitacion.fecha_inicio.desc()).first()
        habitacion_num = "N/A"
        if movimiento:
            hab = db.query(HabitacionDB).filter(HabitacionDB.id == movimiento.habitacion_id).first()
            if hab:
                habitacion_num = hab.numero
        
        # Obtener pagos de esta estancia
        pagos_db = db.query(PagoDB).filter(PagoDB.estancia_id == e.id).all()
        pagos_map = {}
        for p in pagos_db:
            metodo = db.query(MetodoPagoDB).filter(MetodoPagoDB.id == p.metodo_pago_id).first()
            if metodo:
                nombre_metodo = metodo.nombre
                pagos_map[nombre_metodo] = pagos_map.get(nombre_metodo, 0.0) + p.monto

        historial.append(EstanciaHistorialResponse(
            id=str(e.id),
            fecha_entrada=e.fecha_entrada.isoformat() + "Z",
            fecha_salida=e.fecha_salida_real.isoformat() + "Z" if e.fecha_salida_real else None,
            tipo_estadia=e.tipo_estadia,
            habitacion=habitacion_num,
            procedencia=e.procedencia,
            destino=e.destino,
            pagos=pagos_map
        ))
    
    return historial

@router.get("/{cedula}/datos-pasados")
def get_datos_pasados_cliente(cedula: str, db: Session = Depends(get_db)):
    from ..infrastructure.models import PagoDB, MetodoPagoDB
    # Buscar la última estancia donde participó el cliente
    estancia_huesped = db.query(EstanciaHuesped).filter(EstanciaHuesped.cliente_id == cedula).join(EstanciaDB).order_by(EstanciaDB.fecha_entrada.desc()).first()
    
    if not estancia_huesped:
        return {"metodo": None, "procedencia": None, "destino": None}
    
    estancia = db.query(EstanciaDB).filter(EstanciaDB.id == estancia_huesped.estancia_id).first()
    
    # Obtener el último pago de esa estancia
    pago = db.query(PagoDB).filter(PagoDB.estancia_id == estancia_huesped.estancia_id).order_by(PagoDB.id.desc()).first()
    
    metodo_nombre = None
    if pago:
        metodo = db.query(MetodoPagoDB).filter(MetodoPagoDB.id == pago.metodo_pago_id).first()
        metodo_nombre = metodo.nombre if metodo else None
        
    return {
        "metodo": metodo_nombre,
        "procedencia": estancia.procedencia if estancia else None,
        "destino": estancia.destino if estancia else None
    }

@router.get("/find/search")
def buscar_clientes(query: str, db: Session = Depends(get_db)):
    # Buscar por cedula o nombre
    from sqlalchemy import or_
    results = db.query(ClienteDB).filter(
        or_(
            ClienteDB.cedula.ilike(f"%{query}%"),
            ClienteDB.nombre.ilike(f"%{query}%")
        )
    ).limit(100).all()
    
    return [
        {
            "cedula": c.cedula,
            "nombre": c.nombre,
            "nacionalidad": c.nacionalidad,
            "reputacion": c.reputacion,
            "profesion": c.profesion,
            "estado_civil": c.estado_civil,
            "direccion": c.direccion
        } for c in results
    ]
