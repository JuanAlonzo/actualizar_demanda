import math
from tqdm import tqdm
from core.config import DRY_RUN
from core.cliente_acad import ClienteAutoCAD
from core.logica_texto import normalizar_tipo, normalizar_terreno, analizar_combinacion
from core.logger import setup_logger

logger = setup_logger()


def main():
    logger.info(
        f"INICIANDO PROCESO - MODO: {'SIMULACIÓN (DRY RUN)' if DRY_RUN else 'EJECUCIÓN REAL'}"
    )

    # Conexión e Inicialización
    try:
        cad = ClienteAutoCAD()
        print(f"Conexión exitosa a: {cad.doc.Name}.")
        logger.info(f"Conexión exitosa a: {cad.doc.Name}.")
    except Exception as e:
        logger.critical(f"Error fatal: {e}")
        return

    # Preparar el entorno
    if not DRY_RUN:
        cad.iniciar_undo()

    # Contadores para el reporte final
    stats = {"procesados": 0, "separados": 0, "modificados": 0, "errores": 0}

    try:
        # 3. Obtener textos de forma eficiente
        textos = cad.obtener_textos()
        logger.info(f"ℹ Se encontraron {len(textos)} textos en el modelo.")

        with tqdm(
            textos,
            desc="Procesando",
            unit="txt",
            colour="green",
            dynamic_ncols=True,
        ) as pbar:
            # 4. Bucle Principal de Procesamiento
            for obj in pbar:
                try:
                    # Extraer datos básicos
                    texto_original = obj.TextString
                    texto_upper = texto_original.upper().strip()
                    altura = obj.Height

                    stats["procesados"] += 1

                    # CASO 1: Combinaciones (Ej: "R/C")
                    if "/" in texto_upper:
                        resultado = analizar_combinacion(texto_upper)

                        if resultado:
                            nuevos_txt = [r[0] for r in resultado]
                            logger.info(
                                f"🔄 Separando: '{texto_original}' -> {nuevos_txt}"
                            )
                            pbar.set_postfix_str(f"Separado: {texto_original}")

                            if not DRY_RUN:
                                origen = obj.InsertionPoint
                                rotacion = obj.Rotation
                                capa = obj.Layer

                                for texto_nuevo, factor_desp in resultado:
                                    distancia = altura * factor_desp
                                    x, y, z = origen
                                    delta_x = distancia * math.cos(rotacion)
                                    delta_y = distancia * math.sin(rotacion)
                                    nuevo_punto = (x + delta_x, y + delta_y, z)

                                    # Crear el nuevo texto
                                    nuevo_obj = cad.crear_texto(
                                        texto_nuevo, nuevo_punto, altura, capa, rotacion
                                    )
                                    cad.copiar_propiedades(obj, nuevo_obj)

                                # Borrar el original compuesto
                                obj.Delete()

                            stats["separados"] += 1

                    # Caso 2: Textos Simples (Ej: "2R", "C", "TC")
                    elif any(x in texto_upper for x in ["R", "C", "T", "TC"]):
                        nuevo_texto = texto_upper

                        if "TC" in texto_upper:
                            nuevo_texto = normalizar_terreno(texto_upper, "TC")
                        elif "T" in texto_upper:
                            nuevo_texto = normalizar_terreno(texto_upper, "T")
                        elif "R" in texto_upper:
                            nuevo_texto = normalizar_tipo(texto_upper, "R")
                        elif "C" in texto_upper:
                            nuevo_texto = normalizar_tipo(texto_upper, "C")

                        if nuevo_texto != texto_upper:
                            if not DRY_RUN:
                                obj.TextString = nuevo_texto

                            logger.info(
                                f"✏️ Normalizado: '{texto_original}' -> '{nuevo_texto}'"
                            )
                            pbar.set_postfix_str(f"Normalizado: {nuevo_texto}")
                            stats["modificados"] += 1

                except Exception as e_obj:
                    logger.warning(
                        f"Error procesando objeto ID {getattr(obj, 'Handle', '?')}: {e_obj}"
                    )
                    stats["errores"] += 1

    except Exception as e_gral:
        # Usamos 'error' con exc_info=True para que guarde el Traceback completo en el archivo
        logger.error(f"Error general en el bucle: {e_gral}", exc_info=True)

    finally:
        if not DRY_RUN:
            cad.terminar_undo()

        # Reporte Final
        resumen = (
            f"\n{'=' * 30}\n"
            f"RESUMEN FINAL\n"
            f"{'=' * 30}\n"
            f"Total Procesados:  {stats['procesados']}\n"
            f"Separados (R/C):   {stats['separados']}\n"
            f"Modificados (Txt): {stats['modificados']}\n"
            f"Errores:           {stats['errores']}\n"
            f"{'=' * 30}"
        )
        print(resumen)
        logger.info(resumen)

        input("Finalizado. Presione Enter para salir...")


if __name__ == "__main__":
    main()
