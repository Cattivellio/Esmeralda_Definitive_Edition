import sqlite3

def migrate():
    conn = sqlite3.connect('esmeralda.db')
    cursor = conn.cursor()
    
    # Check if columns exists in usuarios
    cursor.execute("PRAGMA table_info(usuarios)")
    columns = [col[1] for col in cursor.fetchall()]
    
    new_cols = [
        ('horario', 'VARCHAR(100)'),
        ('is_present', 'BOOLEAN DEFAULT 0'),
        ('fecha_nacimiento', 'DATETIME'),
        ('fecha_ingreso', 'DATETIME'),
        ('foto_url', 'VARCHAR(255)')
    ]
    
    for col_name, col_type in new_cols:
        if col_name not in columns:
            print(f"Adding '{col_name}' to 'usuarios'...")
            cursor.execute(f"ALTER TABLE usuarios ADD COLUMN {col_name} {col_type}")
            print(f"Column '{col_name}' added.")
        else:
            print(f"'{col_name}' already exists.")
            
    conn.commit()
    conn.close()
    print("Migration of 'usuarios' table complete.")

if __name__ == "__main__":
    migrate()
