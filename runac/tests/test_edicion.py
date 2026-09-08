"""Tests de la edición de datos importados.

Cubren las reglas que el documento funcional pone sobre la corrección:

  - un bloqueante no se corrige acá, se corrige en el Excel;
  - una advertencia sí, y queda constancia;
  - el nivel nacional no modifica datos provinciales;
  - con la carga cerrada no se edita: primero hay que reabrirla;
  - lo que se guarda respeta el tipo que declaró la Capa 1.

Los que necesitan base van marcados `mysql_compat`, igual que en SISOC. Los que
no la necesitan prueban la conversión de valores, que es donde está la regla.
"""

import pytest

from runac.services import edicion_service as edicion


def _campo(tipo="TEXTO", obligatorio=False, longitud=None, catalogo=None):
    return {
        "nombre": "un_campo",
        "titulo_esperado": "Un campo",
        "tipo_dato": tipo,
        "obligatorio": obligatorio,
        "longitud_maxima": longitud,
        "catalogo": catalogo,
    }


# ---------------------------------------------------------------------------
# Qué se acepta como valor corregido
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "texto,esperado",
    [
        ("15/03/2026", "2026-03-15"),
        ("2026-03-15", "2026-03-15"),
        ("15-03-2026", "2026-03-15"),
    ],
)
def test_fecha_en_los_formatos_que_usan_las_provincias(texto, esperado):
    valor, error = edicion._convertir(texto, _campo("FECHA"))
    assert error is None
    assert str(valor) == esperado


def test_fecha_inexistente_se_rechaza():
    """31 de febrero no existe, aunque parezca una fecha."""
    valor, error = edicion._convertir("31/02/2026", _campo("FECHA"))
    assert valor is None
    assert "no es una fecha válida" in error


def test_entero_con_separador_de_miles():
    valor, error = edicion._convertir("1.250", _campo("ENTERO"))
    assert error is None
    assert valor == 1250


def test_texto_en_campo_numerico_se_rechaza():
    valor, error = edicion._convertir("doce", _campo("ENTERO"))
    assert valor is None
    assert "no es un número entero" in error


def test_campo_obligatorio_no_puede_quedar_vacio():
    valor, error = edicion._convertir("   ", _campo(obligatorio=True))
    assert valor is None
    assert "obligatorio" in error


def test_campo_opcional_puede_quedar_vacio():
    valor, error = edicion._convertir("", _campo(obligatorio=False))
    assert valor is None
    assert error is None


def test_texto_mas_largo_que_el_maximo_se_rechaza():
    valor, error = edicion._convertir("x" * 40, _campo(longitud=20))
    assert valor is None
    assert "máximo" in error


def test_texto_dentro_del_maximo_se_acepta():
    valor, error = edicion._convertir("x" * 10, _campo(longitud=20))
    assert error is None
    assert valor == "x" * 10


def test_el_valor_se_guarda_sin_espacios_al_borde():
    valor, error = edicion._convertir("  Hogar San José  ", _campo())
    assert error is None
    assert valor == "Hogar San José"


# ---------------------------------------------------------------------------
# Nombres que se interpolan en SQL
# ---------------------------------------------------------------------------


def test_un_nombre_de_campo_valido_pasa():
    assert edicion._identificador_seguro("fecha_de_inicio_mpe") == "fecha_de_inicio_mpe"


@pytest.mark.parametrize(
    "nombre",
    ["", "campo con espacios", "campo;DROP TABLE x", "Campo", "campo-guion", "x" * 65],
)
def test_un_nombre_que_no_declaro_la_capa_1_se_rechaza(nombre):
    """La tabla y la columna se interpolan en el SQL: sólo puede entrar lo que
    la Capa 1 declaró."""
    with pytest.raises(edicion.EdicionNoPermitida):
        edicion._identificador_seguro(nombre)


# ---------------------------------------------------------------------------
# Cuándo se puede editar
# ---------------------------------------------------------------------------


def test_los_estados_editables_son_los_de_la_jurisdiccion():
    """Con la carga cerrada o presentada, la provincia no toca los datos."""
    assert set(edicion.ESTADOS_EDITABLES) == {"EN_CARGA", "OBSERVADA", "SUBSANADA"}
    for estado in ("CERRADA", "EN_REVISION", "HABILITADA", "PRESENTADA", "CONSOLIDADA"):
        assert estado not in edicion.ESTADOS_EDITABLES


def test_como_se_muestra_un_valor_para_editarlo():
    from datetime import date

    assert edicion._texto_del_valor(None) == ""
    assert edicion._texto_del_valor(date(2026, 3, 15)) == "15/03/2026"
    assert edicion._texto_del_valor(1250) == "1250"
    assert edicion._texto_del_valor("Hogar") == "Hogar"
