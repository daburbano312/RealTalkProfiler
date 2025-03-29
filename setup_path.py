import sys
from pathlib import Path

# Esto define GLOBALMENTE la raíz del proyecto para todas las importaciones
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))
