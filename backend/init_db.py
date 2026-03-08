import sys
import os

# Configuración de rutas para que Python encuentre los módulos
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_dir, "src"))

# Evitar imports relativos que causan problemas en scripts independientes
from infrastructure.database import engine, Base
from infrastructure.models import HabitacionDB, User, MetodoPagoDB, EstadoHabitacion
from sqlalchemy.orm import Session
from infrastructure.database import SessionLocal

# Re-definimos los datos aquí para evitar el error de importación relativa del mock original
_t = {
    "47": "sencilla", "46": "sencilla", "45": "sencilla", "44": "sencilla", "43": "sencilla", "42": "sencilla", "41": "sencilla", "40": "sencilla", "39": "sencilla", "38": "sencilla", "37": "sencilla", "36": "sencilla",
    "27": "sencilla", "28": "sencilla", "29": "sencilla", "30": "sencilla", "31": "sencilla", "32": "sencilla", "33": "sencilla", "34": "sencilla", "35": "sencilla",
    "48": "presidencial", "26": "sencilla", "25": "sencilla", "24": "sencilla", "23": "sencilla", "22": "sencilla", "21": "sencilla",
    "11": "cuadruple", "12": "confort", "13": "triple", "14": "confort", "15": "triple", "16": "triple", "17": "confort", "18": "cuadruple", "19": "confort", "20": "triple",
    "10": "cuadruple", "09": "confort", "08": "triple", "07": "confort", "06": "triple", "05": "triple", "04": "confort", "03": "triple", "02": "confort", "01": "triple",
    "AP2": "apartamento", "AP1": "apartamento"
}

MOCK_DATABASE_DATA = [
     {"id": 47, "numero": "47", "tipo": _t["47"], "estado": "bloqueada", "x": 1, "y": 1},
     {"id": 46, "numero": "46", "tipo": _t["46"], "estado": "libre", "x": 2, "y": 1},
     {"id": 45, "numero": "45", "tipo": _t["45"], "estado": "libre", "x": 3, "y": 1},
     {"id": 44, "numero": "44", "tipo": _t["44"], "estado": "ocupada_hospedaje", "x": 4, "y": 1},
     {"id": 43, "numero": "43", "tipo": _t["43"], "estado": "libre", "x": 5, "y": 1},
     {"id": 42, "numero": "42", "tipo": _t["42"], "estado": "libre", "x": 6, "y": 1},
     {"id": 41, "numero": "41", "tipo": _t["41"], "estado": "libre", "x": 7, "y": 1},
     {"id": 40, "numero": "40", "tipo": _t["40"], "estado": "libre", "x": 8, "y": 1},
     {"id": 39, "numero": "39", "tipo": _t["39"], "estado": "libre", "x": 9, "y": 1},
     {"id": 38, "numero": "38", "tipo": _t["38"], "estado": "libre", "x": 10, "y": 1},
     {"id": 37, "numero": "37", "tipo": _t["37"], "estado": "libre", "x": 11, "y": 1},
     {"id": 36, "numero": "36", "tipo": _t["36"], "estado": "libre", "x": 12, "y": 1},
     {"id": 27, "numero": "27", "tipo": _t["27"], "estado": "bloqueada", "x": 3, "y": 2},
     {"id": 28, "numero": "28", "tipo": _t["28"], "estado": "libre", "x": 4, "y": 2},
     {"id": 29, "numero": "29", "tipo": _t["29"], "estado": "ocupada_hospedaje", "x": 5, "y": 2},
     {"id": 30, "numero": "30", "tipo": _t["30"], "estado": "libre", "x": 7, "y": 2},
     {"id": 31, "numero": "31", "tipo": _t["31"], "estado": "libre", "x": 8, "y": 2},
     {"id": 32, "numero": "32", "tipo": _t["32"], "estado": "libre", "x": 9, "y": 2},
     {"id": 33, "numero": "33", "tipo": _t["33"], "estado": "libre", "x": 10, "y": 2},
     {"id": 34, "numero": "34", "tipo": _t["34"], "estado": "libre", "x": 11, "y": 2},
     {"id": 35, "numero": "35", "tipo": _t["35"], "estado": "sucia", "x": 12, "y": 2},
     {"id": 48, "numero": "48", "tipo": _t["48"], "estado": "libre", "x": 6, "y": 4},
     {"id": 26, "numero": "26", "tipo": _t["26"], "estado": "sucia", "x": 7, "y": 4},
     {"id": 25, "numero": "25", "tipo": _t["25"], "estado": "sucia", "x": 8, "y": 4},
     {"id": 24, "numero": "24", "tipo": _t["24"], "estado": "sucia", "x": 9, "y": 4},
     {"id": 23, "numero": "23", "tipo": _t["23"], "estado": "sucia", "x": 10, "y": 4},
     {"id": 22, "numero": "22", "tipo": _t["22"], "estado": "sucia", "x": 11, "y": 4},
     {"id": 21, "numero": "21", "tipo": _t["21"], "estado": "libre", "x": 12, "y": 4},
     {"id": 11, "numero": "11", "tipo": _t["11"], "estado": "libre", "x": 3, "y": 5},
     {"id": 12, "numero": "12", "tipo": _t["12"], "estado": "bloqueada", "x": 4, "y": 5},
     {"id": 13, "numero": "13", "tipo": _t["13"], "estado": "libre", "x": 5, "y": 5},
     {"id": 14, "numero": "14", "tipo": _t["14"], "estado": "bloqueada", "x": 6, "y": 5},
     {"id": 15, "numero": "15", "tipo": _t["15"], "estado": "sucia", "x": 7, "y": 5},
     {"id": 16, "numero": "16", "tipo": _t["16"], "estado": "libre", "x": 8, "y": 5},
     {"id": 17, "numero": "17", "tipo": _t["17"], "estado": "bloqueada", "x": 9, "y": 5},
     {"id": 18, "numero": "18", "tipo": _t["18"], "estado": "sucia", "x": 10, "y": 5},
     {"id": 19, "numero": "19", "tipo": _t["19"], "estado": "libre", "x": 11, "y": 5},
     {"id": 20, "numero": "20", "tipo": _t["20"], "estado": "ocupada_parcial", "x": 12, "y": 5},
     {"id": 10, "numero": "10", "tipo": _t["10"], "estado": "libre", "x": 3, "y": 7},
     {"id": 9, "numero": "09", "tipo": _t["09"], "estado": "libre", "x": 4, "y": 7},
     {"id": 8, "numero": "08", "tipo": _t["08"], "estado": "libre", "x": 5, "y": 7},
     {"id": 7, "numero": "07", "tipo": _t["07"], "estado": "sucia", "x": 6, "y": 7},
     {"id": 6, "numero": "06", "tipo": _t["06"], "estado": "libre", "x": 7, "y": 7},
     {"id": 5, "numero": "05", "tipo": _t["05"], "estado": "libre", "x": 8, "y": 7},
     {"id": 4, "numero": "04", "tipo": _t["04"], "estado": "sucia", "x": 9, "y": 7},
     {"id": 3, "numero": "03", "tipo": _t["03"], "estado": "sucia", "x": 10, "y": 7},
     {"id": 2, "numero": "02", "tipo": _t["02"], "estado": "sucia", "x": 11, "y": 7},
     {"id": 1, "numero": "01", "tipo": _t["01"], "estado": "ocupada_hospedaje", "x": 12, "y": 7},
     {"id": 49, "numero": "AP2", "tipo": _t["AP2"], "estado": "bloqueada", "x": 1, "y": 8},
     {"id": 50, "numero": "AP1", "tipo": _t["AP1"], "estado": "libre", "x": 2, "y": 8}
]

def init_db():
    print("--- Creando tablas ---")
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas.")

    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == "admin").first():
            admin = User(username="admin", password_hash="admin123", rol="admin")
            db.add(admin)
            print("Admin creado (pass: admin123).")

        # Agregar camareras falsas para retoque
        from infrastructure.models import RegistroPersonaHotel # Import inside to avoid circular if any
        camareras = [
            {"username": "camarera1", "nombre": "Juana Perez", "rol": "camarera", "cedula": "camarera1"},
            {"username": "camarera2", "nombre": "Maria Lopez", "rol": "camarera", "cedula": "camarera2"},
            {"username": "camarera3", "nombre": "Rosa Garcia", "rol": "camarera", "cedula": "camarera3"},
        ]
        for c in camareras:
            if not db.query(User).filter(User.username == c["username"]).first():
                nueva_c = User(username=c["username"], nombre=c["nombre"], password_hash="123456", rol="camarera")
                db.add(nueva_c)
            
            # Asegurar que estén en el hotel como "presente" para las pruebas
            reg = db.query(RegistroPersonaHotel).filter(RegistroPersonaHotel.cedula == c["cedula"]).first()
            if not reg:
                db.add(RegistroPersonaHotel(cedula=c["cedula"], nombre=c["nombre"], cargo="Camarera", estado="presente"))
        print("Camareras de prueba creadas y marcadas como PRESENTES.")

        metodos = [
            {"nombre": "Efectivo Dolar", "moneda": "USD"},
            {"nombre": "Efectivo Bolivar", "moneda": "VES"},
            {"nombre": "Punto de Venta", "moneda": "VES"},
            {"nombre": "Pago Móvil", "moneda": "VES"},
            {"nombre": "Zelle", "moneda": "USD"},
            {"nombre": "Transferencia", "moneda": "VES"},
        ]
        for m in metodos:
            # Upsert simple: si no existe el nombre, lo crea
            metodo_db = db.query(MetodoPagoDB).filter(MetodoPagoDB.nombre == m["nombre"]).first()
            if not metodo_db:
                db.add(MetodoPagoDB(**m))
        print("Metodos de pago sincronizados.")

        if db.query(HabitacionDB).count() == 0:
            for h in MOCK_DATABASE_DATA:
                db_hab = HabitacionDB(
                    id=h["id"],
                    numero=h["numero"],
                    tipo=h["tipo"],
                    estado=h["estado"],
                    pos_x=h["x"],
                    pos_y=h["y"],
                    precio_parcial=20.0, # Precios base ejemplo
                    precio_hospedaje=40.0
                )
                db.add(db_hab)
            print(f"{len(MOCK_DATABASE_DATA)} habitaciones creadas.")
        
        db.commit()
        print("FINALIZADO: Base de datos lista.")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
