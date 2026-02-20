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

    def crear_filtro_dxf(self, codigos: List[int], valores: List[Any]):
        """Crea un filtro DFX para selección rápida."""
        vt_i2 = pythoncom.VT_ARRAY | pythoncom.VT_I2
        vt_variant = pythoncom.VT_ARRAY | pythoncom.VT_VARIANT

        filtro_cod = win32com.client.VARIANT(vt_i2, codigos)
        filtro_val = win32com.client.VARIANT(vt_variant, valores)
        return filtro_cod, filtro_val

    def obtener_textos(self, capas_activas: set = None) -> List[Any]:
        """
        Obtiene textos usando SelectionSets nativos para máxima velocidad.
        """
        capas_activas = set()
        try:
            for i in range(self.doc.Layers.Count):
                capa = self.doc.Layers.Item(i)
                if capa.LayerOn and not capa.Freeze:
                    capas_activas.add(capa.Name)
            logger.debug(f"Capas activas: {capas_activas}")
        except Exception as e:
            logger.warning(f"No se pudieron obtener capas: {e}")

        nombre_ss = "SS_TEXTOS_PYTHON"

        try:
            self.doc.SelectionSets.Item(nombre_ss).Delete()
        except Exception:
            pass

        ss = self.doc.SelectionSets.Add(nombre_ss)

        codigos = [0]
        valores = ["Text"]

        if capas_activas:
            codigos.append(8)
            valores.append(",".join(capas_activas))

        f_cod, f_val = self.crear_filtro_dxf(codigos, valores)

        try:
            ss.Select(5, None, None, f_cod, f_val)
            objetos = [ss.Item(i) for i in range(ss.Count)]
        except Exception as e:
            logger.error(f"Error en SelectionSet: {e}")
            objetos = []
        finally:
            ss.Delete()

        return objetos

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
