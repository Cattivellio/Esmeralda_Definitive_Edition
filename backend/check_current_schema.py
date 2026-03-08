import sqlite3

def check_schema():
    conn = sqlite3.connect('esmeralda.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(habitaciones)")
    columns = cursor.fetchall()
    print("Columns in 'habitaciones':")
    for col in columns:
        print(col)
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='inspecciones'")
    table = cursor.fetchone()
    if table:
        print("\nTable 'inspecciones' exists.")
        cursor.execute("PRAGMA table_info(inspecciones)")
        columns = cursor.fetchall()
        print("Columns in 'inspecciones':")
        for col in columns:
            print(col)
    else:
        print("\nTable 'inspecciones' does NOT exist.")
    
    conn.close()

if __name__ == "__main__":
    check_schema()
