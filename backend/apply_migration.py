import sqlite3

def migrate():
    conn = sqlite3.connect('esmeralda.db')
    cursor = conn.cursor()
    
    # Check if nfc_code exists in habitaciones
    cursor.execute("PRAGMA table_info(habitaciones)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'nfc_code' not in columns:
        print("Adding 'nfc_code' to 'habitaciones'...")
        cursor.execute("ALTER TABLE habitaciones ADD COLUMN nfc_code VARCHAR(50)")
        print("Column added.")
    else:
        print("'nfc_code' already exists.")
    
    # Ensure inspecciones exists (though create_all should have handled it)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='inspecciones'")
    if not cursor.fetchone():
        print("Creating 'inspecciones' table manually...")
        cursor.execute("""
            CREATE TABLE inspecciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habitacion_id INTEGER NOT NULL,
                usuario_id INTEGER NOT NULL,
                fecha DATETIME,
                telefono VARCHAR(10),
                televisor VARCHAR(10),
                aire_acondicionado VARCHAR(10),
                luces VARCHAR(10),
                cama VARCHAR(10),
                ducha_agua VARCHAR(10),
                observaciones TEXT,
                foto_url VARCHAR(255),
                FOREIGN KEY(habitacion_id) REFERENCES habitaciones(id),
                FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
            )
        """)
        print("Table 'inspecciones' created.")
    else:
        print("Table 'inspecciones' already exists.")
        
    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
