from datetime import datetime
from pathlib import Path

# Si es True, solo se simularán los cambios sin modificar el dibujo.
DRY_RUN = False

EXPORT_LOG = True
LOG_DIR = Path("logs")
LOG_FILENAME = f"changes_updated_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
LOG_PATH = LOG_DIR / LOG_FILENAME

if EXPORT_LOG:
    LOG_DIR.mkdir(exist_ok=True)


# de: desp_base = altura * 1.5
FACTOR_DESPLAZAMIENTO = 1.5

TYPE_RESIDENCIAL = "R"
TYPE_COMERCIAL = "C"
TYPE_TERRENO = "T"
TYPE_TERRENO_COMERCIAL = "TC"

# Patron base para normalizar tipos, se usará con formato para cada tipo específico.
PATRON_BASE = r"(\d*)({tipo})"

# Capas a ignorar durante la iteración de objetos en AutoCAD.
IGNORE_LAYERS = ["Defpoint", "0"]

# Entidades soportadas
SUPPORTED_ENTITIES = ["AcDbText"]
