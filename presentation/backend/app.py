import sys
from pathlib import Path
from flask import Flask
from flask_cors import CORS

# Garantiza de forma definitiva que Python reconozca la raíz y todas las carpetas
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# IMPORTANTE: Importar aquí explícitamente setup_path
import setup_path

from presentation.backend.routes import api_blueprint
from config.settings import settings

app = Flask(__name__)
CORS(app)

app.register_blueprint(api_blueprint, url_prefix="/api")

if __name__ == "__main__":
    app.run(host=settings.API_HOST, port=settings.API_PORT, debug=settings.API_DEBUG)
