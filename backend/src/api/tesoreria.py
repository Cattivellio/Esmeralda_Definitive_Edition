from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
import os
import shutil
import uuid
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..infrastructure.database import get_db
from ..infrastructure.models import (
    TransaccionDB, MetodoPagoDB, User
)
from .schemas import TransaccionSchema, TransferenciaRequest, MetodoPagoSchema

router = APIRouter(prefix="/api/tesoreria", tags=["tesoreria"])

# Carpeta de subida
UPLOAD_DIR = "uploads/facturas"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/cuentas", response_model=List[MetodoPagoSchema])
@router.get("/metodos-pago-full", response_model=List[MetodoPagoSchema])
def get_metodos_pago_full(db: Session = Depends(get_db)):
    # In this unified model, Accounts = Payment Methods
    metodos = db.query(MetodoPagoDB).all()
    res = []
    for m in metodos:
        # Calculate balance
        ingresos = db.query(TransaccionDB).filter(
            (TransaccionDB.metodo_pago_id == m.id) & (TransaccionDB.tipo == 'Ingreso')
        ).all()
        egresos = db.query(TransaccionDB).filter(
            (TransaccionDB.metodo_pago_id == m.id) & (TransaccionDB.tipo == 'Egreso')
        ).all()
        transf_out = db.query(TransaccionDB).filter(
            (TransaccionDB.metodo_pago_id == m.id) & (TransaccionDB.tipo == 'Transferencia')
        ).all()
        transf_in = db.query(TransaccionDB).filter(
            (TransaccionDB.metodo_pago_destino_id == m.id) & (TransaccionDB.tipo == 'Transferencia')
        ).all()

        saldo = m.saldo_inicial
        saldo += sum(t.monto for t in ingresos)
        saldo -= sum(t.monto for t in egresos)
        saldo -= sum(t.monto for t in transf_out)
        saldo += sum(t.monto for t in transf_in)

        res.append({
            "id": m.id,
            "nombre": m.nombre,
            "moneda": m.moneda,
            "color": m.color,
            "activo": m.activo,
            "saldo_inicial": m.saldo_inicial,
            "saldo_actual": saldo
        })
    return res

@router.get("/transacciones", response_model=List[TransaccionSchema])
def get_transacciones(
    metodo_pago_id: Optional[int] = None,
    tipo: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(TransaccionDB)
    if metodo_pago_id:
        query = query.filter((TransaccionDB.metodo_pago_id == metodo_pago_id) | (TransaccionDB.metodo_pago_destino_id == metodo_pago_id))
    if tipo:
        query = query.filter(TransaccionDB.tipo == tipo)
    
    transacciones = query.order_by(TransaccionDB.fecha.desc()).limit(limit).all()
    
    res = []
    for t in transacciones:
        item = {
            "id": t.id,
            "tipo": t.tipo,
            "monto": t.monto,
            "moneda": t.moneda,
            "metodo_pago_id": t.metodo_pago_id,
            "metodo_pago_destino_id": t.metodo_pago_destino_id,
            "descripcion": t.descripcion,
            "justificacion": t.justificacion,
            "fecha": t.fecha,
            "usuario_id": t.usuario_id,
            "pago_id": t.pago_id,
            "extra_id": t.extra_id,
            "referencia": t.referencia,
            "metodo_pago_nombre": t.metodo_pago.nombre if t.metodo_pago else "N/A",
            "metodo_pago_destino_nombre": t.metodo_pago_destino.nombre if t.metodo_pago_destino else None
        }
        res.append(item)
    return res

@router.post("/transacciones", response_model=TransaccionSchema)
def create_transaccion(trans: TransaccionSchema, db: Session = Depends(get_db)):
    nueva = TransaccionDB(
        tipo=trans.tipo,
        monto=trans.monto,
        moneda=trans.moneda,
        metodo_pago_id=trans.metodo_pago_id,
        descripcion=trans.descripcion,
        justificacion=trans.justificacion,
        fecha=datetime.utcnow(),
        usuario_id=trans.usuario_id,
        referencia=trans.referencia,
        categoria=trans.categoria,
        factura_url=trans.factura_url
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@router.post("/upload-factura")
async def upload_factura(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"url": f"/facturas/{filename}"}

@router.post("/transferencias")
def create_transferencia(req: TransferenciaRequest, db: Session = Depends(get_db)):
    m_orig = db.query(MetodoPagoDB).filter(MetodoPagoDB.id == req.metodo_pago_origen_id).first()
    m_dest = db.query(MetodoPagoDB).filter(MetodoPagoDB.id == req.metodo_pago_destino_id).first()
    
    if not m_orig or not m_dest:
        raise HTTPException(status_code=400, detail="Métodos no válidos")
    
    trans = TransaccionDB(
        tipo='Transferencia',
        monto=req.monto,
        moneda=m_orig.moneda,
        metodo_pago_id=req.metodo_pago_origen_id,
        metodo_pago_destino_id=req.metodo_pago_destino_id,
        descripcion=req.descripcion or f"Transferencia de {m_orig.nombre} a {m_dest.nombre}",
        fecha=datetime.utcnow()
    )
    db.add(trans)
    db.commit()
    return {"status": "success"}
