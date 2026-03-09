from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ClienteSchema(BaseModel):
    cedula: str
    nombre: str
    fecha_nacimiento: Optional[datetime] = None
    nacionalidad: Optional[str] = None
    estado_civil: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    profesion: Optional[str] = None
    tipo_cedula: Optional[str] = "V-"
    codigo_telefono: Optional[str] = "+58"
    reputacion: str = "positivo"
    observaciones: Optional[str] = ""
    visitas: Optional[int] = 0
    estado: Optional[str] = "ausente"

class PagoSchema(BaseModel):
    metodo: str
    monto: float
    referencia: Optional[str] = ""

class ExtraSchema(BaseModel):
    descripcion: str
    monto: float

class MetodoPagoSchema(BaseModel):
    id: Optional[int] = None
    nombre: str
    moneda: str
    color: str = "#ffffff"
    activo: bool = True
    saldo_inicial: float = 0.0
    saldo_actual: Optional[float] = 0.0

    class Config:
        from_attributes = True

class CambiarHabitacionRequest(BaseModel):
    nueva_habitacion_id: int
    motivo: str

class IngresoRequest(BaseModel):
    huespedes: List[ClienteSchema]
    tipo_estadia: str # parcial, hospedaje
    fecha_entrada: datetime
    fecha_salida_planificada: datetime
    pagos: List[PagoSchema]
    extras: List[ExtraSchema]
    procedencia: Optional[str] = None
    destino: Optional[str] = None
    observaciones_transaccion: Optional[str] = ""
    codigo_descuento: Optional[str] = None
    usuario_id: Optional[int] = None

class ReservaResponse(BaseModel):
    id: str
    habitacion_numero: str
    cliente_nombre: str
    fecha_entrada: datetime
    fecha_salida: datetime
    tipo_estadia: str
    monto_pagado: float
    monto_total: float
    metodo_pago: str
    usuario_creacion: str
    fecha_creacion: datetime
    observaciones: Optional[str] = ""

class EstanciaDetalleResponse(BaseModel):
    id: str
    cliente_principal_id: str
    tipo_estadia: str
    fecha_entrada: datetime
    fecha_salida_planificada: Optional[datetime] = None
    procedencia: Optional[str] = None
    destino: Optional[str] = None
    observaciones: Optional[str] = None
    huespedes: List[ClienteSchema]
    pagos: List[PagoSchema]
    extras: List[ExtraSchema]
    voucher_codigo: Optional[str] = None
    costo_dolar_base: float = 0.0

class BloquearRequest(BaseModel):
    motivo: str
    nueva_habitacion_id: Optional[int] = None

class RetoqueRequest(BaseModel):
    camarera_id: int

class LimpiarRequest(BaseModel):
    camarera_id: int

class NovedadSchema(BaseModel):
    id: Optional[int] = None
    fecha: Optional[datetime] = None
    texto: str
    tipo: str # novedad, averia
    estado: Optional[str] = "pendiente"
    usuario: Optional[str] = None
    fecha_resolucion: Optional[datetime] = None

    class Config:
        from_attributes = True

class TransaccionSchema(BaseModel):
    id: Optional[int] = None
    tipo: str # Ingreso, Egreso, Transferencia
    monto: float
    moneda: str
    metodo_pago_id: int
    metodo_pago_destino_id: Optional[int] = None
    descripcion: Optional[str] = None
    justificacion: Optional[str] = None
    fecha: Optional[datetime] = None
    usuario_id: Optional[int] = None
    pago_id: Optional[int] = None
    extra_id: Optional[int] = None
    referencia: Optional[str] = None
    categoria: Optional[str] = None
    factura_url: Optional[str] = None
    metodo_pago_nombre: Optional[str] = None
    metodo_pago_destino_nombre: Optional[str] = None

    class Config:
        from_attributes = True

class TransferenciaRequest(BaseModel):
    metodo_pago_origen_id: int
    metodo_pago_destino_id: int
    monto: float
    descripcion: Optional[str] = None
