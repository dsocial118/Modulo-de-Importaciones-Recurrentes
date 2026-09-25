"""API del front v2 (React), bajo `/api/mir/`.

Sigue la norma de SISOC para el front nuevo (`docs/implementaciones/frontend_v2.md`
en el repositorio de SISOC):

  - Las vistas son delgadas: **la lógica sigue en `runac/services/`**, y son
    los mismos services que usan las pantallas actuales. Nunca hay dos lógicas
    de negocio vivas.
  - Autenticación por la sesión de Django, en el mismo dominio. No hay tokens
    en el navegador.
  - El permiso se verifica siempre acá, en el servidor. Lo que el front oculte
    es comodidad, no seguridad.
"""

from django.conf import settings
from django.middleware.csrf import get_token
from django.urls import reverse
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from runac.api_serializers import InicioSerializer, SesionSerializer
from runac.permissions import (
    SECCIONES,
    es_nacional,
    jurisdiccion_de,
    menu_de,
    nombre_del_rol,
    puede_administrar,
    puede_cargar,
    puede_editar_datos,
    puede_entrar,
    puede_presentar,
    puede_revisar,
    rol_de,
)
from runac.services import circuito_service as circuito
from runac.services import importacion_service as svc
from runac.views.carga import JURISDICCIONES
from runac.views.inicio import DETALLE_DE_SECCION

# Las secciones que ya tienen pantalla en /v2/. El resto sigue en la versión
# actual, y el menú del front nuevo lleva ahí hasta que se migren.
EN_V2 = {"inicio": "/v2/mir/"}


def _exigir(usuario, seccion: str):
    if not puede_entrar(usuario, seccion):
        raise PermissionDenied("Tu rol no tiene acceso a esta sección.")


def jurisdiccion_permitida(request) -> str | None:
    """Sobre qué jurisdicción trabaja este pedido.

    Un usuario provincial trabaja **sólo sobre la suya**, pida lo que pida: la
    jurisdicción sale de su usuario, no de la dirección. Es el hallazgo #10 de
    la auditoría —en las pantallas actuales, cambiar la dirección alcanza para
    ver otra provincia— y la API nueva no lo repite.

    El nivel nacional elige, pero sólo entre las jurisdicciones que existen.
    """
    if not es_nacional(request.user):
        return jurisdiccion_de(request.user)
    pedida = request.query_params.get("jurisdiccion")
    return pedida if pedida in JURISDICCIONES else None


class SesionView(APIView):
    """Quién está conectado y qué puede hacer: lo primero que pide el front."""

    @extend_schema(responses=SesionSerializer)
    def get(self, request):
        usuario = request.user
        menu = []
        for seccion in menu_de(usuario):
            clave = seccion["clave"]
            menu.append(
                {
                    "clave": clave,
                    "etiqueta": seccion["etiqueta"],
                    "detalle": DETALLE_DE_SECCION.get(clave, ""),
                    "ruta": EN_V2.get(clave) or reverse(SECCIONES[clave]["url"]),
                    "en_v2": clave in EN_V2,
                }
            )
        datos = {
            "instancia": settings.MIR_INSTANCIA,
            "usuario": usuario.get_username(),
            "rol": rol_de(usuario),
            "nombre_del_rol": nombre_del_rol(usuario),
            "es_nacional": es_nacional(usuario),
            "jurisdiccion": jurisdiccion_de(usuario),
            "permisos": {
                "cargar": puede_cargar(usuario),
                "presentar": puede_presentar(usuario),
                "editar_datos": puede_editar_datos(usuario),
                "revisar": puede_revisar(usuario),
                "administrar": puede_administrar(usuario),
            },
            "menu": menu,
            # Para los pedidos que modifican algo. El nombre de la galleta de
            # CSRF cambia según la base (config/settings.py), así que el front
            # no la busca: la recibe acá.
            "csrf_token": get_token(request),
            "salir": reverse("runac:salir"),
            # Etiqueta de seguridad, no decoración: ver MIR_AVISO en settings.
            "aviso": settings.MIR_AVISO if settings.MIR_MOSTRAR_AVISO else "",
        }
        return Response(SesionSerializer(datos).data)


def _archivo(a: dict) -> dict:
    imp = a.get("importacion") or {}
    return {
        "codigo": a["codigo"],
        "nombre": a.get("nombre") or "",
        "obligatorio": bool(a.get("obligatorio")),
        "campos": a.get("campos") or 0,
        "reglas": a.get("reglas") or 0,
        "estado": a["estado"],
        "filas": imp.get("filas_leidas"),
        "bloqueantes": imp.get("bloqueantes") or 0,
        "advertencias": imp.get("advertencias") or 0,
    }


class InicioView(APIView):
    """El período, y cómo viene la presentación de la jurisdicción."""

    @extend_schema(responses=InicioSerializer)
    def get(self, request):
        _exigir(request.user, "inicio")

        periodos = svc.periodos()
        codigos = [p["codigo"] for p in periodos]
        pedido = request.query_params.get("periodo")
        elegido = pedido if pedido in codigos else (codigos[0] if codigos else None)
        jurisdiccion = jurisdiccion_permitida(request)

        presentacion, archivos = None, []
        if elegido:
            if jurisdiccion:
                estado = svc.estado_de_la_presentacion(jurisdiccion, elegido)
                archivos = estado["archivos"]
                if estado["presentacion"]:
                    pres = estado["presentacion"]
                    presentacion = {
                        "id": pres["id"],
                        "estado": pres["estado"],
                        "estado_legible": circuito.estado_legible(pres["estado"]),
                    }
            else:
                # Sin jurisdicción elegida se muestra lo que se espera, sin
                # estado de carga: es lo que ve el nivel nacional al entrar.
                archivos = [
                    {**a, "importacion": None, "estado": "SIN_CARGAR"}
                    for a in svc.archivos_esperados(elegido)
                ]

        # Cargado es lo que entró: tiene una importación VALIDA. La pantalla
        # actual excluye "CON_ERRORES" y "ESTRUCTURA_INVALIDA", que el motor ya
        # no usa, y por eso contaba como cargado un archivo FALLIDA.
        cargados = [a for a in archivos if a.get("importada")]
        datos = {
            "periodos": periodos,
            "periodo": next((p for p in periodos if p["codigo"] == elegido), None),
            "jurisdiccion": jurisdiccion,
            "jurisdicciones": JURISDICCIONES if es_nacional(request.user) else [],
            "presentacion": presentacion,
            "archivos": [_archivo(a) for a in archivos],
            "avance": {"cargados": len(cargados), "total": len(archivos)},
        }
        return Response(InicioSerializer(datos).data)
