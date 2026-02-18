import re
from .config import PATRON_BASE
from typing import List, Tuple, Optional


def normalizar_tipo(texto: str, tipo: str = "R") -> str:
    """
    Normaliza texto manteniendo el número si existe, o agregando '1'.
    Ej: "2R" -> "2R", "R" -> "1R", "C" -> "1C"
    """
    texto_upper = texto.strip().upper()
    match = re.search(PATRON_BASE.format(tipo=tipo), texto_upper)

    if match:
        num = match.group(1)
        return f"{num if num else '1'}{tipo}"

    return f"1{tipo}"


def normalizar_terreno(texto: str, tipo: str) -> str:
    """
    Para Terrenos (T, TC), la regla de negocio es forzar siempre '1'.
    Ej: "2T" -> "1T" (Ignora el 2 original según tu script legacy)
    """
    return f"1{tipo}"


def analizar_combinacion(texto: str) -> Optional[List[Tuple[str, float]]]:
    """
    Analiza una cadena con '/' (ej: "R/C") y determina qué parte es qué.

    Retorna: Una lista de tuplas [(TextoNormalizado, FactorDesplazamiento)]
    o None si no es válido.

    Nota: El FactorDesplazamiento es un multiplicador.
    0 = Posición original.
    1.5 = Desplazado (según tu variable desp_base).
    """
    partes = texto.split("/")
    if len(partes) != 2:
        return None

    p1 = partes[0].strip().upper()
    p2 = partes[1].strip().upper()

    resultado = []

    # --- Lógica de detección (Portado de update_demand.py) ---

    # Analizar primera parte (Posición 0)
    if "R" in p1 and "C" not in p1:
        resultado.append((normalizar_tipo(p1, "R"), 0.0))
    elif "C" in p1 and "TC" not in p1:
        resultado.append((normalizar_tipo(p1, "C"), 0.0))

    # Analizar segunda parte (Posición Desplazada = 1.5)
    # Usamos 1.5 como factor abstracto, en el main se multiplicará por la altura
    factor_desp = 1.5

    if "R" in p2 and "C" not in p2:
        resultado.append((normalizar_tipo(p2, "R"), factor_desp))
    elif "C" in p2 and "TC" not in p2:
        resultado.append((normalizar_tipo(p2, "C"), factor_desp))

    # Validación: Debemos haber identificado ambas partes correctamente
    if len(resultado) == 2:
        return resultado
    return None
