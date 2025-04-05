import sqlite3
import os

# Asegurarse de que exista la carpeta 'data'
if not os.path.exists("data"):
    os.makedirs("data")

# Conectar a la base de datos (se creará si no existe)
conn = sqlite3.connect("data/inmuebles.db")
c = conn.cursor()

# Crear la tabla 'proyectos'
c.execute('''
    CREATE TABLE IF NOT EXISTS proyectos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        ubicacion TEXT NOT NULL,
        precio TEXT NOT NULL,
        descripcion TEXT
    )
''')

# Insertar algunos registros de ejemplo
proyectos = [
    ("Residencial El Sol", "Ciudad A", "200,000 USD", "Residencial con amplias áreas verdes y seguridad 24/7."),
    ("Condominio Vista Mar", "Ciudad B", "150,000 USD", "Condominio frente al mar con excelente vista y amenidades."),
    ("Urbanización Los Pinos", "Ciudad C", "180,000 USD", "Urbanización con colegios y centros comerciales cercanos.")
]

c.executemany("INSERT INTO proyectos (nombre, ubicacion, precio, descripcion) VALUES (?, ?, ?, ?)", proyectos)

conn.commit()
conn.close()

print("Base de datos creada y datos insertados correctamente.")
