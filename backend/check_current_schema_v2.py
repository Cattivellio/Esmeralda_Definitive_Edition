import sqlite3

def check_schema():
    conn = sqlite3.connect('esmeralda.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(habitaciones)")
    columns = cursor.fetchall()
    col_names = [col[1] for col in columns]
    print(f"Columns in 'habitaciones': {col_names}")
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='inspecciones'")
    table = cursor.fetchone()
    if table:
        print("\nTable 'inspecciones' exists.")
        cursor.execute("PRAGMA table_info(inspecciones)")
        cols_insp = cursor.fetchall()
        print(f"Columns in 'inspecciones': {[c[1] for c in cols_insp]}")
    else:
        print("\nTable 'inspecciones' does NOT exist.")
    
    conn.close()

if __name__ == "__main__":
    check_schema()
