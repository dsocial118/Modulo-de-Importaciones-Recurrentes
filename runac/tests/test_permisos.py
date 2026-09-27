"""Tests de permisos: cada rol ve y puede lo que le corresponde.

Surgen de un problema real detectado en pruebas: el operador
provincial veía en su menú la sección de revisión nacional.

Hay dos cosas distintas y las dos se prueban:

  - el **menú**, que es lo que se le ofrece a cada rol;
  - el **acceso**, que es a qué puede entrar escribiendo la dirección.

Ocultar un enlace no es un permiso.
"""

from types import SimpleNamespace

import pytest

from runac import permissions as perm


def _usuario(rol=None, superusuario=False):
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
# El menú
# ---------------------------------------------------------------------------


def test_el_operador_no_ve_la_revision_nacional():
    """El problema que originó estos tests."""
    secciones = [s["clave"] for s in perm.menu_de(_usuario(OPERADOR))]
    assert "revision" not in secciones


def test_el_revisor_no_ve_la_carga_de_archivos():
    """El nivel nacional no carga: revisa."""
    secciones = [s["clave"] for s in perm.menu_de(_usuario(REVISOR))]
    assert "cargar" not in secciones


def test_cada_rol_ve_al_menos_el_inicio():
    for rol in perm.ROLES:
        secciones = [s["clave"] for s in perm.menu_de(_usuario(rol))]
        assert "inicio" in secciones


def test_sin_rol_no_hay_menu():
    assert perm.menu_de(_usuario(None)) == []


def test_el_menu_conserva_el_orden_del_circuito():
    """El menú se lee como el recorrido: plantillas, cargar, resultado."""
    secciones = [s["clave"] for s in perm.menu_de(_usuario(OPERADOR))]
    assert secciones.index("plantillas") < secciones.index("cargar")
    assert secciones.index("cargar") < secciones.index("resultado")


# ---------------------------------------------------------------------------
# El acceso
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "rol,seccion",
    [
        (OPERADOR, "revision"),
        (RESPONSABLE, "revision"),
        (REVISOR, "cargar"),
    ],
)
def test_no_se_entra_a_una_seccion_ajena(rol, seccion):
    assert not perm.puede_entrar(_usuario(rol), seccion)


def test_el_revisor_entra_al_resultado_aunque_no_este_en_su_menu():
    """Llega desde la bandeja de revisión, con el enlace «Ver carga»."""
    usuario = _usuario(REVISOR)
    assert "resultado" not in [s["clave"] for s in perm.menu_de(usuario)]
    assert perm.puede_entrar(usuario, "resultado")


def test_una_seccion_que_no_existe_no_se_habilita():
    assert not perm.puede_entrar(_usuario(ADMIN), "inventada")


def test_toda_seccion_del_menu_es_accesible():
    """Sería un error ofrecer en el menú algo a lo que no se puede entrar."""
    for rol in perm.ROLES:
        for seccion in perm.menu_de(_usuario(rol)):
            assert perm.puede_entrar(_usuario(rol), seccion["clave"])


# ---------------------------------------------------------------------------
# Las acciones
# ---------------------------------------------------------------------------


def test_solo_el_operador_importa():
    assert perm.puede_cargar(_usuario(OPERADOR))
    assert not perm.puede_cargar(_usuario(REVISOR))


def test_solo_el_responsable_presenta():
    assert perm.puede_presentar(_usuario(RESPONSABLE))
    assert not perm.puede_presentar(_usuario(OPERADOR))
    assert not perm.puede_presentar(_usuario(REVISOR))


def test_el_nivel_nacional_no_edita_datos_provinciales():
    """Es la regla del documento: el revisor observa, no modifica."""
    assert perm.puede_editar_datos(_usuario(OPERADOR))
    assert perm.puede_editar_datos(_usuario(RESPONSABLE))
    assert not perm.puede_editar_datos(_usuario(REVISOR))
    assert not perm.puede_editar_datos(_usuario(ADMIN))


def test_solo_el_revisor_observa():
    assert perm.puede_revisar(_usuario(REVISOR))
    assert not perm.puede_revisar(_usuario(OPERADOR))


def test_toda_seccion_declara_menu_y_acceso():
    """Una sección sin declarar quedaría abierta o invisible por descuido."""
    for clave, datos in perm.SECCIONES.items():
        assert datos.get("menu") is not None, clave
        assert datos.get("acceso") is not None, clave
        assert datos.get("etiqueta"), clave
        assert datos.get("icono"), clave


# ---------------------------------------------------------------------------
# Sin sesión
# ---------------------------------------------------------------------------


def test_sin_sesion_no_se_bloquea_por_permisos():
    """Sin sesión no es un problema de permisos: falta entrar.

    Si el mixin bloqueara al usuario anónimo, el sitio devolvería 403 en la
    portada en vez de mandarlo a iniciar sesión. Ya pasó.
    """
    anonimo = SimpleNamespace(
        is_authenticated=False,
        is_superuser=False,
        groups=SimpleNamespace(values_list=lambda *a, **k: []),
    )
    assert perm.rol_de(anonimo) is None
    assert perm.menu_de(anonimo) == []
    assert not perm.puede_entrar(anonimo, "inicio")


def test_al_salir_desde_react_se_vuelve_a_entrar_a_react():
    """«Salir» llevaba a la versión actual: el login volvía a / (27-09-2026)."""
    from django.test import RequestFactory

    from runac.views.inicio import salir

    pedido = RequestFactory().get("/salir/", {"next": "/v2/mir/"})
    pedido.session = type(
        "S", (), {"flush": lambda self: None, "cycle_key": lambda self: None}
    )()
    pedido.user = type("U", (), {"is_authenticated": False})()
    respuesta = salir(pedido)
    assert respuesta["Location"] == "/entrar/?next=%2Fv2%2Fmir%2F"


def test_salir_no_manda_a_otro_sitio():
    from django.test import RequestFactory

    from runac.views.inicio import salir

    pedido = RequestFactory().get("/salir/", {"next": "https://otro.sitio/"})
    pedido.session = type(
        "S", (), {"flush": lambda self: None, "cycle_key": lambda self: None}
    )()
    pedido.user = type("U", (), {"is_authenticated": False})()
    assert salir(pedido)["Location"] == "/entrar/"


def test_el_administrador_no_carga_ni_presenta_ni_corrige_datos():
    """La responsabilidad sobre los datos es de la provincia (27-09-2026).

    El administrador de esta instalación es superusuario de Django, y eso lo
    dejaba pasar en todo.
    """
    admin = _usuario(ADMIN, superusuario=True)
    assert not perm.puede_cargar(admin)
    assert not perm.puede_presentar(admin)
    assert not perm.puede_editar_datos(admin)
    assert perm.puede_administrar(admin)
