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
    ("Residencial El Poblado", "El Poblado", "800,000,000 COP", "Condominio de lujo con amplias zonas comunes y seguridad 24 horas."),
    ("Torres de La 80", "La 80", "550,000,000 COP", "Viviendas modernas con acceso a transporte público y colegios cercanos."),
    ("Villas de Belén", "Belén", "320,000,000 COP", "Urbanización tranquila con acceso a parques y centros comerciales."),
    ("Condominio Valle del Lili", "El Tesoro", "1,200,000,000 COP", "Residencial de alto nivel con vistas panorámicas y piscinas privadas."),
    ("Parques de la Castellana", "Castellana", "400,000,000 COP", "Viviendas accesibles con parques recreativos y zonas deportivas."),
    ("Condominio Los Alcázares", "Los Alcázares", "650,000,000 COP", "Proyectos residenciales con acabados de lujo y cercanía a universidades."),
    ("Residencial Suramérica", "Suramericana", "380,000,000 COP", "Conjunto cerrado con seguridad privada y zonas verdes."),
    ("Las Palmas de Medellín", "Las Palmas", "1,500,000,000 COP", "Exclusivas villas con vistas al valle y acceso privado a la montaña."),
    ("Residencial Bello Horizonte", "Bello Horizonte", "460,000,000 COP", "Edificación moderna con espacios amplios y zonas comerciales en el sector."),
    ("Condominio La Mota", "La Mota", "370,000,000 COP", "Viviendas familiares con buena conexión a servicios básicos."),
    ("El Horizonte", "Robledo", "300,000,000 COP", "Urbanización cerca de colegios y supermercados, ideal para familias."),
    ("Villas de los Balsos", "Los Balsos", "900,000,000 COP", "Condos de lujo con excelentes acabados y ubicación privilegiada."),
    ("Calle 10 Condos", "La Candelaria", "350,000,000 COP", "Ubicado cerca del centro, con acceso a todo tipo de servicios y transporte."),
    ("Residencial San Joaquín", "San Joaquín", "420,000,000 COP", "Conjunto de viviendas con espacios amplios y zonas recreativas."),
    ("Residencial Ciudad del Río", "Ciudad del Río", "950,000,000 COP", "Condominio en zona tranquila y de fácil acceso a la zona comercial."),
    ("Torres de la 33", "La 33", "680,000,000 COP", "Edificio residencial con excelente vista a la ciudad y espacios modernos."),
    ("Viviendas del Parque", "Parques del Río", "750,000,000 COP", "Conjunto cerrado con parques y senderos, ideal para actividades al aire libre."),
    ("Condominio Altos del Chicó", "Chicó", "1,100,000,000 COP", "Residencial de lujo con piscina, gimnasio y zona de BBQ."),
    ("El Castillo Residencial", "El Castillo", "850,000,000 COP", "Proyectos de alto nivel con acabados de lujo y buena ubicación."),
    ("Villas San Diego", "San Diego", "420,000,000 COP", "Conjunto cerrado con seguridad y cerca de las mejores universidades."),
    ("Condominio Santa María", "Santa María de los Ángeles", "520,000,000 COP", "Complejo residencial con acceso a centros comerciales y colegios.")
]

c.executemany("INSERT INTO proyectos (nombre, ubicacion, precio, descripcion) VALUES (?, ?, ?, ?)", proyectos)

conn.commit()
conn.close()

print("Base de datos creada y datos insertados correctamente.")
