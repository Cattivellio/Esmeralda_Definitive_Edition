import sqlite3

def migrate():
    conn = sqlite3.connect('esmeralda.db')
    cursor = conn.cursor()
    
    # Create inventario table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre VARCHAR(100) NOT NULL,
            descripcion TEXT,
            categoria VARCHAR(50) NOT NULL,
            stock_actual INTEGER DEFAULT 0,
            stock_minimo INTEGER DEFAULT 5,
            unidad_medida VARCHAR(20) DEFAULT 'unidades',
            costo_unitario FLOAT DEFAULT 0.0,
            ultima_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create movimientos_inventario table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimientos_inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            usuario_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            tipo VARCHAR(20) NOT NULL,
            motivo VARCHAR(255),
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(item_id) REFERENCES inventario(id),
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )
    """)
    
    conn.commit()
    conn.close()
    print("Migration for inventory tables complete.")

if __name__ == "__main__":
    migrate()
