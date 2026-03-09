import sqlite3

conn = sqlite3.connect('esmeralda.db')
cursor = conn.cursor()
try:
    cursor.execute("ALTER TABLE estancias ADD COLUMN camarera_checkout_id INTEGER REFERENCES usuarios(id)")
    conn.commit()
    print("Column 'camarera_checkout_id' added successfully.")
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
