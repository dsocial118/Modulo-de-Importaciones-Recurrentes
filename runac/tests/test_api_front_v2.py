"""Tests de la API del front v2 y del reenvío de /v2/.

No tocan la base: los services se reemplazan por datos armados acá. Lo que se
prueba es lo que decide la capa nueva —quién ve qué jurisdicción, qué cuenta
como cargado, qué deja pasar el reenvío—, que es justamente lo que no cubren
los tests de los services.
"""

from types import SimpleNamespace

import pytest
import requests
from django.test import RequestFactory
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory, force_authenticate

from runac import api_views
from runac.views import front_v2


def _usuario(rol=None, jurisdiccion=None, superusuario=False):
    grupos = [
        g for g in (rol, f"jurisdiccion:{jurisdiccion}" if jurisdiccion else None) if g
    ]
    return SimpleNamespace(
        is_authenticated=True,
        is_active=True,
        is_superuser=superusuario,
        groups=SimpleNamespace(values_list=lambda *a, **k: grupos),
        get_username=lambda: rol or "anonimo",
    )


OPERADOR_CHUBUT = _usuario("operador_provincial", "Chubut")
REVISOR = _usuario("revisor_nacional")


def _pedido(ruta, usuario, **params):
    pedido = APIRequestFactory().get(ruta, params)
    force_authenticate(pedido, user=usuario)
    return pedido


# ---------------------------------------------------------------------------
# Quién ve qué jurisdicción: el hallazgo #10 de la auditoría
# ---------------------------------------------------------------------------


def _request(usuario, params):
    r = Request(APIRequestFactory().get("/", params))
    r.user = usuario
    return r


def test_el_provincial_ve_su_jurisdiccion_aunque_pida_otra():
    """En las pantallas actuales, cambiar la dirección alcanza. Acá no."""
    assert (
        api_views.jurisdiccion_permitida(
            _request(OPERADOR_CHUBUT, {"jurisdiccion": "Chaco"})
        )
        == "Chubut"
    )


def test_el_nacional_elige_la_jurisdiccion():
    assert (
        api_views.jurisdiccion_permitida(_request(REVISOR, {"jurisdiccion": "Chaco"}))
        == "Chaco"
    )


def test_el_nacional_no_elige_una_jurisdiccion_que_no_existe():
    assert (
        api_views.jurisdiccion_permitida(
            _request(REVISOR, {"jurisdiccion": "Atlántida"})
        )
        is None
    )


# ---------------------------------------------------------------------------
# El inicio
# ---------------------------------------------------------------------------

PERIODO = {
    "codigo": "2026_T1",
    "estado": "ABIERTO",
    "fecha_desde": "2026-01-01",
    "fecha_hasta": "2026-03-31",
}


def _archivo(codigo, estado, importada, **imp):
    return {
        "codigo": codigo,
        "nombre": f"Archivo {codigo}",
        "obligatorio": 1,
        "campos": 10,
        "reglas": 2,
        "estado": estado,
        "importada": importada,
        "importacion": imp or None,
    }


@pytest.fixture
def services(mocker):
    mocker.patch.object(api_views.svc, "periodos", return_value=[PERIODO])
    estado = mocker.patch.object(
        api_views.svc,
        "estado_de_la_presentacion",
        return_value={
            "presentacion": {"id": 7, "estado": "EN_CARGA"},
            "archivos": [
                _archivo(
                    "A", "VALIDA", True, filas_leidas=30, bloqueantes=0, advertencias=3
                ),
                _archivo(
                    "B",
                    "FALLIDA",
                    False,
                    filas_leidas=12,
                    bloqueantes=4,
                    advertencias=0,
                ),
                _archivo("C", "SIN_CARGAR", False),
            ],
            "listo": False,
        },
    )
    return estado


def test_un_archivo_con_errores_no_cuenta_como_cargado(services):
    """La pantalla actual lo contaba: excluía estados que el motor ya no usa."""
    datos = api_views.InicioView.as_view()(
        _pedido("/api/mir/inicio/", OPERADOR_CHUBUT)
    ).data
    assert datos["avance"] == {"cargados": 1, "total": 3}


def test_el_inicio_trae_filas_y_hallazgos_de_cada_archivo(services):
    datos = api_views.InicioView.as_view()(
        _pedido("/api/mir/inicio/", OPERADOR_CHUBUT)
    ).data
    por_codigo = {a["codigo"]: a for a in datos["archivos"]}
    assert por_codigo["A"]["advertencias"] == 3
    assert por_codigo["B"]["bloqueantes"] == 4
    assert por_codigo["C"]["filas"] is None


def test_el_provincial_no_recibe_la_lista_de_jurisdicciones(services):
    datos = api_views.InicioView.as_view()(
        _pedido("/api/mir/inicio/", OPERADOR_CHUBUT)
    ).data
    assert datos["jurisdicciones"] == []
    services.assert_called_once_with("Chubut", "2026_T1")


def test_un_periodo_que_no_existe_cae_en_el_primero(services):
    datos = api_views.InicioView.as_view()(
        _pedido("/api/mir/inicio/", OPERADOR_CHUBUT, periodo="1999_T9")
    ).data
    assert datos["periodo"]["codigo"] == "2026_T1"


def test_sin_rol_no_se_entra_al_inicio(services):
    respuesta = api_views.InicioView.as_view()(_pedido("/api/mir/inicio/", _usuario()))
    assert respuesta.status_code == 403


# ---------------------------------------------------------------------------
# La sesión
# ---------------------------------------------------------------------------


def test_el_menu_marca_que_secciones_estan_en_v2():
    datos = api_views.SesionView.as_view()(
        _pedido("/api/mir/sesion/", OPERADOR_CHUBUT)
    ).data
    menu = {m["clave"]: m for m in datos["menu"]}
    assert menu["inicio"]["ruta"] == "/v2/mir/"
    # Todas las secciones migraron: ninguna lleva a la pantalla actual.
    assert all(m["en_v2"] and m["ruta"].startswith("/v2/mir") for m in menu.values())


def test_una_seccion_sin_pantalla_en_v2_lleva_a_la_actual(mocker):
    mocker.patch.dict(api_views.EN_V2, {}, clear=True)
    datos = api_views.SesionView.as_view()(
        _pedido("/api/mir/sesion/", OPERADOR_CHUBUT)
    ).data
    cargar = next(m for m in datos["menu"] if m["clave"] == "cargar")
    assert cargar["en_v2"] is False
    assert not cargar["ruta"].startswith("/v2/")


# ---------------------------------------------------------------------------
# Lo de otra jurisdicción no existe
# ---------------------------------------------------------------------------


def test_lo_de_otra_jurisdiccion_da_404(mocker):
    """Verificado el 25-09-2026: en las pantallas actuales esto da 200."""
    from rest_framework.exceptions import NotFound

    mocker.patch.object(
        api_views.svc, "importacion", return_value={"id": 6, "jurisdiccion": "Chaco"}
    )
    with pytest.raises(NotFound):
        api_views._importacion_permitida(OPERADOR_CHUBUT, 6)


def test_lo_propio_se_ve(mocker):
    mocker.patch.object(
        api_views.svc, "importacion", return_value={"id": 1, "jurisdiccion": "Chubut"}
    )
    assert api_views._importacion_permitida(OPERADOR_CHUBUT, 1)["id"] == 1


def test_el_nacional_ve_cualquier_jurisdiccion(mocker):
    mocker.patch.object(
        api_views.svc, "jurisdiccion_de_la_presentacion", return_value="Chaco"
    )
    assert api_views._presentacion_permitida(REVISOR, 6) == "Chaco"


def test_una_accion_sobre_otra_jurisdiccion_no_se_ejecuta(mocker):
    mocker.patch.object(
        api_views.svc, "jurisdiccion_de_la_presentacion", return_value="Chaco"
    )
    ejecutar = mocker.patch.object(api_views.circuito, "ejecutar")
    pedido = APIRequestFactory().post(
        "/api/mir/presentaciones/6/acciones/cerrar_carga/"
    )
    force_authenticate(pedido, user=_usuario("responsable_provincial", "Chubut"))
    respuesta = api_views.AccionView.as_view()(
        pedido, presentacion_id=6, accion="cerrar_carga"
    )
    assert respuesta.status_code == 404
    ejecutar.assert_not_called()


def test_el_nacional_no_corrige_datos(mocker):
    mocker.patch.object(
        api_views.svc, "importacion", return_value={"id": 1, "jurisdiccion": "Chubut"}
    )
    editar = mocker.patch.object(api_views.edicion, "editar")
    pedido = APIRequestFactory().post(
        "/api/mir/importaciones/1/datos/",
        {"hoja_id": 1, "numero_fila": 2, "campo": "x", "valor": "y"},
        format="json",
    )
    force_authenticate(pedido, user=REVISOR)
    respuesta = api_views.DatosView.as_view()(pedido, importacion_id=1)
    assert respuesta.status_code == 403
    editar.assert_not_called()


def test_el_provincial_carga_en_su_jurisdiccion_aunque_mande_otra(mocker):
    from django.core.files.uploadedfile import SimpleUploadedFile

    importar = mocker.patch.object(
        api_views.svc, "importar_uno", return_value={"rechazado": True, "mensaje": "x"}
    )
    pedido = APIRequestFactory().post(
        "/api/mir/carga/MPI/",
        {
            "archivo": SimpleUploadedFile("MPI.xlsx", b"x"),
            "periodo": "2026_T1",
            "jurisdiccion": "Chaco",
        },
        format="multipart",
    )
    force_authenticate(pedido, user=OPERADOR_CHUBUT)
    api_views.CargarArchivoView.as_view()(pedido, codigo="MPI")
    assert importar.call_args.args[2] == "Chubut"


def test_la_sesion_dice_la_jurisdiccion_y_el_aviso():
    datos = api_views.SesionView.as_view()(
        _pedido("/api/mir/sesion/", OPERADOR_CHUBUT)
    ).data
    assert datos["jurisdiccion"] == "Chubut"
    assert datos["es_nacional"] is False
    assert datos["aviso"]  # la etiqueta «datos de prueba» no se pierde en /v2/


# ---------------------------------------------------------------------------
# El reenvío de /v2/
# ---------------------------------------------------------------------------


def _get(ruta, usuario=OPERADOR_CHUBUT, metodo="get"):
    pedido = getattr(RequestFactory(), metodo)(ruta)
    pedido.user = usuario
    return pedido


def test_un_modulo_desconocido_da_404():
    from django.http import Http404

    with pytest.raises(Http404):
        front_v2.reenviar(_get("/v2/otro/"), "otro")


def test_solo_se_reenvian_lecturas():
    respuesta = front_v2.reenviar(_get("/v2/mir/", metodo="post"), "mir")
    assert respuesta.status_code == 405


def test_sin_sesion_va_al_login():
    anonimo = SimpleNamespace(is_authenticated=False)
    respuesta = front_v2.reenviar(_get("/v2/mir/", usuario=anonimo), "mir")
    assert respuesta.status_code == 302
    assert "/entrar/" in respuesta["Location"]


def test_si_el_front_no_responde_da_503(mocker):
    mocker.patch.object(
        front_v2.requests, "request", side_effect=requests.ConnectionError
    )
    assert front_v2.reenviar(_get("/v2/mir/"), "mir").status_code == 503


def test_no_reenvia_la_galleta_de_sesion(mocker):
    llamada = mocker.patch.object(
        front_v2.requests,
        "request",
        return_value=SimpleNamespace(content=b"", status_code=200, headers={}),
    )
    pedido = _get("/v2/mir/")
    pedido.COOKIES["sesion_runac"] = "secreto"
    front_v2.reenviar(pedido, "mir")
    cabeceras = llamada.call_args.kwargs["headers"]
    assert "Cookie" not in cabeceras and "Authorization" not in cabeceras


def test_los_archivos_con_huella_se_guardan_y_la_pagina_no(mocker):
    mocker.patch.object(
        front_v2.requests,
        "request",
        return_value=SimpleNamespace(
            content=b"x", status_code=200, headers={"Content-Type": "text/javascript"}
        ),
    )
    activo = front_v2.reenviar(
        _get("/v2/mir/assets/app-abc123.js"), "mir", "assets/app-abc123.js"
    )
    pagina = front_v2.reenviar(_get("/v2/mir/"), "mir")
    assert "immutable" in activo["Cache-Control"]
    assert activo["Content-Type"] == "text/javascript"
    assert pagina["Cache-Control"] == "no-cache"
