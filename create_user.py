import sqlite3
import os
from werkzeug.security import generate_password_hash # Importa la función para hashear

# Asegurarse de que exista la carpeta 'data'
if not os.path.exists("data"):
    os.makedirs("data") # [cite: 14]

# Conectar a la base de datos
conn = sqlite3.connect("data/inmuebles.db") # Puedes usar la misma BD o una nueva
c = conn.cursor()

# Crear la tabla 'usuarios'
c.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )
''')

# --- Opcional: Insertar un usuario de ejemplo ---
# Es MUY importante hashear la contraseña antes de guardarla
# Nunca guardes contraseñas en texto plano
try:
    # Genera un hash seguro para la contraseña 'password123'
    hashed_password = generate_password_hash('password123', method='pbkdf2:sha256')
    c.execute("INSERT INTO usuarios (email, password_hash) VALUES (?, ?)",
              ('admin@example.com', hashed_password))
    print("Usuario 'admin@example.com' insertado con contraseña hasheada.")
except sqlite3.IntegrityError:
    print("El usuario 'admin@example.com' ya existe.")


conn.commit()
conn.close()

print("Tabla 'usuarios' creada (o ya existente).")