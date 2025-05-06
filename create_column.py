# Opcional: Script para actualizar la tabla (ejecutar una sola vez)
import sqlite3
import os

DB_PATH = "data/inmuebles.db"

def add_ranked_suggestions_column():
    if not os.path.exists("data"):
        print("La carpeta 'data' no existe. Asegúrate de que la base de datos esté en la ubicación correcta.")
        return

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        print(f"Conectado a {DB_PATH}")

        # Verificar si la columna ya existe
        c.execute("PRAGMA table_info(historial)")
        columns = [col[1] for col in c.fetchall()]

        if 'ranked_suggestions' not in columns:
            print("Añadiendo columna 'ranked_suggestions' a la tabla 'historial'...")
            # Añadir la nueva columna. Usamos TEXT para guardar el JSON.
            c.execute("ALTER TABLE historial ADD COLUMN ranked_suggestions TEXT")
            conn.commit()
            print("Columna 'ranked_suggestions' añadida exitosamente.")
        else:
            print("La columna 'ranked_suggestions' ya existe.")

    except sqlite3.Error as e:
        print(f"Error de base de datos al intentar añadir la columna: {e}")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
    finally:
        if conn:
            conn.close()
            print("Conexión cerrada.")

if __name__ == "__main__":
    add_ranked_suggestions_column()