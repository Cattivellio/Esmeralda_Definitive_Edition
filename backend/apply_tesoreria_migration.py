import sqlite3
import os

db_path = "backend/esmeralda.db"

def apply_migration():
    if not os.path.exists(db_path):
        print(f"Error: Database {db_path} not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 1. Create cuentas table
        print("Creating cuentas table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cuentas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            moneda TEXT DEFAULT 'USD',
            saldo_inicial REAL DEFAULT 0.0,
            color TEXT DEFAULT '#36ea7e',
            activo BOOLEAN DEFAULT 1
        )
        """)

        # 2. Add cuenta_id to metodos_pago
        print("Adding cuenta_id to metodos_pago...")
        try:
            cursor.execute("ALTER TABLE metodos_pago ADD COLUMN cuenta_id INTEGER REFERENCES cuentas(id)")
        except sqlite3.OperationalError:
            print("Column cuenta_id already exists in metodos_pago or other error.")

        # 3. Create transacciones table
        print("Creating transacciones table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS transacciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            monto REAL NOT NULL,
            moneda TEXT DEFAULT 'USD',
            cuenta_id INTEGER NOT NULL REFERENCES cuentas(id),
            cuenta_destino_id INTEGER REFERENCES cuentas(id),
            descripcion TEXT,
            justificacion TEXT,
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
            usuario_id INTEGER REFERENCES usuarios(id),
            pago_id INTEGER REFERENCES pagos(id),
            extra_id INTEGER REFERENCES ingresos_extras.id,
            referencia TEXT
        )
        """)

        # 4. Initialize default account if none exists
        cursor.execute("SELECT COUNT(*) FROM cuentas")
        if cursor.fetchone()[0] == 0:
            print("Initializing default account 'Caja Principal'...")
            cursor.execute("INSERT INTO cuentas (nombre, moneda, saldo_inicial, color) VALUES (?, ?, ?, ?)", 
                         ("Caja Principal", "USD", 0.0, "#36ea7e"))
            default_id = cursor.lastrowid
            
            # Link all current payment methods to this account
            print(f"Linking existing payment methods to account ID {default_id}...")
            cursor.execute("UPDATE metodos_pago SET cuenta_id = ?", (default_id,))

        conn.commit()
        print("Migration applied successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Error applying migration: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    apply_migration()
