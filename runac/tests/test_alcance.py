"""Tests del alcance por jurisdicción: cada usuario provincial, sobre la suya.

Surgen de un problema real, verificado el 25-09-2026: un operador de Chubut
que escribía la dirección a mano veía el detalle, bajaba los errores y veía
los datos de una importación de Chaco; y con el selector de prueba podía
cargar y corregir en cualquier provincia.
"""

from types import SimpleNamespace

import pytest
from django.http import Http404
from django.test import RequestFactory

from runac.services import alcance_service as alcance
from runac.views.carga import jurisdiccion_en_curso


def _usuario(rol=None, jurisdiccion=None):
    grupos = [
        g for g in (rol, f"jurisdiccion:{jurisdiccion}" if jurisdiccion else None) if g
    ]
    return SimpleNamespace(
        is_authenticated=True,
        is_superuser=False,
        groups=SimpleNamespace(values_list=lambda *a, **k: grupos),
        get_username=lambda: rol or "anonimo",
    )


OPERADOR_CHUBUT = _usuario("operador_provincial", "Chubut")
REVISOR = _usuario("revisor_nacional")


def _pedido(usuario, sesion=None, **params):
    pedido = RequestFactory().get("/", params)
    pedido.user = usuario
    pedido.session = dict(sesion or {})
    return pedido


# ---------------------------------------------------------------------------
# Sobre qué jurisdicción se trabaja
# ---------------------------------------------------------------------------


def test_el_provincial_trabaja_sobre_la_suya_aunque_pida_otra():
    assert (
        jurisdiccion_en_curso(_pedido(OPERADOR_CHUBUT, jurisdiccion="Chaco"))
        == "Chubut"
    )


def test_el_provincial_no_hereda_una_eleccion_de_la_sesion():
    """El selector guardaba la elegida en la sesión, y ahí se quedaba."""
    pedido = _pedido(OPERADOR_CHUBUT, sesion={"jurisdiccion": "Chaco"})
    assert jurisdiccion_en_curso(pedido) == "Chubut"


def test_el_nacional_elige_y_se_recuerda():
    pedido = _pedido(REVISOR, jurisdiccion="Chaco")
    assert jurisdiccion_en_curso(pedido) == "Chaco"
    assert pedido.session["jurisdiccion"] == "Chaco"


def test_el_nacional_no_elige_una_que_no_existe():
    pedido = _pedido(REVISOR, jurisdiccion="Atlántida")
    assert jurisdiccion_en_curso(pedido) != "Atlántida"


# ---------------------------------------------------------------------------
# Lo de otra jurisdicción no existe
# ---------------------------------------------------------------------------


def test_lo_propio_se_ve():
    assert alcance.es_suya(OPERADOR_CHUBUT, "Chubut")


def test_lo_ajeno_no():
    assert not alcance.es_suya(OPERADOR_CHUBUT, "Chaco")


def test_el_nacional_ve_todas():
    assert alcance.es_suya(REVISOR, "Chaco")


def test_lo_que_no_existe_no_es_de_nadie():
    assert not alcance.es_suya(REVISOR, None)


def test_una_importacion_de_otra_jurisdiccion_da_404(mocker):
    mocker.patch.object(alcance, "jurisdiccion_de_la_importacion", return_value="Chaco")
    with pytest.raises(Http404):
        alcance.exigir_importacion(OPERADOR_CHUBUT, 6)


def test_una_presentacion_de_otra_jurisdiccion_da_404(mocker):
    mocker.patch.object(
        alcance, "jurisdiccion_de_la_presentacion", return_value="Chaco"
    )
    with pytest.raises(Http404):
        alcance.exigir_presentacion(OPERADOR_CHUBUT, 6)


def test_una_observacion_de_otra_jurisdiccion_da_404(mocker):
    mocker.patch.object(alcance, "presentacion_de_la_observacion", return_value=6)
    mocker.patch.object(
        alcance, "jurisdiccion_de_la_presentacion", return_value="Chaco"
    )
    with pytest.raises(Http404):
        alcance.exigir_observacion(OPERADOR_CHUBUT, 1)


def test_una_observacion_que_no_existe_da_404(mocker):
    mocker.patch.object(alcance, "presentacion_de_la_observacion", return_value=None)
    with pytest.raises(Http404):
        alcance.exigir_observacion(REVISOR, 1)


def test_la_propia_pasa(mocker):
    mocker.patch.object(
        alcance, "jurisdiccion_de_la_importacion", return_value="Chubut"
    )
    assert alcance.exigir_importacion(OPERADOR_CHUBUT, 1) == "Chubut"
