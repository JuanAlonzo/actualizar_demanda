import unittest
from core.logica_texto import normalizar_tipo, normalizar_terreno, analizar_combinacion


class TestLogicaNegocio(unittest.TestCase):
    # --- PRUEBAS PARA normalizar_tipo ---

    def test_normalizar_basico_r(self):
        """Caso simple: 'R' debe convertirse en '1R'."""
        entrada = "R"
        resultado = normalizar_tipo(entrada, "R")
        self.assertEqual(resultado, "1R")

    def test_normalizar_con_numero(self):
        """Caso con número: '5C' debe quedarse como '5C'."""
        entrada = "5C"
        resultado = normalizar_tipo(entrada, "C")
        self.assertEqual(resultado, "5C")

    def test_normalizar_espacios_y_minusculas(self):
        """Caso sucio: '  r ' debe limpiarse a '1R'."""
        entrada = "  r "
        resultado = normalizar_tipo(entrada, "R")
        self.assertEqual(resultado, "1R")

    # --- PRUEBAS PARA normalizar_terreno ---

    def test_terreno_fuerza_uno(self):
        """Regla de negocio: Terrenos siempre son 1, incluso si dicen '2T'."""
        entrada = "2T"
        resultado = normalizar_terreno(entrada, "T")
        self.assertEqual(resultado, "1T")

    def test_terreno_comercial(self):
        """Caso TC: 'TC' -> '1TC'."""
        entrada = "TC"
        resultado = normalizar_terreno(entrada, "TC")
        self.assertEqual(resultado, "1TC")

    # --- PRUEBAS PARA analizar_combinacion (LA MÁS IMPORTANTE) ---

    def test_combinacion_rc_simple(self):
        """Prueba estándar 'R/C'."""
        entrada = "R/C"
        resultado = analizar_combinacion(entrada)

        # Esperamos una lista de 2 tuplas
        self.assertIsNotNone(resultado)
        self.assertEqual(len(resultado), 2)

        # R debe estar en posición 0 (factor 0.0)
        self.assertEqual(resultado[0], ("1R", 0.0))
        # C debe estar desplazado (factor 1.5)
        self.assertEqual(resultado[1], ("1C", 1.5))

    def test_combinacion_cr_invertida(self):
        """Prueba invertida 'C/R'. El orden importa."""
        entrada = "C/R"
        resultado = analizar_combinacion(entrada)

        # C debe estar en posición 0
        self.assertEqual(resultado[0], ("1C", 0.0))
        # R debe estar desplazado
        self.assertEqual(resultado[1], ("1R", 1.5))

    def test_combinacion_con_numeros(self):
        """Prueba compleja '2R/3C'."""
        entrada = "2R/3C"
        resultado = analizar_combinacion(entrada)

        self.assertEqual(resultado[0], ("2R", 0.0))
        self.assertEqual(resultado[1], ("3C", 1.5))

    def test_combinacion_invalida(self):
        """Si le paso basura, debe retornar None."""
        self.assertIsNone(analizar_combinacion("R"))  # Falta el slash
        self.assertIsNone(
            analizar_combinacion("T/Z")
        )  # Tipos no soportados por la lógica actual


if __name__ == "__main__":
    unittest.main()
