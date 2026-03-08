from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from ..infrastructure.database import get_db
from ..infrastructure.models import NovedadDB
from .schemas import NovedadSchema

router = APIRouter(prefix="/api/novedades", tags=["novedades"])

from datetime import datetime, timezone
@router.get("/", response_model=List[NovedadSchema])
def get_novedades(limit: int = 100, skip: int = 0, s: Optional[str] = None, start: Optional[datetime] = None, end: Optional[datetime] = None, db: Session = Depends(get_db)):
    query = db.query(NovedadDB)
    
    if start:
        query = query.filter(NovedadDB.fecha >= start)
    if end:
        query = query.filter(NovedadDB.fecha <= end)
    
    if s:
        query = query.filter(
            (NovedadDB.texto.ilike(f"%{s}%")) | (NovedadDB.usuario.ilike(f"%{s}%"))
        )
        
    novedades = query.order_by(NovedadDB.fecha.desc()).offset(skip).limit(limit).all()
    for n in novedades:
        if n.fecha: n.fecha = n.fecha.replace(tzinfo=timezone.utc)
        if n.fecha_resolucion: n.fecha_resolucion = n.fecha_resolucion.replace(tzinfo=timezone.utc)
    return novedades

@router.post("/", response_model=NovedadSchema)
def crear_novedad(novedad: NovedadSchema, db: Session = Depends(get_db)):
    db_novedad = NovedadDB(
        texto=novedad.texto,
        tipo=novedad.tipo,
        estado=novedad.estado if novedad.tipo == "averia" else "pendiente",
        usuario=novedad.usuario
    )
    db.add(db_db_novedad := db_novedad)
    db.commit()
    db.refresh(db_db_novedad)
    if db_db_novedad.fecha: 
        db_db_novedad.fecha = db_db_novedad.fecha.replace(tzinfo=timezone.utc)
    return db_db_novedad

@router.put("/{id}/resolver", response_model=NovedadSchema)
def resolver_averia(id: int, db: Session = Depends(get_db)):
    db_novedad = db.query(NovedadDB).filter(NovedadDB.id == id).first()
    if not db_novedad:
        raise HTTPException(status_code=404, detail="Novedad no encontrada")
    
    if db_novedad.tipo != "averia":
        raise HTTPException(status_code=400, detail="Solo las averías pueden ser marcadas como arregladas")
    
    db_novedad.estado = "arreglada"
    db_novedad.fecha_resolucion = datetime.utcnow()
    db.commit()
    db.refresh(db_novedad)
    if db_novedad.fecha: 
        db_novedad.fecha = db_novedad.fecha.replace(tzinfo=timezone.utc)
    if db_novedad.fecha_resolucion: 
        db_novedad.fecha_resolucion = db_novedad.fecha_resolucion.replace(tzinfo=timezone.utc)
    return db_novedad
