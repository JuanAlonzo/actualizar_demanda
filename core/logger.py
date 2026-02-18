import logging
import sys
from core.config import LOG_PATH


def setup_logger():
    """
    Configura el sistema de logging con dos salidas:
    1. Archivo: Detallado con fecha y hora.
    2. Consola: Limpio (solo el mensaje) para mantener la estética de emojis.
    """
    # Crear el logger principal
    logger = logging.getLogger("AutoCAD_Updater")
    logger.setLevel(logging.DEBUG)  # Capturamos todo

    # Evitar duplicados si se llama varias veces
    if logger.handlers:
        return logger

    # --- HANDLER 1: ARCHIVO (Detallado) ---
    file_handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    # Formato: [Fecha] [Nivel] [Modulo] Mensaje
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)

    # --- HANDLER 2: CONSOLA (Limpio) ---
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    # Formato: Solo el mensaje (para que tus emojis luzcan bien)
    console_formatter = logging.Formatter("%(message)s")
    console_handler.setFormatter(console_formatter)

    # Agregar handlers al logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
