"""Tests del diseño responsive.

El operador provincial carga desde donde esté: la pantalla chica no es un caso
degradado, es el primero. Estos tests verifican que lo que hace posible el uso en
teléfono esté presente en el HTML, porque es fácil romperlo sin darse cuenta al
editar una plantilla.

No reemplazan mirar la pantalla, pero detectan las regresiones estructurales:
una tabla sin etiquetas de celda es ilegible en un teléfono, y no se nota hasta
que alguien lo abre en uno.
"""

import glob
import os
import re

import pytest

PLANTILLAS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "templates",
    "runac",
)


def _leer(nombre):
    with open(os.path.join(PLANTILLAS, nombre), encoding="utf-8") as fh:
        return fh.read()


def _todas():
    return sorted(glob.glob(os.path.join(PLANTILLAS, "*.html")))


# ---------------------------------------------------------------------------
# La base
# ---------------------------------------------------------------------------


def test_declara_el_viewport():
    """Sin esto, el teléfono renderiza como si fuera un escritorio angosto."""
    base = _leer("base.html")
    assert 'name="viewport"' in base
    assert "width=device-width" in base


def test_el_menu_se_pliega_en_pantalla_chica():
    """Cinco secciones no entran en una barra de 375 píxeles."""
    base = _leer("base.html")
    assert "navbar-toggler" in base
    assert "navbar-collapse" in base
    assert 'data-bs-toggle="collapse"' in base


def test_es_mobile_first():
    """Las reglas base son para teléfono; las medias sólo suman ancho.

    Un `max-width` significaría que el escritorio es el caso base y el teléfono
    la excepción, que es justo al revés de lo pedido.
    """
    base = _leer("base.html")
    anchos_minimos = re.findall(r"@media \(min-width: (\d+)px\)", base)
    anchos_maximos = re.findall(r"@media \(max-width: (\d+)px\)", base)
    assert anchos_minimos, "no hay media queries de ancho mínimo"
    assert not anchos_maximos, "hay media queries de ancho máximo: no es mobile first"


def test_los_cortes_son_telefono_tablet_escritorio():
    base = _leer("base.html")
    cortes = sorted(int(a) for a in re.findall(r"@media \(min-width: (\d+)px\)", base))
    assert 768 in cortes, "falta el corte de tablet"
    assert 992 in cortes, "falta el corte de escritorio"


def test_nada_desborda_a_lo_ancho():
    base = _leer("base.html")
    assert "overflow-x: hidden" in base


def test_los_controles_se_tocan_con_el_dedo():
    """Un botón de 24 píxeles no se toca: se intenta tocar."""
    base = _leer("base.html")
    assert ".btn { min-height" in base
    assert 'input[type="file"], .form-control, .form-select { min-height' in base


# ---------------------------------------------------------------------------
# Las tablas
# ---------------------------------------------------------------------------


def test_las_tablas_se_convierten_en_fichas():
    base = _leer("base.html")
    assert ".tabla-ficha thead { display: none; }" in base
    assert "content: attr(data-etiqueta)" in base


def test_las_fichas_vuelven_a_ser_tabla_en_pantalla_grande():
    """La ficha es para el teléfono; en la tablet la tabla vuelve a ser tabla."""
    base = _leer("base.html")
    corte = base.index("@media (min-width: 768px)")
    assert "display: table-header-group" in base[corte:]
    assert "display: table-cell" in base[corte:]


@pytest.mark.parametrize(
    "plantilla",
    [
        "cargar.html",
        "resultado.html",
        "detalle.html",
        "revision.html",
        "estructura.html",
    ],
)
def test_toda_tabla_de_datos_es_ficha_en_el_telefono(plantilla):
    html = _leer(plantilla)
    for tabla in re.findall(r"<table[^>]*>", html):
        assert "tabla-ficha" in tabla, f"{plantilla}: tabla sin tabla-ficha"


@pytest.mark.parametrize(
    "plantilla",
    ["cargar.html", "resultado.html", "detalle.html", "revision.html"],
)
def test_las_celdas_llevan_el_nombre_de_su_columna(plantilla):
    """Sin data-etiqueta, en el teléfono la ficha es una lista de valores sueltos
    sin decir qué es cada uno."""
    html = _leer(plantilla)
    assert "data-etiqueta" in html, f"{plantilla}: ninguna celda etiquetada"


def test_el_encabezado_queda_fijo_al_desplazarse():
    """El scroll es del contenedor: sin altura máxima, `sticky` no tiene efecto."""
    base = _leer("base.html")
    assert ".tabla-scroll { max-height:" in base
    assert "overflow-y: auto" in base
    assert ".tabla-scroll thead th {" in base
    assert "position: sticky" in base


# ---------------------------------------------------------------------------
# Impresión
# ---------------------------------------------------------------------------


def test_el_comprobante_se_imprime_sin_la_navegacion():
    base = _leer("base.html")
    assert "@media print" in base
    corte = base.index("@media print")
    assert ".navbar" in base[corte:]


def test_ninguna_plantilla_quedo_con_comentarios_multilinea():
    """Los comentarios {# #} de Django son de UNA línea: uno multilínea se
    imprime tal cual en la pantalla. Ya pasó una vez."""
    for ruta in _todas():
        with open(ruta, encoding="utf-8") as fh:
            html = fh.read()
        for comentario in re.findall(r"\{#(.*?)#\}", html, re.S):
            assert "\n" not in comentario, (
                f"{os.path.basename(ruta)}: comentario multilínea, "
                "usar {% comment %} en su lugar"
            )
