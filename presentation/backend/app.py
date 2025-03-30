import sys
from pathlib import Path
from flask import Flask, render_template
from flask_cors import CORS

# 🔁 Asegura que Python reconoce la raíz
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 🚨 Importa setup_path si lo necesitas
import setup_path

# ✅ Especificamos la carpeta donde están los templates
template_path = Path(__file__).resolve().parent / "templates"
app = Flask(__name__, template_folder=str(template_path))
CORS(app)

# 🎯 Ruta de bienvenida que muestra el frontend
@app.route("/")
def home():
    return render_template("index.html")

# 📡 API
from presentation.backend.routes import api_blueprint
from config.settings import settings
app.register_blueprint(api_blueprint, url_prefix="/api")

# 🚀 Ejecutar
if __name__ == "__main__":
    app.run(host=settings.API_HOST, port=settings.API_PORT, debug=settings.API_DEBUG)
