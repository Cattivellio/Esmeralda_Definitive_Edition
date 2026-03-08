import threading
import time
import sys
import os

# Configuración de rutas
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_dir, "src"))

from infrastructure.database import SessionLocal
from infrastructure.models import HabitacionDB, LogDB

def thread_escritor_habitacion(id_hilo, num_operaciones):
    """Simula a un recepcionista cambiando estados de habitación rápidamente."""
    db = SessionLocal()
    exitos = 0
    errores = 0
    try:
        for i in range(num_operaciones):
            try:
                # Cambiamos el estado de la habitación 1 repetidamente
                hab = db.query(HabitacionDB).filter(HabitacionDB.id == 1).first()
                if hab:
                    hab.observaciones = f"Update from Thread {id_hilo} - ops {i}"
                    db.commit()
                    exitos += 1
            except Exception as e:
                print(f"\n[Hilo {id_hilo}] Error en escritura: {e}")
                db.rollback()
                errores += 1
            time.sleep(0.01) # Simula un respiro muy corto
    finally:
        db.close()
    print(f"\n[Hilo {id_hilo}] Finalizado. Éxitos: {exitos}, Errores: {errores}")

def thread_escritor_logs(id_hilo, num_operaciones):
    """Simula a la administración generando muchos registros de log."""
    db = SessionLocal()
    exitos = 0
    errores = 0
    try:
        for i in range(num_operaciones):
            try:
                nuevo_log = LogDB(accion="TEST_STRESS", descripcion=f"Hilo {id_hilo} operacion {i}")
                db.add(nuevo_log)
                db.commit()
                exitos += 1
            except Exception as e:
                print(f"\n[Hilo {id_hilo}] Error en log: {e}")
                db.rollback()
                errores += 1
            time.sleep(0.01)
    finally:
        db.close()
    print(f"\n[Hilo {id_hilo}] Finalizado. Éxitos: {exitos}, Errores: {errores}")

def thread_lector(id_hilo, num_operaciones):
    """Simula a lencería o al dueño leyendo datos constantemente."""
    db = SessionLocal()
    exitos = 0
    errores = 0
    try:
        for i in range(num_operaciones):
            try:
                # Lee todas las habitaciones
                count = db.query(HabitacionDB).count()
                exitos += 1
            except Exception as e:
                print(f"\n[Hilo {id_hilo}] Error en lectura: {e}")
                errores += 1
            time.sleep(0.01)
    finally:
        db.close()
    print(f"\n[Hilo {id_hilo}] Finalizado (Lector). Éxitos: {exitos}, Errores: {errores}")

def run_stress_test():
    print("--- Iniciando Test de Concurrencia SQLite (Modo WAL) ---")
    print("Simulando 4 usuarios trabajando al mismo tiempo (2 escribiendo, 2 leyendo)...")
    
    threads = []
    # 2 hilos que escriben
    threads.append(threading.Thread(target=thread_escritor_habitacion, args=(1, 50)))
    threads.append(threading.Thread(target=thread_escritor_logs, args=(2, 50)))
    
    # 2 hilos que leen
    threads.append(threading.Thread(target=thread_lector, args=(3, 100)))
    threads.append(threading.Thread(target=thread_lector, args=(4, 100)))

    start_time = time.time()
    
    for t in threads:
        t.start()
        
    for t in threads:
        t.join()
        
    end_time = time.time()
    print(f"\n--- Test Finalizado en {end_time - start_time:.2f} segundos ---")
    print("Si todos los hilos muestran 0 errores, SQLite WAL está funcionando perfectamente.")

if __name__ == "__main__":
    run_stress_test()
