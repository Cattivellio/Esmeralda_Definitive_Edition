from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..infrastructure.database import get_db
from ..infrastructure.models import RegistroPersonaHotel, User, ClienteDB, HistorialAcceso, HabitacionDB, EstanciaHuesped

router = APIRouter(prefix="/api/acceso", tags=["acceso"])

class AccesoRequest(BaseModel):
    nombre: str
    cedula: str
    cargo: str

class AccesoBatchRequest(BaseModel):
    personas: List[AccesoRequest]
    tipo: str # "entrada" o "salida"

@router.get("/cargos")
def get_cargos(db: Session = Depends(get_db)):
    # Roles de la tabla usuarios
    roles_usuarios = db.query(User.rol).distinct().all()
    roles = [r[0] for r in roles_usuarios if r[0]]
    if "Cliente" not in roles:
        roles.append("Cliente")
    return sorted(list(set(roles)))

@router.get("/cargos-resumen")
def get_cargos_resumen(db: Session = Depends(get_db)):
    usuarios = db.query(User).all()
    clientes = db.query(ClienteDB).all()
    
    cargos = {}
    for u in usuarios:
        c = u.rol
        if c not in cargos:
            cargos[c] = {"total": 0, "presentes": 0, "ausentes": 0}
        cargos[c]["total"] += 1
        
    if clientes:
        cargos["Cliente"] = {"total": len(clientes), "presentes": 0, "ausentes": 0}
        
    registros = db.query(RegistroPersonaHotel).all()
    estado_dict = {r.cedula: r.estado for r in registros}
    
    for u in usuarios:
        cedula = u.username
        estado = estado_dict.get(cedula, "ausente")
        if estado == "presente":
            cargos[u.rol]["presentes"] += 1
        else:
            cargos[u.rol]["ausentes"] += 1
            
    for c in clientes:
        cedula = c.cedula
        estado = estado_dict.get(cedula, "ausente")
        if estado == "presente":
            cargos["Cliente"]["presentes"] += 1
        else:
            cargos["Cliente"]["ausentes"] += 1
            
    resumen = [{"cargo": k, **v} for k, v in cargos.items()]
    return resumen

@router.get("/personas/{cargo}")
def get_personas_by_cargo(cargo: str, db: Session = Depends(get_db)):
    # También incluimos el estado para el frontend
    registros = db.query(RegistroPersonaHotel).all()
    estado_dict = {r.cedula: r.estado for r in registros}

    if cargo == "Cliente":
        clientes = db.query(ClienteDB).all()
        # Mapeo de habitaciones activas
        hab_mapping = {}
        # Habitaciones que tienen una estancia activa
        rooms = db.query(HabitacionDB).filter(HabitacionDB.estancia_actual_id != None).all()
        for r in rooms:
            # Huéspedes vinculados a esa estancia
            guest_links = db.query(EstanciaHuesped).filter(EstanciaHuesped.estancia_id == r.estancia_actual_id).all()
            for link in guest_links:
                hab_mapping[link.cliente_id] = r.numero
        
        return [
            {
                "nombre": f"HAB {hab_mapping[c.cedula]} | {c.nombre}" if c.cedula in hab_mapping else c.nombre, 
                "cedula": c.cedula, 
                "cargo": "Cliente", 
                "estado": estado_dict.get(c.cedula, "ausente")
            } for c in clientes
        ]
    else:
        usuarios = db.query(User).filter(User.rol == cargo).all()
        return [{"nombre": u.nombre or u.username, "cedula": u.username, "cargo": cargo, "estado": estado_dict.get(u.username, "ausente")} for u in usuarios]

@router.post("/registrar")
def registrar_acceso_batch(request: AccesoBatchRequest, db: Session = Depends(get_db)):
    resultados = []
    
    for req in request.personas:
        registro = db.query(RegistroPersonaHotel).filter(RegistroPersonaHotel.cedula == req.cedula).first()
        
        if not registro:
            registro = RegistroPersonaHotel(
                nombre=req.nombre,
                cedula=req.cedula,
                cargo=req.cargo,
                estado="ausente"
            )
            db.add(registro)
            db.commit()
            db.refresh(registro)

        if request.tipo == "entrada":
            if registro.estado == "presente":
                continue # Skip if already inside
            registro.estado = "presente"
            registro.ultima_entrada = datetime.utcnow()
        else: # salida
            if registro.estado == "ausente":
                continue # Skip if already outside
            registro.estado = "ausente"
            registro.ultima_salida = datetime.utcnow()
        
        # Log history
        historial = HistorialAcceso(
            cedula=req.cedula,
            nombre=req.nombre,
            tipo=request.tipo,
            timestamp=datetime.utcnow()
        )
        db.add(historial)
        
        resultados.append(registro.nombre)
        
    db.commit()
    return {
        "status": "success",
        "modificados": len(resultados),
        "nombres": resultados
    }

@router.get("/presentes")
def get_personas_presentes(db: Session = Depends(get_db)):
    presentes = db.query(RegistroPersonaHotel).filter(RegistroPersonaHotel.estado == "presente").all()
    return [
        {
            "id": p.id,
            "nombre": p.nombre,
            "cedula": p.cedula,
            "cargo": p.cargo,
            "estado": p.estado,
            "ultima_entrada": p.ultima_entrada.isoformat() + "Z" if p.ultima_entrada else None,
            "ultima_salida": p.ultima_salida.isoformat() + "Z" if p.ultima_salida else None
        } for p in presentes
    ]

@router.get("/historial")
def get_historial_global(limit: int = 100, skip: int = 0, s: Optional[str] = None, start: Optional[datetime] = None, end: Optional[datetime] = None, db: Session = Depends(get_db)):
    query = db.query(HistorialAcceso)
    
    if start:
        query = query.filter(HistorialAcceso.timestamp >= start)
    if end:
        query = query.filter(HistorialAcceso.timestamp <= end)
    
    if s:
        query = query.filter(
            (HistorialAcceso.nombre.ilike(f"%{s}%")) | (HistorialAcceso.cedula.ilike(f"%{s}%"))
        )
        
    historial = query.order_by(HistorialAcceso.timestamp.desc()).offset(skip).limit(limit).all()
    return [
        {
            "id": h.id,
            "cedula": h.cedula,
            "nombre": h.nombre,
            "tipo": h.tipo,
            "timestamp": h.timestamp.isoformat() + "Z" if h.timestamp else None
        } for h in historial
    ]

@router.get("/historial/{cedula}")
def get_historial_persona(cedula: str, db: Session = Depends(get_db)):
    historial = db.query(HistorialAcceso).filter(HistorialAcceso.cedula == cedula).order_by(HistorialAcceso.timestamp.desc()).all()
    return [
        {
            "id": h.id,
            "cedula": h.cedula,
            "nombre": h.nombre,
            "tipo": h.tipo,
            "timestamp": h.timestamp.isoformat() + "Z" if h.timestamp else None
        } for h in historial
    ]
