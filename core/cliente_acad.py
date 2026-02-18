import win32com.client
import pythoncom
import logging
from typing import List, Tuple, Any

logger = logging.getLogger("AutoCAD_Updater")


class ClienteAutoCAD:
    def __init__(self):
        try:
            self.acad = win32com.client.Dispatch("AutoCAD.Application")
            self.doc = self.acad.ActiveDocument
            self.model = self.doc.ModelSpace
            self.util = self.doc.Utility
            logger.debug(f"Inicializando cliente COM para: {self.doc.Name}")
        except Exception as e:
            raise ConnectionError(f"No se pudo conectar a AutoCAD: {e}")

    def _punto_a_variant(self, punto: Tuple[float, float, float]):
        """Convierte una tupla (x,y,z) a un array de doubles compatible con COM."""
        return win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, punto)

    def iniciar_undo(self):
        self.doc.StartUndoMark()

    def terminar_undo(self):
        self.doc.EndUndoMark()

    def obtener_textos(self) -> List[Any]:
        """
        Devuelve una lista de objetos de texto usando un SelectionSet filtrado.
        Mucho más rápido que iterar todo el ModelSpace.
        """
        objetos_texto = []
        total = self.model.Count

        # Iteramos manualmente
        for i in range(total):
            try:
                item = self.model.Item(i)
                # Filtramos aquí en Python, no en AutoCAD
                if item.EntityName == "AcDbText":
                    objetos_texto.append(item)
            except Exception:
                continue

        return objetos_texto

    def crear_texto(
        self,
        texto: str,
        punto: Tuple[float, float, float],
        altura: float,
        capa: str,
        rotacion: float = 0,
    ):
        """Crea texto usando coordenadas."""
        # win32com requiere un array de coordenadas
        punto_com = self._punto_a_variant(punto)

        nuevo_obj = self.model.AddText(texto, punto_com, altura)
        nuevo_obj.Layer = capa
        nuevo_obj.Rotation = rotacion
        return nuevo_obj

    def copiar_propiedades(self, origen, destino):
        """Replica propiedades visuales básicas."""
        try:
            destino.Layer = origen.Layer
            destino.StyleName = origen.StyleName
            if origen.Color != 256:
                destino.Color = origen.Color
        except Exception as e:
            logger.warning(f"Advertencia copiando propiedades: {e}")
