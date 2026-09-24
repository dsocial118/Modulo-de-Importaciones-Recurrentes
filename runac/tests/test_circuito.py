"""Tests del circuito de carga, revisión y presentación.

Cubren las reglas del análisis funcional que no pueden romperse sin que el
circuito deje de ser el que la contraparte validó:

  - quién puede ejecutar cada acción;
  - desde qué estado;
  - que no se pueda cerrar la carga con archivos obligatorios faltantes;
  - que el nivel nacional no modifique datos provinciales.

No tocan la base: prueban la tabla de transiciones, que es donde vive la regla.
Los modelos del MVP son `managed = False` —la estructura la crea la Capa 1,
no Django—, así que los tests que necesitan datos van marcados `mysql_compat`,
igual que en SISOC.
"""

from types import SimpleNamespace

import pytest

from runac.services import circuito_service as circuito


def _usuario(rol=None, superusuario=False):
    """Un usuario mínimo: al servicio sólo le importa el rol."""
    grupos = SimpleNamespace(values_list=lambda *a, **k: [rol] if rol else [])
    return SimpleNamespace(
        is_authenticated=True,
        is_superuser=superusuario,
        groups=grupos,
        get_username=lambda: rol or "anonimo",
    )


OPERADOR = "operador_provincial"
RESPONSABLE = "responsable_provincial"
REVISOR = "revisor_nacional"
ADMIN = "administrador_nacional"


# ---------------------------------------------------------------------------
# Coherencia de la tabla de transiciones
# ---------------------------------------------------------------------------


def test_todo_estado_de_destino_esta_declarado():
    """No puede haber una acción que lleve a un estado que no existe."""
    for accion, (origenes, destino, _) in circuito.ACCIONES.items():
        assert destino in circuito.ESTADOS, f"{accion} lleva a un estado desconocido"
        for origen in origenes:
            assert origen in circuito.ESTADOS, f"{accion} sale de un estado desconocido"


def test_toda_accion_tiene_etiqueta_y_ayuda():
    """Si falta la etiqueta, el botón sale vacío en la pantalla."""
    for accion in circuito.ACCIONES:
        assert circuito.ETIQUETAS.get(accion)
        assert circuito.AYUDAS.get(accion)


def test_todo_estado_se_alcanza_o_es_el_inicial():
    """Un estado inalcanzable es un estado muerto en el circuito."""
    alcanzables = {destino for _, destino, _ in circuito.ACCIONES.values()}
    alcanzables.add("EN_CARGA")  # el inicial
    alcanzables.add("OBSERVADA")  # se llega al crear una observación
    alcanzables.add("SUBSANADA")  # se llega al responder la última observación
    assert set(circuito.ESTADOS) == alcanzables


# ---------------------------------------------------------------------------
# Quién puede hacer qué
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "estado,rol,accion_esperada",
    [
        ("EN_CARGA", RESPONSABLE, "cerrar_carga"),
        ("CERRADA", REVISOR, "abrir_revision"),
        ("EN_REVISION", REVISOR, "habilitar"),
        ("HABILITADA", RESPONSABLE, "presentar"),
        ("SUBSANADA", RESPONSABLE, "cerrar_carga"),
    ],
)
def test_el_rol_correcto_ve_su_accion(estado, rol, accion_esperada):
    acciones = circuito.acciones_disponibles({"estado": estado}, _usuario(rol))
    assert accion_esperada in [a["accion"] for a in acciones]


@pytest.mark.parametrize(
    "estado,rol,accion_prohibida",
    [
        # El operador carga y corrige, pero no cierra ni presenta.
        ("EN_CARGA", OPERADOR, "cerrar_carga"),
        ("HABILITADA", OPERADOR, "presentar"),
        # El revisor observa y habilita, pero no presenta por la provincia.
        ("HABILITADA", REVISOR, "presentar"),
        # La provincia no se autohabilita.
        ("EN_REVISION", RESPONSABLE, "habilitar"),
    ],
)
def test_el_rol_equivocado_no_ve_la_accion(estado, rol, accion_prohibida):
    acciones = circuito.acciones_disponibles({"estado": estado}, _usuario(rol))
    assert accion_prohibida not in [a["accion"] for a in acciones]


def test_no_se_puede_cerrar_la_carga_con_archivos_faltantes():
    """`listo` es falso cuando falta algún archivo obligatorio."""
    acciones = circuito.acciones_disponibles(
        {"estado": "EN_CARGA"}, _usuario(RESPONSABLE), listo=False
    )
    assert "cerrar_carga" not in [a["accion"] for a in acciones]


def test_sin_presentacion_no_hay_acciones():
    assert circuito.acciones_disponibles(None, _usuario(RESPONSABLE)) == []


def test_consolidar_no_es_una_accion_de_pantalla():
    """La consolidación la dispara el sistema, no un botón."""
    for estado in circuito.ESTADOS:
        acciones = circuito.acciones_disponibles(
            {"estado": estado}, _usuario(ADMIN, superusuario=True)
        )
        assert "consolidar" not in [a["accion"] for a in acciones]


# ---------------------------------------------------------------------------
# Reglas del documento funcional
# ---------------------------------------------------------------------------


def test_la_presentacion_es_el_ultimo_acto():
    """Sólo se presenta desde HABILITADA, es decir tras la revisión nacional."""
    origenes, _, _ = circuito.ACCIONES["presentar"]
    assert origenes == ("HABILITADA",)


def test_reabrir_la_carga_deshace_el_cierre():
    """Para reimportar después del cierre hay que reabrir, no importar encima."""
    origenes, destino, quien = circuito.ACCIONES["reabrir_carga"]
    assert destino == "EN_CARGA"
    assert "CERRADA" in origenes
    assert quien == "responsable"


def test_el_ciclo_de_subsanacion_no_tiene_tope():
    """Se puede volver a cerrar y observar cuantas veces haga falta."""
    assert "SUBSANADA" in circuito.ACCIONES["cerrar_carga"][0]
    assert "CERRADA" in circuito.ACCIONES["abrir_revision"][0]


def test_estado_legible_no_devuelve_el_codigo_crudo():
    for codigo in circuito.ESTADOS:
        assert circuito.estado_legible(codigo) != codigo


def test_estado_desconocido_no_rompe():
    assert circuito.estado_legible("INVENTADO") == "INVENTADO"
