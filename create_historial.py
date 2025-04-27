import sqlite3
import os

# Crear la tabla historial si no existe
def crear_tabla_historial():
    if not os.path.exists("data"):
        os.makedirs("data")
    conn = sqlite3.connect("data/inmuebles.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS historial (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id TEXT NOT NULL,
            call_name TEXT NOT NULL,
            transcriptions TEXT,
            emotions TEXT,
            suggestions TEXT
        )
    ''')
    conn.commit()
    conn.close()

crear_tabla_historial()
