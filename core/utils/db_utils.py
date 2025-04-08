import sqlite3

def obtener_proyectos_inmobiliarios():
    """
    Consulta la base de datos SQLite y retorna un resumen de proyectos inmobiliarios.
    """
    try:
        conn = sqlite3.connect("data/inmuebles.db")
        c = conn.cursor()
        c.execute("SELECT nombre, ubicacion, precio, descripcion FROM proyectos")
        filas = c.fetchall()
        conn.close()

        if not filas:
            return "No se encontraron proyectos inmobiliarios en la base de datos."

        # Crear un resumen para cada proyecto
        resumen = "\n".join([
            f"{nombre} - {ubicacion} - {precio}.\n  Descripción: {descripcion}"
            for nombre, ubicacion, precio, descripcion in filas
        ])
        return resumen
    except Exception as e:
        return f"Error al consultar la base de datos: {e}"
