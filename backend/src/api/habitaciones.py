from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session
from ..domain.habitacion import Habitacion
from ..infrastructure.database import get_db
from ..infrastructure.models import (
    HabitacionDB, ClienteDB, EstanciaDB, EstanciaHabitacion, 
    PagoDB, MetodoPagoDB, IngresoExtraDB, EstadoHabitacion, 
    EstadoEstancia, EstanciaHuesped, VoucherDB, RegistroPersonaHotel, HistorialAcceso, User, LogDB
)
from .schemas import (
    IngresoRequest, EstanciaDetalleResponse, CambiarHabitacionRequest, 
    BloquearRequest, RetoqueRequest, LimpiarRequest, ReservaResponse
)
import uuid
from datetime import datetime, timedelta, time, timezone

router = APIRouter(prefix="/api/habitaciones", tags=["habitaciones"])

@router.get("/", response_model=List[Habitacion])
def get_habitaciones(db: Session = Depends(get_db)):
    # Consultar todas las habitaciones de la base de datos
    db_habitaciones = db.query(HabitacionDB).all()
    
    # Consultar estancias activas para mapear la hora de salida
    from ..infrastructure.models import EstanciaDB, EstadoEstancia
    estancias_activas = db.query(EstanciaDB).filter(EstanciaDB.estado == EstadoEstancia.activa).all()
    estancias_dict = {e.id: e for e in estancias_activas}
    
    # Ordenar: primero números (ordenados por valor entero), luego letras/otros
    def room_sort_key(h):
        if h.numero.isdigit():
            return (0, int(h.numero))
        return (1, h.numero)
    
    db_habitaciones.sort(key=room_sort_key)
    
    # Mapear de modelo DB a modelo Pydantic del Dominio
    habitaciones = []
    for h in db_habitaciones:
        # Convertir estado_db (ej: ocupada_hospedaje) a formato visual (Hospedaje)
        estado_map = {
            "libre": "Libre",
            "ocupada_hospedaje": "Hospedaje",
            "ocupada_parcial": "Parcial",
            "sucia": "Sucia",
            "mantenimiento": "Mantenimiento",
            "bloqueada": "Bloqueada",
            "retoque": "Retoque"
        }
        
        hora_salida_iso = None
        if h.estancia_actual_id and h.estancia_actual_id in estancias_dict:
            est = estancias_dict[h.estancia_actual_id]
            if est.fecha_salida_planificada:
                hora_salida_iso = est.fecha_salida_planificada.isoformat() + "Z"

        habitaciones.append(Habitacion(
            id=h.id,
            numero=h.numero,
            tipo=h.tipo,
            precio_parcial=h.precio_parcial,
            precio_hospedaje=h.precio_hospedaje,
            estado_actual=estado_map.get(h.estado.value if hasattr(h.estado, 'value') else h.estado, "Libre"),
            pos_x=h.pos_x,
            pos_y=h.pos_y,
            razon_bloqueo=h.razon_bloqueo,
            observaciones=h.observaciones,
            descripcion=h.descripcion,
            amenities=h.amenities,
            capacidad=h.capacidad,
            nfc_code=h.nfc_code,
            hora_salida=hora_salida_iso 
        ))
        
    return habitaciones

def check_overlap(db: Session, habitacion_id: int, start: datetime, end: datetime, exclude_estancia_id=None):
    """Verifica si hay solapamiento de estancias o reservas. Olguura de 1 hora."""
    from sqlalchemy import or_, and_
    
    # Convertir a naive UTC si son aware
    if start.tzinfo:
        start = start.astimezone(timezone.utc).replace(tzinfo=None)
    if end.tzinfo:
        end = end.astimezone(timezone.utc).replace(tzinfo=None)

    # Margen de 1 hora (60 minutos)
    buffer = timedelta(hours=1)
    buffered_start = start - buffer
    buffered_end = end + buffer
    
    query = db.query(EstanciaDB).join(EstanciaHabitacion).filter(
        and_(
            EstanciaHabitacion.habitacion_id == habitacion_id,
            EstanciaDB.estado.in_([EstadoEstancia.activa, EstadoEstancia.reservada])
        )
    )
    
    if exclude_estancia_id:
        query = query.filter(EstanciaDB.id != exclude_estancia_id)
        
    overlaps = query.filter(
        or_(
            and_(EstanciaDB.fecha_entrada <= buffered_start, EstanciaDB.fecha_salida_planificada > buffered_start),
            and_(EstanciaDB.fecha_entrada < buffered_end, EstanciaDB.fecha_salida_planificada >= buffered_end),
            and_(EstanciaDB.fecha_entrada >= buffered_start, EstanciaDB.fecha_salida_planificada <= buffered_end)
        )
    ).first()
    
    return overlaps

@router.post("/{id}/ingresar")
def ingresar_cliente(id: int, request: IngresoRequest, db: Session = Depends(get_db)):
    # 1. Verificar que la habitación existe y está libre
    habitacion = db.query(HabitacionDB).filter(HabitacionDB.id == id).first()
    if not habitacion:
        raise HTTPException(status_code=404, detail="Habitación no encontrada")
    
    # 1.5 Verificar conflictos
    # Si es ingreso inmediato (fecha_entrada <= ahora + 5 min), verificar que esté libre visualmente
    ahora = datetime.utcnow()
    # Asegurar que request.fecha_entrada sea naive para la comparacion
    f_entrada = request.fecha_entrada
    if f_entrada.tzinfo:
        f_entrada = f_entrada.astimezone(timezone.utc).replace(tzinfo=None)
    
    # También normalizar la salida planificada
    f_salida = request.fecha_salida_planificada
    if f_salida.tzinfo:
        f_salida = f_salida.astimezone(timezone.utc).replace(tzinfo=None)

    es_inmediato = f_entrada <= (ahora + timedelta(minutes=10))
    
    if es_inmediato and habitacion.estado != EstadoHabitacion.libre:
         raise HTTPException(status_code=400, detail=f"La habitación no está libre (Estado: {habitacion.estado})")

    conflict = check_overlap(db, id, f_entrada, f_salida)
    if conflict:
        raise HTTPException(status_code=400, detail=f"Conflicto de horario con otra reserva/estancia (ID: {conflict.id})")
    # El primero es el cliente principal
    huespedes_db = []
    for h_schema in request.huespedes:
        cliente = db.query(ClienteDB).filter(ClienteDB.cedula == h_schema.cedula).first()
        if not cliente:
            cliente = ClienteDB(
                cedula=h_schema.cedula,
                nombre=h_schema.nombre,
                fecha_nacimiento=h_schema.fecha_nacimiento,
                nacionalidad=h_schema.nacionalidad,
                estado_civil=h_schema.estado_civil,
                direccion=h_schema.direccion or request.procedencia,
                telefono=h_schema.telefono,
                profesion=h_schema.profesion,
                reputacion=h_schema.reputacion,
                observaciones=h_schema.observaciones
            )
            db.add(cliente)
        else:
            # Actualizar datos si ya existe
            cliente.nombre = h_schema.nombre
            cliente.fecha_nacimiento = h_schema.fecha_nacimiento
            cliente.nacionalidad = h_schema.nacionalidad
            cliente.estado_civil = h_schema.estado_civil
            cliente.direccion = h_schema.direccion or request.procedencia
            cliente.telefono = h_schema.telefono
            cliente.profesion = h_schema.profesion
            cliente.observaciones = h_schema.observaciones
            cliente.reputacion = h_schema.reputacion
        huespedes_db.append(cliente)

    # 3. Validar Voucher si existe
    voucher_id = None
    if request.codigo_descuento:
        v = db.query(VoucherDB).filter(VoucherDB.codigo == request.codigo_descuento, VoucherDB.activo == True).first()
        if v:
            voucher_id = v.id

    # 4. Crear Estancia
    estado_estancia = EstadoEstancia.activa if es_inmediato else EstadoEstancia.reservada
    
    nueva_estancia = EstanciaDB(
        cliente_principal_id=huespedes_db[0].cedula,
        tipo_estadia=request.tipo_estadia,
        fecha_entrada=f_entrada,
        fecha_salida_planificada=f_salida,
        estado=estado_estancia,
        voucher_id=voucher_id,
        procedencia=request.procedencia,
        destino=request.destino,
        observaciones=request.observaciones_transaccion,
        usuario_creacion_id=request.usuario_id,
        fecha_creacion=ahora
    )
    db.add(nueva_estancia)
    db.flush() # Para obtener el ID de la estancia

    # 5. Vincular Habitación
    estancia_hab = EstanciaHabitacion(
        estancia_id=nueva_estancia.id,
        habitacion_id=habitacion.id,
        fecha_inicio=f_entrada
    )
    db.add(estancia_hab)

    # 6. Registrar Acompañantes
    for h in huespedes_db:
        estancia_huesped = EstanciaHuesped(
            estancia_id=nueva_estancia.id,
            cliente_id=h.cedula
        )
        db.add(estancia_huesped)

    # 7. Registrar Pagos
    for p in request.pagos:
        # Buscar el ID del método de pago por nombre
        metodo = db.query(MetodoPagoDB).filter(MetodoPagoDB.nombre == p.metodo).first()
        if metodo:
            pago_db = PagoDB(
                estancia_id=nueva_estancia.id,
                metodo_pago_id=metodo.id,
                monto=p.monto,
                referencia=p.referencia
            )
            db.add(pago_db)

    # 8. Registrar Extras
    for e in request.extras:
        extra_db = IngresoExtraDB(
            estancia_id=nueva_estancia.id,
            descripcion=e.descripcion,
            monto=e.monto
        )
        db.add(extra_db)

    # 9. Actualizar Habitación (Solo si es ingreso inmediato)
    if es_inmediato:
        habitacion.estancia_actual_id = nueva_estancia.id
        if request.tipo_estadia == "parcial":
            habitacion.estado = EstadoHabitacion.ocupada_parcial
        else:
            habitacion.estado = EstadoHabitacion.ocupada_hospedaje

    # 10. Marcar a los huéspedes como PRESENTES en el hotel y loguear historial
    ahora = datetime.utcnow()
    for h in huespedes_db:
        clean_cedula = h.cedula.strip()
        registro = db.query(RegistroPersonaHotel).filter(RegistroPersonaHotel.cedula == clean_cedula).first()
        if not registro:
            registro = RegistroPersonaHotel(
                cedula=clean_cedula,
                nombre=h.nombre,
                cargo="Cliente",
                estado="presente",
                ultima_entrada=ahora
            )
            db.add(registro)
        else:
            registro.estado = "presente"
            registro.ultima_entrada = ahora
            registro.nombre = h.nombre # Actualizar nombre por si acaso
            
        # Log de historial de acceso
        historial = HistorialAcceso(
            cedula=h.cedula,
            nombre=h.nombre,
            tipo="entrada",
            timestamp=ahora
        )
        db.add(historial)

    db.commit()
    return {"status": "success", "message": "Ingreso registrado correctamente", "estancia_id": str(nueva_estancia.id)}

@router.get("/{id}/estancia-activa", response_model=EstanciaDetalleResponse)
def get_estancia_activa(id: int, db: Session = Depends(get_db)):
    # 1. Buscar la habitación
    habitacion = db.query(HabitacionDB).filter(HabitacionDB.id == id).first()
    if not habitacion:
        raise HTTPException(status_code=404, detail="Habitación no encontrada")
    
    # 2. Verificar si tiene estancia activa
    if not habitacion.estancia_actual_id:
        raise HTTPException(status_code=404, detail="Esta habitación no tiene una estancia activa")
    
    # 3. Consultar la estancia con sus relaciones
    estancia = db.query(EstanciaDB).filter(EstanciaDB.id == habitacion.estancia_actual_id).first()
    if not estancia:
         raise HTTPException(status_code=404, detail="Error de integridad: No se encontró la estancia vinculada")

    # 4. Mapear huéspedes
    huespedes_list = []
    # Usamos el listado de huéspedes vinculados a la estancia
    for eh in estancia.huespedes:
        c = db.query(ClienteDB).filter(ClienteDB.cedula == eh.cliente_id).first()
        if c:
            # Separar tipo de cédula
            tipo = "V-"
            cedula_num = c.cedula
            for pref in ["V-", "E-", "J-", "G-", "P-"]:
                if c.cedula.startswith(pref):
                    tipo = pref
                    cedula_num = c.cedula[len(pref):]
                    break
            
            # Separar código de teléfono
            cod_tel = "+58"
            tel_num = c.telefono or ""
            for pref in ["+58", "+1", "+57", "+34", "+54"]:
                if tel_num.startswith(pref):
                    cod_tel = pref
                    tel_num = tel_num[len(pref):]
                    break

            huespedes_list.append({
                "cedula": cedula_num,
                "tipo_cedula": tipo,
                "nombre": c.nombre,
                "fecha_nacimiento": c.fecha_nacimiento,
                "nacionalidad": c.nacionalidad,
                "telefono": tel_num,
                "codigo_telefono": cod_tel,
                "profesion": c.profesion,
                "reputacion": c.reputacion.value if hasattr(c.reputacion, 'value') else c.reputacion,
                "observaciones": c.observaciones,
                "visitas": db.query(EstanciaHuesped).filter(EstanciaHuesped.cliente_id == c.cedula).count(),
                "estado": (reg.estado if (reg := db.query(RegistroPersonaHotel).filter(RegistroPersonaHotel.cedula == c.cedula.strip()).first()) else "ausente")
            })

    # 5. Mapear Pagos
    pagos_list = []
    for p in estancia.pagos:
        metodo = db.query(MetodoPagoDB).filter(MetodoPagoDB.id == p.metodo_pago_id).first()
        pagos_list.append({
            "metodo": metodo.nombre if metodo else "Desconocido",
            "monto": p.monto,
            "referencia": p.referencia
        })

    # 6. Mapear Extras
    extras_list = []
    for e in estancia.extras:
        extras_list.append({
            "descripcion": e.descripcion,
            "monto": e.monto
        })

    # 7. Obtener código de voucher
    voucher_codigo = None
    if estancia.voucher_id:
        v = db.query(VoucherDB).filter(VoucherDB.id == estancia.voucher_id).first()
        if v:
            voucher_codigo = v.codigo

    # Calcular costo base (estimado según precio actual si no se guardó el histórico)
    # Por ahora devolvemos el precio de la habitación según el tipo de estadía
    costo_base = habitacion.precio_hospedaje if estancia.tipo_estadia == "hospedaje" else habitacion.precio_parcial

    return EstanciaDetalleResponse(
        id=str(estancia.id),
        cliente_principal_id=estancia.cliente_principal_id,
        tipo_estadia=estancia.tipo_estadia,
        fecha_entrada=estancia.fecha_entrada.replace(tzinfo=timezone.utc) if estancia.fecha_entrada else None,
        fecha_salida_planificada=estancia.fecha_salida_planificada.replace(tzinfo=timezone.utc) if estancia.fecha_salida_planificada else None,
        procedencia=estancia.procedencia,
        destino=estancia.destino,
        observaciones=estancia.observaciones,
        huespedes=huespedes_list,
        pagos=pagos_list if pagos_list else [],
        extras=extras_list if extras_list else [],
        voucher_codigo=voucher_codigo,
        costo_dolar_base=costo_base
    )

@router.put("/{id}/estancia")
def actualizar_estancia(id: int, request: IngresoRequest, db: Session = Depends(get_db)):
    with open(r"c:\Users\walter\Documents\GitHub\Esmeralda_Definitive_Edition\backend\debug_put.log", "w") as f:
        f.write(request.model_dump_json(indent=2))
    
    # 1. Buscar habitación y su estancia activa
    habitacion = db.query(HabitacionDB).filter(HabitacionDB.id == id).first()
    if not habitacion or not habitacion.estancia_actual_id:
        raise HTTPException(status_code=404, detail="No hay una estancia activa para esta habitación")
    
    estancia = db.query(EstanciaDB).filter(EstanciaDB.id == habitacion.estancia_actual_id).first()
    
    estancia.procedencia = request.procedencia
    estancia.destino = request.destino
    estancia.observaciones = request.observaciones_transaccion
    
    # 3. Actualizar Huéspedes (Upsert) y recrear vínculos
    db.query(EstanciaHuesped).filter(EstanciaHuesped.estancia_id == estancia.id).delete()
    
    # Obtener lista de huéspedes actualizada para marcar como presentes si no lo estaban
    ahora = datetime.utcnow()
    
    for h_schema in request.huespedes:
        cliente = db.query(ClienteDB).filter(ClienteDB.cedula == h_schema.cedula).first()
        if not cliente:
            cliente = ClienteDB(
                cedula=h_schema.cedula,
                nombre=h_schema.nombre,
                fecha_nacimiento=h_schema.fecha_nacimiento,
                nacionalidad=h_schema.nacionalidad,
                estado_civil=h_schema.estado_civil,
                direccion=h_schema.direccion or request.procedencia,
                telefono=h_schema.telefono,
                profesion=h_schema.profesion,
                observaciones=h_schema.observaciones
            )
            db.add(cliente)
        else:
            cliente.nombre = h_schema.nombre
            cliente.fecha_nacimiento = h_schema.fecha_nacimiento
            cliente.estado_civil = h_schema.estado_civil
            cliente.direccion = h_schema.direccion or request.procedencia
            cliente.telefono = h_schema.telefono
            cliente.observaciones = h_schema.observaciones
            cliente.reputacion = h_schema.reputacion
        
        # Vincular
        db.add(EstanciaHuesped(estancia_id=estancia.id, cliente_id=cliente.cedula))

        # Garantizar que el huésped esté marcado como PRESENTE en el hotel
        clean_cedula = h_schema.cedula.strip()
        registro = db.query(RegistroPersonaHotel).filter(RegistroPersonaHotel.cedula == clean_cedula).first()
        if not registro:
            db.add(RegistroPersonaHotel(
                cedula=clean_cedula,
                nombre=h_schema.nombre,
                cargo="Cliente",
                estado="presente",
                ultima_entrada=ahora
            ))
            # Log de historial de acceso
            db.add(HistorialAcceso(cedula=clean_cedula, nombre=h_schema.nombre, tipo="entrada", timestamp=ahora))
        else:
            if registro.estado != "presente":
                registro.estado = "presente"
                registro.ultima_entrada = ahora
                # Log de historial de acceso
                db.add(HistorialAcceso(cedula=clean_cedula, nombre=h_schema.nombre, tipo="entrada", timestamp=ahora))

    db.commit()

    # 4. Sincronizar Pagos (Simple: Borrar y Recrear para esta estancia en este ejemplo de flujo rápido)
    # En producción se debería usar IDs para evitar pérdida de timestamps originales
    db.query(PagoDB).filter(PagoDB.estancia_id == estancia.id).delete()
    for p in request.pagos:
        metodo = db.query(MetodoPagoDB).filter(MetodoPagoDB.nombre == p.metodo).first()
        if metodo:
            db.add(PagoDB(estancia_id=estancia.id, metodo_pago_id=metodo.id, monto=p.monto, referencia=p.referencia))

    # 5. Sincronizar Extras
    db.query(IngresoExtraDB).filter(IngresoExtraDB.estancia_id == estancia.id).delete()
    for e in request.extras:
        db.add(IngresoExtraDB(estancia_id=estancia.id, descripcion=e.descripcion, monto=e.monto))

    db.commit()
    return {"status": "success", "message": "Datos de estancia actualizados correctamente"}

@router.post("/{id}/cambiar_habitacion")
def cambiar_habitacion(id: int, request: CambiarHabitacionRequest, db: Session = Depends(get_db)):
    # 1. Buscar habitación actual y su estancia
    hab_actual = db.query(HabitacionDB).filter(HabitacionDB.id == id).first()
    if not hab_actual or not hab_actual.estancia_actual_id:
        raise HTTPException(status_code=404, detail="No hay estancia activa en la habitación actual")
    
    # 2. Buscar nueva habitación y asegurar que esté libre
    hab_nueva = db.query(HabitacionDB).filter(HabitacionDB.id == request.nueva_habitacion_id).first()
    if not hab_nueva or hab_nueva.estado != EstadoHabitacion.libre:
        raise HTTPException(status_code=400, detail="La nueva habitación no está disponible")
    
    estancia = db.query(EstanciaDB).filter(EstanciaDB.id == hab_actual.estancia_actual_id).first()
    
    # 3. Registrar el cambio de habitación en el historial (observaciones)
    obs_previas = estancia.observaciones or ""
    nueva_obs = f"\\n[Cambio de Hab. {hab_actual.numero} a {hab_nueva.numero}]: {request.motivo}"
    estancia.observaciones = obs_previas + nueva_obs
    
    ahora = datetime.utcnow()
    
    # 4. Finalizar vinculación antigua
    vinculo_antiguo = db.query(EstanciaHabitacion).filter(
        EstanciaHabitacion.estancia_id == estancia.id, 
        EstanciaHabitacion.habitacion_id == hab_actual.id,
        EstanciaHabitacion.fecha_fin.is_(None)
    ).first()
    if vinculo_antiguo:
        vinculo_antiguo.fecha_fin = ahora
    
    # 5. Crear nueva vinculación
    nuevo_vinculo = EstanciaHabitacion(
        estancia_id=estancia.id,
        habitacion_id=hab_nueva.id,
        fecha_inicio=ahora
    )
    db.add(nuevo_vinculo)
    
    # 6. Actualizar estado de las habitaciones
    hab_nueva.estancia_actual_id = estancia.id
    hab_nueva.estado = hab_actual.estado
    
    hab_actual.estancia_actual_id = None
    hab_actual.estado = EstadoHabitacion.sucia  # Se deja sucia por defecto
    
    db.commit()
    return {"status": "success", "message": "Habitación cambiada exitosamente"}

@router.post("/{id}/liberar")
def liberar_habitacion(id: int, db: Session = Depends(get_db)):
    # 1. Buscar la habitación
    habitacion = db.query(HabitacionDB).filter(HabitacionDB.id == id).first()
    if not habitacion:
        raise HTTPException(status_code=404, detail="Habitación no encontrada")
    
    if habitacion.estado == EstadoHabitacion.retoque:
        raise HTTPException(status_code=400, detail="No se puede egresar una habitación en RETOQUE")
    
    # 2. Finalizar la estancia si existe
    if habitacion.estancia_actual_id:
        estancia = db.query(EstanciaDB).filter(EstanciaDB.id == habitacion.estancia_actual_id).first()
        if estancia:
            estancia.estado = EstadoEstancia.finalizada
            estancia.fecha_salida_real = datetime.utcnow()
        
        # Finalizar vinculación de habitación
        vinculo = db.query(EstanciaHabitacion).filter(
            EstanciaHabitacion.estancia_id == habitacion.estancia_actual_id,
            EstanciaHabitacion.habitacion_id == habitacion.id,
            EstanciaHabitacion.fecha_fin.is_(None)
        ).first()
        if vinculo:
            vinculo.fecha_fin = datetime.utcnow()
            
    # 3. Poner la habitación en estado sucia y quitar la estancia actual
    habitacion.estancia_actual_id = None
    habitacion.estado = EstadoHabitacion.sucia
    
    db.commit()
    return {"status": "success", "message": "Habitación liberada correctamente (estado Sucia)"}

@router.post("/{id}/pasar_a_hospedaje")
def pasar_a_hospedaje(id: int, db: Session = Depends(get_db)):
    # Validar que sea hoy? No necesariamene, puede ser ayer.
    ahora = datetime.utcnow()
    habitacion = db.query(HabitacionDB).filter(HabitacionDB.id == id).first()
    if not habitacion or not habitacion.estancia_actual_id:
        raise HTTPException(status_code=404, detail="No hay una estancia activa para esta habitación")
    
    estancia = db.query(EstanciaDB).filter(EstanciaDB.id == habitacion.estancia_actual_id).first()
    
    if estancia.tipo_estadia != "parcial":
        raise HTTPException(status_code=400, detail="La estancia actual no es de tipo parcial")
    
    # 2. Cambiar tipo de estancia a hospedaje
    estancia.tipo_estadia = "hospedaje"
    
    # 3. Recalcular fecha de salida planificada
    # Si la entrada fue >= 9 AM, sale mañana a la 1 PM. Si fue antes, sale hoy a la 1 PM.
    f_entrada = estancia.fecha_entrada
    if f_entrada.hour >= 9:
        f_salida = datetime.combine(f_entrada.date() + timedelta(days=1), time(13, 0))
    else:
        f_salida = datetime.combine(f_entrada.date(), time(13, 0))
    
    estancia.fecha_salida_planificada = f_salida
    
    # 4. Actualizar estado de habitación a ocupada_hospedaje
    habitacion.estado = EstadoHabitacion.ocupada_hospedaje
    
    db.commit()
    return {
        "status": "success", 
        "message": "Convertido a hospedaje correctamente", 
        "nueva_fecha_salida": f_salida.isoformat()
    }

@router.post("/{id}/limpiar")
def limpiar_habitacion(id: int, request: LimpiarRequest, db: Session = Depends(get_db)):
    habitacion = db.query(HabitacionDB).filter(HabitacionDB.id == id).first()
    if not habitacion:
        raise HTTPException(status_code=404, detail="Habitación no encontrada")
    
    if habitacion.estado != EstadoHabitacion.sucia:
        raise HTTPException(status_code=400, detail="La habitación no está sucia")
    
    camarera = db.query(User).filter(User.id == request.camarera_id).first()
    if not camarera:
        raise HTTPException(status_code=404, detail="Camarera no encontrada")

    habitacion.estado = EstadoHabitacion.libre
    
    # Log the cleaning action
    db.add(LogDB(
        usuario_id=camarera.id,
        accion="Limpieza",
        descripcion=f"Habitación {habitacion.numero} limpiada por {camarera.nombre}"
    ))
    
    db.commit()
    return {"status": "success", "message": "Habitación marcada como limpia (Libre)"}

@router.get("/camareras-presentes")
def get_camareras_presentes(db: Session = Depends(get_db)):
    # Buscamos usuarios con rol de camarera
    camareras = db.query(User).filter(User.rol == "camarera").all()
    
    # Filtramos por aquellas que están presentes según RegistroPersonaHotel
    # Según acceso.py, relacionamos User.username con RegistroPersonaHotel.cedula
    presentes = []
    for c in camareras:
        reg = db.query(RegistroPersonaHotel).filter(
            RegistroPersonaHotel.cedula == c.username,
            RegistroPersonaHotel.estado == "presente"
        ).first()
        if reg:
            presentes.append({
                "id": c.id,
                "nombre": c.nombre or c.username,
                "username": c.username
            })
    return presentes

@router.post("/{id}/bloquear")
def bloquear_habitacion(id: int, request: BloquearRequest, db: Session = Depends(get_db)):
    habitacion = db.query(HabitacionDB).filter(HabitacionDB.id == id).first()
    if not habitacion:
        raise HTTPException(status_code=404, detail="Habitación no encontrada")
    
    # Si la habitación está ocupada y se proporciona una nueva habitación, mover al huésped
    if habitacion.estancia_actual_id and request.nueva_habitacion_id:
        hab_nueva = db.query(HabitacionDB).filter(HabitacionDB.id == request.nueva_habitacion_id).first()
        if not hab_nueva or hab_nueva.estado != EstadoHabitacion.libre:
            raise HTTPException(status_code=400, detail="La nueva habitación no está disponible")
        
        estancia = db.query(EstanciaDB).filter(EstanciaDB.id == habitacion.estancia_actual_id).first()
        
        # Registrar el cambio por bloqueo
        obs_previas = estancia.observaciones or ""
        nueva_obs = f"\n[Cambio por Bloqueo de Hab. {habitacion.numero} a {hab_nueva.numero}]: {request.motivo}"
        estancia.observaciones = obs_previas + nueva_obs
        
        ahora = datetime.utcnow()
        
        # Finalizar vinculación antigua
        vinculo_antiguo = db.query(EstanciaHabitacion).filter(
            EstanciaHabitacion.estancia_id == estancia.id, 
            EstanciaHabitacion.habitacion_id == habitacion.id,
            EstanciaHabitacion.fecha_fin.is_(None)
        ).first()
        if vinculo_antiguo:
            vinculo_antiguo.fecha_fin = ahora
        
        # Crear nueva vinculación
        nuevo_vinculo = EstanciaHabitacion(
            estancia_id=estancia.id,
            habitacion_id=hab_nueva.id,
            fecha_inicio=ahora
        )
        db.add(nuevo_vinculo)
        
        # Actualizar nueva habitación
        hab_nueva.estancia_actual_id = estancia.id
        hab_nueva.estado = habitacion.estado # Mantener el estado (Hospedaje/Parcial)
        
        # La habitación actual ya no tiene la estancia
        habitacion.estancia_actual_id = None

    habitacion.estado = EstadoHabitacion.bloqueada
    habitacion.razon_bloqueo = request.motivo
    db.commit()
    return {"status": "success", "message": "Habitación bloqueada correctamente"}

@router.post("/{id}/desbloquear")
def desbloquear_habitacion(id: int, db: Session = Depends(get_db)):
    habitacion = db.query(HabitacionDB).filter(HabitacionDB.id == id).first()
    if not habitacion:
        raise HTTPException(status_code=404, detail="Habitación no encontrada")
    
    if habitacion.estado != EstadoHabitacion.bloqueada:
        raise HTTPException(status_code=400, detail="La habitación no está bloqueada")
    
    habitacion.estado = EstadoHabitacion.libre
    habitacion.razon_bloqueo = None
    db.commit()
    return {"status": "success", "message": "Habitación desbloqueada correctamente"}

@router.get("/{id}/historial")
def get_historial_habitacion(id: int, db: Session = Depends(get_db)):
    # Buscar vinculaciones de esta habitación con estancias
    vinculos = db.query(EstanciaHabitacion).filter(EstanciaHabitacion.habitacion_id == id).order_by(EstanciaHabitacion.fecha_inicio.desc()).all()
    
    historial = []
    for v in vinculos:
        estancia = v.estancia
        cliente = db.query(ClienteDB).filter(ClienteDB.cedula == estancia.cliente_principal_id).first()
        
        # Consolidar pagos por método
        pagos_dict = {}
        for p in estancia.pagos:
            metodo = db.query(MetodoPagoDB).filter(MetodoPagoDB.id == p.metodo_pago_id).first()
            nombre_metodo = metodo.nombre if metodo else "Desconocido"
            pagos_dict[nombre_metodo] = pagos_dict.get(nombre_metodo, 0) + p.monto

        historial.append({
            "fecha_entrada": v.fecha_inicio.replace(tzinfo=timezone.utc) if v.fecha_inicio else None,
            "fecha_salida": (v.fecha_fin or estancia.fecha_salida_real).replace(tzinfo=timezone.utc) if (v.fecha_fin or estancia.fecha_salida_real) else None,
            "cliente": cliente.nombre if cliente else "Desconocido",
            "tipo_estadia": estancia.tipo_estadia,
            "pagos": pagos_dict,
            "procedencia": estancia.procedencia,
            "destino": estancia.destino,
            "observaciones": estancia.observaciones
        })
    
    return historial

@router.post("/{id}/retoque")
def retoque_habitacion(id: int, request: RetoqueRequest, db: Session = Depends(get_db)):
    habitacion = db.query(HabitacionDB).filter(HabitacionDB.id == id).first()
    if not habitacion:
        raise HTTPException(status_code=404, detail="Habitación no encontrada")
    
    camarera = db.query(User).filter(User.id == request.camarera_id).first()
    if not camarera:
        raise HTTPException(status_code=404, detail="Camarera no encontrada")
    
    # Cambiar estado a retoque
    habitacion.estado = EstadoHabitacion.retoque
    
    # Registrar en logs
    db.add(LogDB(
        usuario_id=camarera.id,
        accion="Retoque",
        descripcion=f"Retoque iniciado en Hab. {habitacion.numero} por {camarera.nombre}"
    ))
    
    db.commit()
    return {"status": "success", "message": "Habitación en RETOQUE"}

@router.post("/{id}/finalizar_retoque")
def finalizar_retoque(id: int, db: Session = Depends(get_db)):
    habitacion = db.query(HabitacionDB).filter(HabitacionDB.id == id).first()
    if not habitacion:
        raise HTTPException(status_code=404, detail="Habitación no encontrada")
    
    if habitacion.estado != EstadoHabitacion.retoque:
        raise HTTPException(status_code=400, detail="La habitación no está en retoque")
    
    # Volver al estado ocupado según la estancia
    if habitacion.estancia_actual_id:
        estancia = db.query(EstanciaDB).filter(EstanciaDB.id == habitacion.estancia_actual_id).first()
        if estancia and estancia.tipo_estadia == "parcial":
            habitacion.estado = EstadoHabitacion.ocupada_parcial
        else:
            habitacion.estado = EstadoHabitacion.ocupada_hospedaje
    else:
        # Si por alguna razón no tiene estancia, volver a libre o sucia?
        # El user dijo que es cuando un cliente pide retoque, por lo que debería tener estancia.
        habitacion.estado = EstadoHabitacion.libre
        
    db.commit()
    return {"status": "success", "message": "Retoque finalizado"}

@router.get("/reservas/proximas", response_model=List[ReservaResponse])
def get_reservas_proximas(db: Session = Depends(get_db)):
    reservas = db.query(EstanciaDB).filter(EstanciaDB.estado == EstadoEstancia.reservada).order_by(EstanciaDB.fecha_entrada.asc()).all()
    
    resultado = []
    for r in reservas:
        cliente = db.query(ClienteDB).filter(ClienteDB.cedula == r.cliente_principal_id).first()
        vinculo = db.query(EstanciaHabitacion).filter(EstanciaHabitacion.estancia_id == r.id).first()
        habitacion = db.query(HabitacionDB).filter(HabitacionDB.id == vinculo.habitacion_id).first() if vinculo else None
        
        monto_pagado = sum(p.monto for p in r.pagos)
        
        # Calcular monto total estimado
        if habitacion:
            monto_total = habitacion.precio_hospedaje if r.tipo_estadia == "hospedaje" else habitacion.precio_parcial
        else:
            monto_total = 0
            
        usuario = db.query(User).filter(User.id == r.usuario_creacion_id).first()
        
        # Obtener método de pago predominante (el primero que encontremos)
        metodo = "N/A"
        if r.pagos:
            m = db.query(MetodoPagoDB).filter(MetodoPagoDB.id == r.pagos[0].metodo_pago_id).first()
            if m:
                metodo = m.nombre

        resultado.append(ReservaResponse(
            id=str(r.id),
            habitacion_numero=habitacion.numero if habitacion else "??",
            cliente_nombre=cliente.nombre if cliente else "??",
            fecha_entrada=r.fecha_entrada.replace(tzinfo=timezone.utc) if r.fecha_entrada else None,
            fecha_salida=r.fecha_salida_planificada.replace(tzinfo=timezone.utc) if r.fecha_salida_planificada else None,
            tipo_estadia=r.tipo_estadia,
            monto_pagado=monto_pagado,
            monto_total=monto_total,
            metodo_pago=metodo,
            usuario_creacion=usuario.nombre if usuario else "Sistema",
            fecha_creacion=(r.fecha_creacion or r.fecha_entrada).replace(tzinfo=timezone.utc),
            observaciones=r.observaciones
        ))
    return resultado

@router.post("/reservas/{estancia_id}/cancelar")
def cancelar_reserva(estancia_id: str, db: Session = Depends(get_db)):
    estancia = db.query(EstanciaDB).filter(EstanciaDB.id == estancia_id).first()
    if not estancia:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    
    estancia.estado = EstadoEstancia.cancelada
    db.commit()
    return {"status": "success", "message": "Reserva cancelada"}

@router.post("/reservas/{estancia_id}/activar")
def activar_reserva(estancia_id: str, db: Session = Depends(get_db)):
    estancia = db.query(EstanciaDB).filter(EstanciaDB.id == estancia_id).first()
    if not estancia:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    
    # Buscar habitación vinculada
    vinculo = db.query(EstanciaHabitacion).filter(EstanciaHabitacion.estancia_id == estancia.id).first()
    if not vinculo:
        raise HTTPException(status_code=400, detail="Esta reserva no tiene una habitación vinculada")
    
    habitacion = db.query(HabitacionDB).filter(HabitacionDB.id == vinculo.habitacion_id).first()
    if habitacion.estado != EstadoHabitacion.libre:
         raise HTTPException(status_code=400, detail=f"La habitación {habitacion.numero} no está libre (Estado: {habitacion.estado})")

    # Activar estancias y actualizar fechas según la realidad
    ahora = datetime.utcnow()
    
    # Recalcular salida
    if estancia.tipo_estadia == "hospedaje":
        # Regla: Si entra >= 9 AM, sale mañana a la 1 PM. Si < 9 AM, sale hoy a la 1 PM.
        if ahora.hour >= 9:
            f_salida = datetime.combine(ahora.date() + timedelta(days=1), time(13, 0))
        else:
            f_salida = datetime.combine(ahora.date(), time(13, 0))
    else:
        # Parcial: Mantener la duración original (delta)
        duracion_original = estancia.fecha_salida_planificada - estancia.fecha_entrada
        f_salida = ahora + duracion_original

    # Actualizar estancia
    estancia.fecha_entrada = ahora
    estancia.fecha_salida_planificada = f_salida
    estancia.estado = EstadoEstancia.activa
    
    # Actualizar vínculo de tiempo
    vinculo.fecha_inicio = ahora
    
    habitacion.estancia_actual_id = estancia.id
    if estancia.tipo_estadia == "parcial":
        habitacion.estado = EstadoHabitacion.ocupada_parcial
    else:
        habitacion.estado = EstadoHabitacion.ocupada_hospedaje
        
    db.commit()
    return {
        "status": "success", 
        "message": "Reserva activada correctamente",
        "nueva_entrada": ahora.isoformat(),
        "nueva_salida": f_salida.isoformat()
    }
@router.get("/historial/global")
def get_estancias_historial(limit: int = 100, skip: int = 0, s: Optional[str] = None, start: Optional[datetime] = None, end: Optional[datetime] = None, db: Session = Depends(get_db)):
    # Traer estancias recientes con datos de cliente y habitacion vinculada
    query = db.query(EstanciaDB)
    
    if start:
        query = query.filter(EstanciaDB.fecha_entrada >= start)
    if end:
        query = query.filter(EstanciaDB.fecha_entrada <= end)
    
    if s:
        # Buscar por nombre de cliente, cédula o número de habitación
        query = query.join(ClienteDB, EstanciaDB.cliente_principal_id == ClienteDB.cedula)
        query = query.filter(
            (ClienteDB.nombre.ilike(f"%{s}%")) | 
            (ClienteDB.cedula.ilike(f"%{s}%")) |
            (EstanciaDB.observaciones.ilike(f"%{s}%"))
        )
        # Nota: La búsqueda por número de habitación es más compleja por el join con Vincualcion
        
    results = query.order_by(EstanciaDB.fecha_entrada.desc()).offset(skip).limit(limit).all()
    
    output = []
    for est in results:
        # Buscar habitacion vinculada (el vinculo mas reciente para esta estancia)
        vinculo = db.query(EstanciaHabitacion).filter(EstanciaHabitacion.estancia_id == est.id).first()
        hab_num = "???"
        if vinculo:
            hab = db.query(HabitacionDB).filter(HabitacionDB.id == vinculo.habitacion_id).first()
            if hab:
                hab_num = hab.numero
        
        cliente = db.query(ClienteDB).filter(ClienteDB.cedula == est.cliente_principal_id).first()
        monto_pagado = sum(p.monto for p in est.pagos)
        
        output.append({
            "id": str(est.id),
            "label": "Hospedaje",
            "hab": hab_num,
            "fecha": est.fecha_entrada.isoformat() if est.fecha_entrada else None,
            "estado": est.estado.value.upper() if hasattr(est.estado, 'value') else str(est.estado).upper(),
            "cat": est.tipo_estadia.capitalize(),
            "monto": f"{monto_pagado:.2f}",
            "cliente": cliente.nombre if cliente else "Desconocido",
            "fotos": [] # Por ahora vacío
        })
    return output
