import enum
import uuid
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey, Boolean, Text
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# Decorador para manejar UUIDs como String en SQLite de forma transparente
class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses CHAR(32), storing as string without dashes.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            from sqlalchemy.dialects import postgresql
            return dialect.type_descriptor(postgresql.UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value


class Reputacion(str, enum.Enum):
    positivo = "positivo"
    negativo = "negativo"

class EstadoHabitacion(str, enum.Enum):
    libre = "libre"
    ocupada_parcial = "ocupada_parcial"
    ocupada_hospedaje = "ocupada_hospedaje"
    sucia = "sucia"
    mantenimiento = "mantenimiento"
    bloqueada = "bloqueada"
    retoque = "retoque"

class EstadoEstancia(str, enum.Enum):
    activa = "activa"
    finalizada = "finalizada"
    cancelada = "cancelada"
    reservada = "reservada"

class User(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    nombre = Column(String(100))
    password_hash = Column(String(255), nullable=False)
    rol = Column(String(50), default="Recepcionista") # Administrador, Recepcionista, etc
    horario = Column(String(100), nullable=True) # Ej. 08:00 - 16:00
    is_present = Column(Boolean, default=False)
    fecha_nacimiento = Column(DateTime, nullable=True)
    fecha_ingreso = Column(DateTime, nullable=True)
    foto_url = Column(String(255), nullable=True)
    nfc_code = Column(String(50), unique=True, nullable=True)

class HabitacionDB(Base):
    __tablename__ = "habitaciones"
    id = Column(Integer, primary_key=True)
    numero = Column(String(10), unique=True, nullable=False)
    tipo = Column(String(50), nullable=False) # mat, dob, etc
    precio_parcial = Column(Float, default=0.0)
    precio_hospedaje = Column(Float, default=0.0)
    estado = Column(Enum(EstadoHabitacion), default=EstadoHabitacion.libre)
    pos_x = Column(Integer)
    pos_y = Column(Integer)
    razon_bloqueo = Column(Text, nullable=True)
    observaciones = Column(Text, nullable=True)
    descripcion = Column(Text, nullable=True)
    amenities = Column(Text, nullable=True)
    capacidad = Column(Integer, default=2)
    nfc_code = Column(String(50), nullable=True)
    
    estancia_actual_id = Column(GUID(), ForeignKey("estancias.id"), nullable=True)
    
    # Relación para historial
    habitacion_estancias = relationship("EstanciaHabitacion", back_populates="habitacion")

class ClienteDB(Base):
    __tablename__ = "clientes"
    cedula = Column(String(20), primary_key=True)
    nombre = Column(String(100), nullable=False)
    fecha_nacimiento = Column(DateTime)
    nacionalidad = Column(String(50))
    estado_civil = Column(String(50))
    direccion = Column(String(255))
    telefono = Column(String(20))
    profesion = Column(String(100))
    reputacion = Column(Enum(Reputacion), default=Reputacion.positivo)
    observaciones = Column(Text)

class EstanciaDB(Base):
    __tablename__ = "estancias"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    cliente_principal_id = Column(String(20), ForeignKey("clientes.cedula"))
    tipo_estadia = Column(String(50)) # parcial, hospedaje
    fecha_entrada = Column(DateTime, default=datetime.utcnow)
    fecha_salida_planificada = Column(DateTime)
    fecha_salida_real = Column(DateTime)
    estado = Column(Enum(EstadoEstancia), default=EstadoEstancia.reservada)
    voucher_id = Column(Integer, ForeignKey("vouchers.id"), nullable=True)
    procedencia = Column(String(100))
    destino = Column(String(100))
    observaciones = Column(Text)
    usuario_creacion_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    camarera_checkout_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    pagos = relationship("PagoDB", back_populates="estancia")
    extras = relationship("IngresoExtraDB", back_populates="estancia")
    huespedes = relationship("EstanciaHuesped", back_populates="estancia")
    movimientos_habitacion = relationship("EstanciaHabitacion", back_populates="estancia")

class EstanciaHabitacion(Base):
    __tablename__ = "estancia_habitaciones"
    id = Column(Integer, primary_key=True)
    estancia_id = Column(GUID(), ForeignKey("estancias.id"))
    habitacion_id = Column(Integer, ForeignKey("habitaciones.id"))
    fecha_inicio = Column(DateTime, default=datetime.utcnow)
    fecha_fin = Column(DateTime) # Null if current

    estancia = relationship("EstanciaDB", back_populates="movimientos_habitacion")
    habitacion = relationship("HabitacionDB", back_populates="habitacion_estancias")

class EstanciaHuesped(Base):
    __tablename__ = "estancia_huespedes"
    id = Column(Integer, primary_key=True)
    estancia_id = Column(GUID(), ForeignKey("estancias.id"))
    cliente_id = Column(String(20), ForeignKey("clientes.cedula"))

    estancia = relationship("EstanciaDB", back_populates="huespedes")

class MetodoPagoDB(Base):
    __tablename__ = "metodos_pago"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False) # Dólar Efvo, Zelle, etc
    moneda = Column(String(10), default="USD") # USD, VES
    color = Column(String(7), default="#ffffff")
    activo = Column(Boolean, default=True)
    saldo_inicial = Column(Float, default=0.0)

    transacciones = relationship("TransaccionDB", foreign_keys="TransaccionDB.metodo_pago_id", back_populates="metodo_pago")

class TransaccionDB(Base):
    __tablename__ = "transacciones"
    id = Column(Integer, primary_key=True)
    tipo = Column(String(20), nullable=False) # Ingreso, Egreso, Transferencia
    monto = Column(Float, nullable=False)
    moneda = Column(String(10), default="USD")
    metodo_pago_id = Column(Integer, ForeignKey("metodos_pago.id"), nullable=False)
    metodo_pago_destino_id = Column(Integer, ForeignKey("metodos_pago.id"), nullable=True) # Solo para transferencia
    descripcion = Column(String(255))
    justificacion = Column(Text, nullable=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    pago_id = Column(Integer, ForeignKey("pagos.id"), nullable=True)
    extra_id = Column(Integer, ForeignKey("ingresos_extras.id"), nullable=True)
    referencia = Column(String(100), nullable=True)
    categoria = Column(String(50), nullable=True) # Solo para Egresos (Servicios, Suministros, etc.)
    factura_url = Column(String(255), nullable=True) # Ruta a la foto de la factura

    metodo_pago = relationship("MetodoPagoDB", foreign_keys=[metodo_pago_id], back_populates="transacciones")
    metodo_pago_destino = relationship("MetodoPagoDB", foreign_keys=[metodo_pago_destino_id])
    usuario = relationship("User")
    pago = relationship("PagoDB")
    extra = relationship("IngresoExtraDB")

class VoucherDB(Base):
    __tablename__ = "vouchers"
    id = Column(Integer, primary_key=True)
    codigo = Column(String(50), unique=True)
    tipo = Column(String(20)) # monto, porcentaje
    valor = Column(Float)
    activo = Column(Boolean, default=True)

class PagoDB(Base):
    __tablename__ = "pagos"
    id = Column(Integer, primary_key=True)
    estancia_id = Column(GUID(), ForeignKey("estancias.id"))
    metodo_pago_id = Column(Integer, ForeignKey("metodos_pago.id"))
    monto = Column(Float, nullable=False)
    referencia = Column(String(100))
    fecha = Column(DateTime, default=datetime.utcnow)

    estancia = relationship("EstanciaDB", back_populates="pagos")

class IngresoExtraDB(Base):
    __tablename__ = "ingresos_extras"
    id = Column(Integer, primary_key=True)
    estancia_id = Column(GUID(), ForeignKey("estancias.id"))
    descripcion = Column(String(255))
    monto = Column(Float, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)

    estancia = relationship("EstanciaDB", back_populates="extras")

class LogDB(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    accion = Column(String(50)) # Login, Egreso, etc
    descripcion = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

class ConfiguracionDB(Base):
    __tablename__ = "configuraciones"
    clave = Column(String(50), primary_key=True)
    valor = Column(String(255), nullable=False)
    descripcion = Column(String(255))

class TurnoDB(Base):
    __tablename__ = "turnos"
    id = Column(Integer, primary_key=True)
    usuario_entrante_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario_saliente_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    fecha_inicio = Column(DateTime, default=datetime.utcnow)
    fecha_fin = Column(DateTime, nullable=True)
    observaciones = Column(Text, nullable=True)

    usuario_entrante = relationship("User", foreign_keys=[usuario_entrante_id])
    usuario_saliente = relationship("User", foreign_keys=[usuario_saliente_id])

class HistorialAcceso(Base):
    __tablename__ = "historial_acceso"
    id = Column(Integer, primary_key=True)
    cedula = Column(String(20), nullable=False)
    nombre = Column(String(100), nullable=False)
    tipo = Column(String(10), nullable=False) # entrada / salida
    timestamp = Column(DateTime, default=datetime.utcnow)

class RegistroPersonaHotel(Base):
    __tablename__ = "registro_persona_hotel"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    cedula = Column(String(20), unique=True, nullable=False)
    cargo = Column(String(50), nullable=False)
    estado = Column(String(20), default="ausente") # presente, ausente
    ultima_entrada = Column(DateTime)
    ultima_salida = Column(DateTime)

class NovedadDB(Base):
    __tablename__ = "novedades"
    id = Column(Integer, primary_key=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    texto = Column(Text, nullable=False)
    tipo = Column(String(20), default="novedad") # novedad, averia
    estado = Column(String(20), default="pendiente") # pendiente, arreglada (para averias)
    usuario = Column(String(50))
    fecha_resolucion = Column(DateTime, nullable=True)

class InspeccionDB(Base):
    __tablename__ = "inspecciones"
    id = Column(Integer, primary_key=True, index=True)
    habitacion_id = Column(Integer, ForeignKey("habitaciones.id"))
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    fecha = Column(DateTime, default=datetime.utcnow)
    telefono = Column(String(10))
    televisor = Column(String(10))
    aire_acondicionado = Column(String(10))
    luces = Column(String(10))
    cama = Column(String(10))
    ducha_agua = Column(String(10))
    observaciones = Column(Text, nullable=True)
    foto_url = Column(String(255), nullable=True)

    habitacion = relationship("HabitacionDB")
    usuario = relationship("User")

class InventarioDB(Base):
    __tablename__ = "inventario"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    categoria = Column(String(50), nullable=False) # Amenities, Limpieza, Mantenimiento, etc.
    stock_actual = Column(Integer, default=0)
    stock_minimo = Column(Integer, default=5)
    unidad_medida = Column(String(20), default="unidades")
    costo_unitario = Column(Float, default=0.0)
    ultima_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MovimientoInventarioDB(Base):
    __tablename__ = "movimientos_inventario"
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("inventario.id"))
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    cantidad = Column(Integer, nullable=False)
    tipo = Column(String(20), nullable=False) # ENTRADA, SALIDA, AJUSTE
    motivo = Column(String(255), nullable=True)
    fecha = Column(DateTime, default=datetime.utcnow)

    item = relationship("InventarioDB")
    usuario = relationship("User")
