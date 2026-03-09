from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.infrastructure.database import get_db
from src.infrastructure.models import TurnoDB, User
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/api/turnos", tags=["turnos"])

class CambioTurnoRequest(BaseModel):
    usuario_entrante: str  # username of the incoming user
    usuario_saliente: str  # username of the outgoing/current user
    observaciones: Optional[str] = None

@router.post("/cambio")
def registrar_cambio_turno(req: CambioTurnoRequest, db: Session = Depends(get_db)):
    # Find the users by username
    user_in = db.query(User).filter(User.username == req.usuario_entrante).first()
    user_out = db.query(User).filter(User.username == req.usuario_saliente).first()

    if not user_in:
        raise HTTPException(status_code=404, detail="Usuario entrante no encontrado")

    # Close the current active shift if one exists
    active_shift = db.query(TurnoDB).filter(TurnoDB.fecha_fin == None).first()
    if active_shift:
        active_shift.fecha_fin = datetime.utcnow()
    
    # Create the new shift
    new_shift = TurnoDB(
        usuario_entrante_id=user_in.id,
        usuario_saliente_id=user_out.id if user_out else None,
        observaciones=req.observaciones
    )
    db.add(new_shift)
    db.commit()
    db.refresh(new_shift)

    return {"message": "Turno cambiado exitosamente", "turno_id": new_shift.id}

@router.get("/actual")
def obtener_turno_actual(db: Session = Depends(get_db)):
    active_shift = db.query(TurnoDB).filter(TurnoDB.fecha_fin == None).first()
    if not active_shift:
        return {"turno": None}
    
    user_in = active_shift.usuario_entrante.username if active_shift.usuario_entrante else None
    
    return {
        "turno": {
            "id": active_shift.id,
            "usuario_entrante": user_in,
            "fecha_inicio": active_shift.fecha_inicio
        }
    }
@router.get("/historial")
def get_historial_turnos(limit: int = 100, s: Optional[str] = None, start: Optional[datetime] = None, end: Optional[datetime] = None, db: Session = Depends(get_db)):
    query = db.query(TurnoDB)
    
    if start:
        query = query.filter(TurnoDB.fecha_inicio >= start)
    if end:
        query = query.filter(TurnoDB.fecha_inicio <= end)
    
    if s:
        # Buscar por nombre del trabajador o observaciones
        query = query.join(TurnoDB.usuario_entrante).filter(
            (User.nombre.ilike(f"%{s}%")) | (TurnoDB.observaciones.ilike(f"%{s}%"))
        )
        
    shifts = query.order_by(TurnoDB.fecha_inicio.desc()).limit(limit).all()
    
    output = []
    for s_obj in shifts:
        output.append({
            "id": s_obj.id,
            "dia": s_obj.fecha_inicio.day,
            "worker": s_obj.usuario_entrante.nombre if s_obj.usuario_entrante else "Desconocido",
            "worker_out": s_obj.usuario_saliente.nombre if s_obj.usuario_saliente else "Inicial",
            "inicio": s_obj.fecha_inicio.isoformat(),
            "fin": s_obj.fecha_fin.isoformat() if s_obj.fecha_fin else "Actual",
            "isActual": s_obj.fecha_fin is None,
            "clients": 0, # Placeholder
            "usd": 0, # Placeholder
            "bs": 0, # Placeholder
            "hosp": 0,
            "parc": 0,
            "ptoA": 0,
            "bcaribe": 0,
            "novedades": 0
        })
    return output
