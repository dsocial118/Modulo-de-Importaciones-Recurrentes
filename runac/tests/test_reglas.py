"""Editar una regla desde la pantalla: lo que no puede fallar.

No tocan la base, igual que el resto de la suite: la estructura la crea la
Capa 1 y no Django. Lo que se prueba acá es **la decisión**, que es donde un
error se paga caro: un límite mal interpretado rechaza datos correctos, y ése
es el peor defecto que puede tener el módulo.
"""

import pytest

from runac.services import reglas_service as rs


class TestLimites:
    """`_limites()` traduce lo que se escribió en la pantalla a dos números."""

    def test_los_dos_extremos(self):
        assert rs._limites("0", "200") == {"minimo": 0, "maximo": 200}

    def test_un_extremo_solo_es_valido(self):
        """«No puede ser negativo», sin techo, es una regla legítima."""
        assert rs._limites("0", "") == {"minimo": 0}
        assert rs._limites(None, "200") == {"maximo": 200}

    def test_el_cero_es_un_limite_y_no_un_vacio(self):
        """Si el cero se tomara como vacío, «entre 0 y 200» perdería el piso."""
        assert rs._limites(0, 200) == {"minimo": 0, "maximo": 200}
        assert "minimo" in rs._limites("0", "200")

    def test_decimales_con_coma(self):
        """Se escribe como se escribe en castellano."""
        assert rs._limites("1,5", "9,5") == {"minimo": 1.5, "maximo": 9.5}

    def test_los_enteros_no_quedan_con_punto_cero(self):
        """Un 200.0 en el mensaje de error se lee como un error del sistema."""
        limites = rs._limites("0", "200")
        assert isinstance(limites["maximo"], int)

    def test_el_minimo_no_puede_superar_al_maximo(self):
        with pytest.raises(rs.NoSePuede):
            rs._limites("500", "10")

    def test_lo_que_no_es_numero_se_rechaza(self):
        with pytest.raises(rs.NoSePuede):
            rs._limites("ocho", "")

    def test_minimo_igual_a_maximo_es_valido(self):
        """Un único valor admitido es raro, pero no es un error."""
        assert rs._limites("7", "7") == {"minimo": 7, "maximo": 7}


class TestDescripcion:
    """El texto que ve la persona tiene que decir lo que la regla hace."""

    def test_los_dos_extremos(self):
        assert rs._descripcion({"minimo": 0, "maximo": 200}) == (
            "El valor debe estar entre 0 y 200."
        )

    def test_solo_techo(self):
        assert (
            rs._descripcion({"maximo": 200}) == "El valor no puede ser mayor que 200."
        )

    def test_solo_piso(self):
        assert rs._descripcion({"minimo": 0}) == "El valor no puede ser menor que 0."

    def test_sin_limites_no_inventa_texto(self):
        assert rs._descripcion({}) == ""


class TestSeveridad:
    """Sólo dos valores, y no se aceptan otros."""

    def test_las_dos_que_existen(self):
        assert rs.SEVERIDADES == ("ADVERTENCIA", "BLOQUEANTE")

    def test_cualquier_otra_cosa_se_rechaza_antes_de_tocar_la_base(self):
        """Falla por la severidad, no por no encontrar la aplicación."""
        with pytest.raises(rs.NoSePuede) as e:
            rs.cambiar_severidad(1, "GRAVE")
        assert "severidad" in str(e.value)
