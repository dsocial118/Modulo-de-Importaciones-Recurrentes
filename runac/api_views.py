# Un solo módulo de API por app, como pide la norma de SISOC (api_views.py).
# pylint: disable=too-many-lines
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

**De quién es cada cosa.** Todo lo que se pide por número —una presentación,
una importación, una observación— se controla contra la jurisdicción del
usuario antes de mostrarlo o tocarlo. Las pantallas actuales no lo hacen: un
usuario de una provincia que arme el pedido a mano puede operar sobre otra
(hallazgo #10 de la auditoría, ampliado el 25-09-2026). Para quien no es de
esa jurisdicción, lo ajeno **no existe**: 404, no 403, para no confirmar que
el número corresponde a algo.
"""

import io
import shutil
import zipfile
from pathlib import Path

from django.conf import settings
from django.http import HttpResponse
from django.middleware.csrf import get_token
from django.urls import reverse
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from runac import api_serializers as s
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
from runac.services import alcance_service as alcance
from runac.services import circuito_service as circuito
from runac.services import demo_service
from runac.services import edicion_service as edicion
from runac.services import importacion_service as svc
from runac.services import instructivo_service as instructivos
from runac.services import informe_errores_service as informes
from runac.services import plantillas_service as plantillas
from runac.services import reglas_service
from runac.services import situacion_service as situacion
from runac.views.carga import JURISDICCIONES, PASOS
from runac.views.estructura import (
    _dos_techos,
    _las_demas,
    _letra,
    _para_editar,
    como_se_escribe,
    titulo_completo,
    valores_admitidos,
)
from runac.views.inicio import DETALLE_DE_SECCION

XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

# Las secciones con pantalla en /v2/. Todas migraron; si alguna volviera a la
# versión actual, basta con sacarla de acá y el menú lleva allá.
EN_V2 = {
    "inicio": "/v2/mir/",
    "plantillas": "/v2/mir/plantillas",
    "cargar": "/v2/mir/cargar",
    "resultado": "/v2/mir/resultado",
    "revision": "/v2/mir/revision",
    "estructura": "/v2/mir/reglas",
    "situacion": "/v2/mir/situacion",
    "observaciones": "/v2/mir/observaciones",
    "administracion": "/v2/mir/administracion",
}


# ---------------------------------------------------------------------------
# De quién es cada cosa
# ---------------------------------------------------------------------------


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


# De quién es cada cosa lo decide `alcance_service`, el mismo que usan las
# pantallas actuales: un solo control para las dos versiones. Acá sólo se
# traduce su 404 al de DRF.


def _presentacion_permitida(usuario, presentacion_id: int) -> str:
    jurisdiccion = alcance.jurisdiccion_de_la_presentacion(presentacion_id)
    if not alcance.es_suya(usuario, jurisdiccion):
        raise NotFound("No existe esa presentación.")
    return jurisdiccion


def _importacion_permitida(usuario, importacion_id: int) -> dict:
    imp = svc.importacion(importacion_id)
    if not imp or not alcance.es_suya(usuario, imp.get("jurisdiccion")):
        raise NotFound("No existe esa importación.")
    return imp


def _periodos_y_elegido(request):
    """Los períodos y cuál se mira: el pedido si existe, o el más reciente."""
    periodos = svc.periodos()
    pedido = request.query_params.get("periodo")
    elegido = next((p for p in periodos if p["codigo"] == pedido), None)
    return periodos, elegido or (periodos[0] if periodos else None)


def _descarga(contenido: bytes, nombre: str, tipo: str = XLSX) -> HttpResponse:
    respuesta = HttpResponse(contenido, content_type=tipo)
    respuesta["Content-Disposition"] = f'attachment; filename="{nombre}"'
    return respuesta


# ---------------------------------------------------------------------------
# Sesión e inicio
# ---------------------------------------------------------------------------


class SesionView(APIView):
    """Quién está conectado y qué puede hacer: lo primero que pide el front."""

    @extend_schema(responses=s.SesionSerializer)
    def get(self, request):
        usuario = request.user
        menu = []
        for seccion in menu_de(usuario, v2=True):
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
            # Se sale y se vuelve a entrar a React, no a la versión actual.
            "salir": f'{reverse("runac:salir")}?next=/v2/mir/',
            # Etiqueta de seguridad, no decoración: ver MIR_AVISO en settings.
            "aviso": settings.MIR_AVISO if settings.MIR_MOSTRAR_AVISO else "",
            "marca": settings.MIR_MARCA,
            # Cómo se nombra cada archivo en pantalla: «Dispositivos penales»
            # y no DISP_PENAL (guion 35, 27-09-2026).
            "nombres_de_archivo": svc.nombres_cortos(),
        }
        return Response(s.SesionSerializer(datos).data)


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


def _estado_de(jurisdiccion, codigo_periodo):
    """El estado de la presentación, o lo que se espera si no hay jurisdicción.

    Sin jurisdicción elegida se muestra lo que se espera, sin estado de carga:
    es lo que ve el nivel nacional al entrar.
    """
    if jurisdiccion:
        return svc.estado_de_la_presentacion(jurisdiccion, codigo_periodo)
    return {
        "presentacion": None,
        "archivos": [
            {**a, "importacion": None, "importada": False, "estado": "SIN_CARGAR"}
            for a in svc.archivos_esperados(codigo_periodo)
        ],
        "listo": False,
    }


# Los pasos de la franja: los del circuito, sin repetir los que comparten
# estado. Carga, validación y corrección son el mismo momento —EN_CARGA—, y en
# una franja de un renglón tres pasos iguales no dicen nada.
def _pasos_de_la_franja(estado: str) -> list[dict]:
    grupos: list[tuple[str, tuple]] = []
    for nombre, estados in PASOS:
        if not grupos or grupos[-1][1] != estados:
            grupos.append((nombre, estados))
    actual = next((i for i, (_, estados) in enumerate(grupos) if estado in estados), 0)
    return [
        {"nombre": nombre, "actual": i == actual, "hecho": i < actual}
        for i, (nombre, _) in enumerate(grupos)
    ]


class FranjaView(APIView):
    """El avance del circuito de una presentación, en un renglón.

    Lo muestra una franja fina arriba de todas las pantallas: el avance les
    gustó y estaba escondido en Resultado (pedido del responsable funcional,
    27-09-2026). Sin jurisdicción —el nivel nacional que no eligió una— no hay
    nada que mostrar.
    """

    @extend_schema(
        parameters=[
            OpenApiParameter("periodo", str),
            OpenApiParameter("jurisdiccion", str),
        ],
        responses=s.FranjaSerializer,
    )
    def get(self, request):
        _, periodo = _periodos_y_elegido(request)
        jurisdiccion = jurisdiccion_permitida(request)
        vacia = {
            "jurisdiccion": jurisdiccion,
            "periodo": periodo["codigo"] if periodo else None,
            "periodo_nombre": svc.nombre_del_periodo(periodo),
            "estado": None,
            "estado_legible": None,
            "que_pasa": "",
            "pasos": [],
            "te_toca": [],
            "archivos_importados": 0,
            "archivos_esperados": 0,
            "observaciones_abiertas": 0,
        }
        if not (periodo and jurisdiccion):
            return Response(s.FranjaSerializer(vacia).data)
        estado_pres = svc.estado_de_la_presentacion(jurisdiccion, periodo["codigo"])
        pres = estado_pres["presentacion"]
        estado = pres["estado"] if pres else "EN_CARGA"
        abiertas = 0
        if pres:
            abiertas = sum(
                1
                for o in circuito.observaciones_de(pres["id"])
                if o["estado"] == "ABIERTA"
            )
        datos = {
            **vacia,
            "estado": estado,
            "estado_legible": circuito.estado_legible(estado),
            "que_pasa": circuito.ESTADOS.get(estado, ("", ""))[1],
            "pasos": _pasos_de_la_franja(estado),
            # Lo que este usuario puede hacer ahora: «Te toca: cerrar la carga».
            "te_toca": [
                a["etiqueta"]
                for a in circuito.acciones_disponibles(
                    pres, request.user, estado_pres["listo"]
                )
            ],
            "archivos_importados": sum(
                1 for a in estado_pres["archivos"] if a.get("importada")
            ),
            "archivos_esperados": len(estado_pres["archivos"]),
            "observaciones_abiertas": abiertas,
        }
        return Response(s.FranjaSerializer(datos).data)


class InicioView(APIView):
    """El período, y cómo viene la presentación de la jurisdicción."""

    @extend_schema(responses=s.InicioSerializer)
    def get(self, request):
        _exigir(request.user, "inicio")
        periodos, periodo = _periodos_y_elegido(request)
        jurisdiccion = jurisdiccion_permitida(request)

        presentacion, archivos = None, []
        if periodo:
            estado = _estado_de(jurisdiccion, periodo["codigo"])
            archivos = estado["archivos"]
            if estado["presentacion"]:
                pres = estado["presentacion"]
                presentacion = {
                    "id": pres["id"],
                    "estado": pres["estado"],
                    "estado_legible": circuito.estado_legible(pres["estado"]),
                }

        # Cargado es lo que entró: tiene una importación VALIDA. La pantalla
        # actual excluye "CON_ERRORES" y "ESTRUCTURA_INVALIDA", que el motor ya
        # no usa, y por eso contaba como cargado un archivo FALLIDA.
        cargados = [a for a in archivos if a.get("importada")]
        datos = {
            "periodos": periodos,
            "periodo": periodo,
            "jurisdiccion": jurisdiccion,
            "jurisdicciones": JURISDICCIONES if es_nacional(request.user) else [],
            "presentacion": presentacion,
            "archivos": [_archivo(a) for a in archivos],
            "avance": {"cargados": len(cargados), "total": len(archivos)},
        }
        return Response(s.InicioSerializer(datos).data)


class EstadoDelPeriodoView(APIView):
    """Abre, cierra o vuelve a preparar un período. Lo decide el nivel nacional."""

    @extend_schema(
        request=s.EstadoDelPeriodoSerializer, responses=s.PeriodoCambiadoSerializer
    )
    def post(self, request, codigo):
        if not puede_administrar(request.user):
            raise PermissionDenied(
                "Sólo el administrador cambia el estado del período."
            )
        pedido = s.EstadoDelPeriodoSerializer(data=request.data)
        pedido.is_valid(raise_exception=True)
        try:
            estado = circuito.cambiar_estado_del_periodo(
                codigo, pedido.validated_data["estado"], request.user
            )
        except circuito.TransicionInvalida as error:
            raise ValidationError({"detail": str(error)}) from error
        aviso = ""
        if estado == "PREPARACION":
            aviso = (
                "Volver a preparación es una herramienta de prueba: en el sistema "
                "real, con el período abierto la definición no se toca."
            )
            cargadas = circuito.volver_atras_es_provisorio(codigo)
            if cargadas:
                aviso += (
                    f" Y este período ya tiene {cargadas} importaciones: lo que "
                    "cambies ahora no es contra lo que esas provincias presentaron."
                )
        datos = {
            "estado": estado,
            "mensaje": f"El período {codigo} quedó en «{estado}».",
            "aviso": aviso,
        }
        return Response(s.PeriodoCambiadoSerializer(datos).data)


class ArmarDemoView(APIView):
    """Herramienta de prueba: deja una presentación completa para mostrar."""

    @extend_schema(request=None, responses=s.MensajeSerializer)
    def post(self, request):
        if not puede_administrar(request.user):
            raise PermissionDenied("Sólo el administrador puede armar la demostración.")
        resumen = demo_service.armar()
        rechazos = "; ".join(f"{c}: {m}" for c, m in resumen["rechazados"])
        mensaje = (
            f'Demostración armada: {len(resumen["importados"])} archivos importados '
            f'y {resumen["correcciones"]} correcciones, sobre '
            f"{demo_service.JURISDICCION}. Es una función de prueba."
        )
        if rechazos:
            mensaje += f" No entraron: {rechazos}."
        return Response({"mensaje": mensaje})


class BorrarImportacionesView(APIView):
    """Herramienta de prueba: deja el sistema sin ninguna importación."""

    @extend_schema(request=None, responses=s.MensajeSerializer)
    def post(self, request):
        if not puede_administrar(request.user):
            raise PermissionDenied(
                "Sólo el administrador puede borrar las importaciones."
            )
        b = circuito.borrar_todas_las_importaciones()
        mensaje = (
            "Se borraron todas las importaciones de todas las jurisdicciones: "
            f'{b["presentaciones"]} presentaciones, {b["importaciones"]} '
            f'importaciones y {b["filas"]} registros.'
            + (" El período se reabrió." if b["periodos"] else "")
            + " Es una función de prueba."
        )
        return Response({"mensaje": mensaje})


# ---------------------------------------------------------------------------
# Plantillas
# ---------------------------------------------------------------------------


class PlantillasView(APIView):
    @extend_schema(responses=s.PlantillasSerializer)
    def get(self, request):
        _exigir(request.user, "plantillas")
        periodos, periodo = _periodos_y_elegido(request)
        archivos = []
        if periodo:
            del_periodo = periodo["codigo"]
            for a in svc.archivos_esperados(del_periodo):
                archivos.append(
                    {
                        "codigo": a["codigo"],
                        "nombre": a.get("nombre") or "",
                        "hojas": a.get("hojas") or 0,
                        "campos": a.get("campos") or 0,
                        "obligatorio": bool(a.get("obligatorio")),
                        "descarga": reverse(
                            "api_mir:plantilla", args=[del_periodo, a["codigo"]]
                        ),
                        "descarga_instructivo": reverse(
                            "api_mir:instructivo", args=[del_periodo, a["codigo"]]
                        ),
                    }
                )
        datos = {
            "periodos": periodos,
            "periodo": periodo,
            "archivos": archivos,
            "descarga_todas": (
                reverse("api_mir:plantillas_todas", args=[periodo["codigo"]])
                if periodo
                else ""
            ),
        }
        return Response(s.PlantillasSerializer(datos).data)


class PlantillaView(APIView):
    """Una plantilla, generada en el momento contra la definición vigente."""

    @extend_schema(
        operation_id="mir_plantilla_descargar", responses={(200, XLSX): bytes}
    )
    def get(self, request, codigo, periodo):
        _exigir(request.user, "plantillas")
        if codigo not in {a["codigo"] for a in svc.archivos_esperados(periodo)}:
            raise NotFound("Ese archivo no forma parte del período.")
        ruta = Path(plantillas.generar(codigo, periodo))
        contenido = ruta.read_bytes()
        shutil.rmtree(ruta.parent, ignore_errors=True)
        return _descarga(contenido, ruta.name)


class InstructivoView(APIView):
    """El instructivo de un archivo: una fila por campo. Se baja aparte de la plantilla."""

    @extend_schema(
        operation_id="mir_instructivo_descargar", responses={(200, XLSX): bytes}
    )
    def get(self, request, codigo, periodo):
        _exigir(request.user, "plantillas")
        if codigo not in {a["codigo"] for a in svc.archivos_esperados(periodo)}:
            raise NotFound("Ese archivo no forma parte del período.")
        return _descarga(
            instructivos.generar(codigo, periodo, request.user.get_username()),
            instructivos.nombre_de_archivo(codigo, periodo),
        )


class PlantillasTodasView(APIView):
    """Todas las plantillas del período en un solo zip, cada una con su instructivo."""

    @extend_schema(responses={(200, "application/zip"): bytes})
    def get(self, request, periodo):
        _exigir(request.user, "plantillas")
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z:
            for a in svc.archivos_esperados(periodo):
                ruta = Path(plantillas.generar(a["codigo"], periodo))
                z.write(ruta, ruta.name)
                shutil.rmtree(ruta.parent, ignore_errors=True)
                z.writestr(
                    instructivos.nombre_de_archivo(a["codigo"], periodo),
                    instructivos.generar(
                        a["codigo"], periodo, request.user.get_username()
                    ),
                )
        nombre = f"{settings.MIR_INSTANCIA}_plantillas_{periodo}.zip"
        return _descarga(buffer.getvalue(), nombre, "application/zip")


# ---------------------------------------------------------------------------
# Carga
# ---------------------------------------------------------------------------


class CargaView(APIView):
    """Los archivos del período, con su estado y lo que necesita cada uno."""

    @extend_schema(responses=s.CargaSerializer)
    def get(self, request):
        _exigir(request.user, "cargar")
        periodos, periodo = _periodos_y_elegido(request)
        jurisdiccion = jurisdiccion_permitida(request)
        archivos, pres, listo = [], None, False
        if periodo and jurisdiccion:
            codigo = periodo["codigo"]
            estado = svc.estado_de_la_presentacion(jurisdiccion, codigo)
            pres, listo = estado["presentacion"], estado["listo"]
            for a in estado["archivos"]:
                faltan = svc.dependencias_faltantes(a["codigo"], jurisdiccion, codigo)
                imp = a.get("importacion") or {}
                archivos.append(
                    {
                        "codigo": a["codigo"],
                        "nombre": a.get("nombre") or "",
                        "obligatorio": bool(a.get("obligatorio")),
                        "estado": a["estado"],
                        "importada": bool(a.get("importada")),
                        "filas": imp.get("filas_incorporadas"),
                        "advertencias": imp.get("advertencias"),
                        "correcciones": (
                            edicion.cantidad_de_correcciones(imp["id"])
                            if a.get("importada")
                            else 0
                        ),
                        "necesita": svc.archivos_referenciados(a["codigo"], codigo),
                        "bloqueado_por": [f["codigo"] for f in faltan],
                        "nombre_sugerido": f'{a["codigo"]}_{codigo}_{jurisdiccion}.xlsx',
                    }
                )
        estado_codigo = pres["estado"] if pres else "EN_CARGA"
        datos = {
            "periodos": periodos,
            "periodo": periodo,
            "jurisdiccion": jurisdiccion,
            "jurisdicciones": JURISDICCIONES if es_nacional(request.user) else [],
            "estado_legible": circuito.estado_legible(estado_codigo),
            # Con la carga cerrada no se importa: primero hay que reabrirla.
            "carga_abierta": estado_codigo == "EN_CARGA",
            "puede_cargar": puede_cargar(request.user),
            "listo": listo,
            "archivos": archivos,
        }
        return Response(s.CargaSerializer(datos).data)


class CargarArchivoView(APIView):
    """Sube UN archivo, declarado por quien carga."""

    parser_classes = [MultiPartParser]

    @extend_schema(
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "archivo": {"type": "string", "format": "binary"},
                    "periodo": {"type": "string"},
                    "jurisdiccion": {"type": "string"},
                },
                "required": ["archivo", "periodo"],
            }
        },
        responses=s.ResultadoDeImportarSerializer,
    )
    def post(self, request, codigo):
        _exigir(request.user, "cargar")
        if not puede_cargar(request.user):
            raise PermissionDenied("Tu rol no puede importar archivos.")
        fichero = request.FILES.get("archivo")
        periodo = request.data.get("periodo")
        jurisdiccion = (
            request.data.get("jurisdiccion")
            if es_nacional(request.user)
            else jurisdiccion_de(request.user)
        )
        if es_nacional(request.user) and jurisdiccion not in JURISDICCIONES:
            raise ValidationError({"jurisdiccion": ["Elegí una jurisdicción."]})
        if not fichero:
            raise ValidationError({"archivo": ["No se seleccionó ningún archivo."]})
        if not jurisdiccion:
            raise PermissionDenied("Tu usuario no tiene jurisdicción asignada.")

        resultado = svc.importar_uno(
            codigo, fichero, jurisdiccion, periodo, request.user.get_username()
        )
        if resultado.get("rechazado"):
            datos = {
                "rechazado": True,
                "mensaje": resultado.get("mensaje", ""),
                "importacion_id": None,
                "estado": None,
                "filas": None,
                "bloqueantes": 0,
                "advertencias": 0,
            }
            return Response(s.ResultadoDeImportarSerializer(datos).data)

        # El resultado se lee de la importación registrada y no de contadores
        # del motor: un rechazo por estructura no trae conteo de bloqueantes, y
        # contar cero llevaba a anunciar «importación correcta» sobre algo que
        # había fallado.
        estado = svc.estado_de_la_presentacion(jurisdiccion, periodo)
        fila = next((a for a in estado["archivos"] if a["codigo"] == codigo), {})
        # La última que se intentó, no la vigente: si la nueva falló, la
        # vigente es la anterior, y anunciar su resultado hacía pasar por
        # buena una importación rechazada (26-09-2026).
        imp = fila.get("ultima") or {}
        datos = {
            "rechazado": False,
            "mensaje": "",
            "importacion_id": imp.get("id"),
            "estado": imp.get("estado") or "FALLIDA",
            "filas": imp.get("filas_incorporadas"),
            "bloqueantes": imp.get("bloqueantes") or 0,
            "advertencias": imp.get("advertencias") or 0,
        }
        return Response(s.ResultadoDeImportarSerializer(datos).data)


# ---------------------------------------------------------------------------
# Resultado y circuito
# ---------------------------------------------------------------------------


def _breve(imp):
    if not imp:
        return None
    return {
        "id": imp["id"],
        "estado": imp["estado"],
        "filas_leidas": imp.get("filas_leidas"),
        "filas_incorporadas": imp.get("filas_incorporadas"),
        "bloqueantes": imp.get("bloqueantes") or 0,
        "advertencias": imp.get("advertencias") or 0,
    }


class ResultadoView(APIView):
    """El estado del período: qué entró, qué observó Nación y qué falta."""

    @extend_schema(responses=s.ResultadoSerializer)
    def get(
        self, request
    ):  # pylint: disable=too-many-locals  # arma una pantalla entera
        _exigir(request.user, "resultado")
        usuario = request.user
        periodos, periodo = _periodos_y_elegido(request)
        jurisdiccion = jurisdiccion_permitida(request)
        estado = (
            _estado_de(jurisdiccion, periodo["codigo"])
            if periodo
            else {"presentacion": None, "archivos": [], "listo": False}
        )
        # Un dict vacío y no None: pylint no sigue el «if pres» y marca cada acceso.
        pres = (estado["presentacion"] if jurisdiccion else None) or {}

        archivos, totales = [], {
            "filas": 0,
            "validas": 0,
            "bloqueantes": 0,
            "advertencias": 0,
        }
        for a in estado["archivos"]:
            imp = a.get("importacion")
            archivos.append(
                {
                    "codigo": a["codigo"],
                    "nombre": a.get("nombre") or "",
                    "estado": a["estado"],
                    "importada": bool(a.get("importada")),
                    "importacion": _breve(imp),
                    "resumen": svc.resumen_de_hallazgos(imp["id"])[:6] if imp else [],
                }
            )
            if imp:
                totales["filas"] += imp.get("filas_leidas") or 0
                totales["validas"] += imp.get("filas_incorporadas") or 0
                totales["bloqueantes"] += imp.get("bloqueantes") or 0
                totales["advertencias"] += imp.get("advertencias") or 0

        codigo_estado = pres["estado"] if pres else "EN_CARGA"
        nombre, ayuda, _ = circuito.ESTADOS.get(codigo_estado, (codigo_estado, "", ""))
        datos = {
            "periodos": periodos,
            "periodo": periodo,
            "jurisdiccion": jurisdiccion,
            "jurisdicciones": JURISDICCIONES if es_nacional(usuario) else [],
            "presentacion": (
                {
                    "id": pres["id"],
                    "estado": pres["estado"],
                    "estado_legible": nombre,
                    "estado_ayuda": ayuda,
                    "version": pres.get("version"),
                    "expediente": pres.get("expediente"),
                }
                if pres
                else None
            ),
            "pasos": [
                {"nombre": n, "actual": codigo_estado in estados}
                for n, estados in PASOS
            ],
            "archivos": archivos,
            "totales": totales,
            "acciones": [
                {"accion": a["accion"], "etiqueta": a["etiqueta"], "ayuda": a["ayuda"]}
                for a in circuito.acciones_disponibles(
                    pres or None, usuario, estado["listo"]
                )
            ],
            "observaciones": circuito.observaciones_de(pres["id"]) if pres else [],
            "puede_responder": puede_cargar(usuario) or puede_presentar(usuario),
            "puede_presentar": puede_presentar(usuario),
            "puede_editar": puede_editar_datos(usuario),
            "listo": estado["listo"],
        }
        return Response(s.ResultadoSerializer(datos).data)


class AccionView(APIView):
    """Ejecuta una transición del circuito sobre una presentación."""

    @extend_schema(request=None, responses=s.AccionHechaSerializer)
    def post(self, request, presentacion_id, accion):
        _exigir(request.user, "resultado")
        _presentacion_permitida(request.user, presentacion_id)
        try:
            # La completitud se calcula desde la presentación, nunca desde algo
            # que mande el navegador.
            nuevo = circuito.ejecutar(
                presentacion_id,
                accion,
                request.user,
                listo=svc.presentacion_completa(presentacion_id),
            )
        except circuito.TransicionInvalida as error:
            raise ValidationError({"detail": str(error)}) from error
        legible = circuito.estado_legible(nuevo)
        datos = {
            "estado": nuevo,
            "estado_legible": legible,
            "mensaje": f"{circuito.ETIQUETAS[accion]}: la presentación quedó en «{legible}».",
        }
        return Response(s.AccionHechaSerializer(datos).data)


class ObservarView(APIView):
    """El revisor nacional formula una observación. No modifica el dato."""

    @extend_schema(request=s.NuevaObservacionSerializer, responses=s.MensajeSerializer)
    def post(self, request, presentacion_id):
        _exigir(request.user, "revision")
        _presentacion_permitida(request.user, presentacion_id)
        pedido = s.NuevaObservacionSerializer(data=request.data)
        pedido.is_valid(raise_exception=True)
        d = pedido.validated_data
        if d.get("importacion_id"):
            imp = svc.importacion(d["importacion_id"])
            if not imp or imp.get("presentacion_id") != presentacion_id:
                raise ValidationError(
                    {"importacion_id": ["No es una importación de esta presentación."]}
                )
        # Sobre un dato: la celda tiene que existir, y se guarda de quién es la
        # fila, para que la observación se entienda sin abrir el archivo.
        identificador = None
        if d.get("campo_id"):
            if not (d.get("importacion_id") and d.get("numero_fila")):
                raise ValidationError(
                    {
                        "campo_id": [
                            "Para observar un dato hacen falta la importación y la fila."
                        ]
                    }
                )
            try:
                identificador = edicion.celda_observable(
                    d["importacion_id"], d["numero_fila"], d["campo_id"]
                )
            except edicion.EdicionNoPermitida as error:
                raise ValidationError({"campo_id": [str(error)]}) from error
        try:
            circuito.crear_observacion(
                presentacion_id,
                request.user,
                texto=d["texto"],
                ubicacion={
                    "importacion_id": d.get("importacion_id"),
                    "numero_fila": d.get("numero_fila"),
                    "campo_id": d.get("campo_id"),
                    "identificador_registro": identificador,
                },
            )
        except circuito.TransicionInvalida as error:
            raise ValidationError({"detail": str(error)}) from error
        return Response(
            {
                "mensaje": "Observación registrada. La jurisdicción la va a ver en el dato "
                "y en la lista de observaciones sin resolver."
            },
            status=status.HTTP_201_CREATED,
        )


class ReabrirObservacionView(APIView):
    """El revisor no acepta la respuesta: la observación vuelve a abrirse."""

    @extend_schema(request=s.RespuestaSerializer, responses=s.MensajeSerializer)
    def post(self, request, observacion_id):
        _exigir(request.user, "revision")
        presentacion_id = alcance.presentacion_de_la_observacion(observacion_id)
        if presentacion_id is None:
            raise NotFound("No existe esa observación.")
        _presentacion_permitida(request.user, presentacion_id)
        pedido = s.RespuestaSerializer(data=request.data)
        pedido.is_valid(raise_exception=True)
        try:
            circuito.reabrir_observacion(
                observacion_id, request.user, pedido.validated_data["respuesta"]
            )
        except circuito.TransicionInvalida as error:
            raise ValidationError({"detail": str(error)}) from error
        return Response({"mensaje": "La observación volvió a abrirse."})


class DesestimarObservacionView(APIView):
    """El revisor retira su observación."""

    @extend_schema(request=None, responses=s.MensajeSerializer)
    def post(self, request, observacion_id):
        _exigir(request.user, "revision")
        presentacion_id = alcance.presentacion_de_la_observacion(observacion_id)
        if presentacion_id is None:
            raise NotFound("No existe esa observación.")
        _presentacion_permitida(request.user, presentacion_id)
        try:
            circuito.desestimar_observacion(observacion_id, request.user)
        except circuito.TransicionInvalida as error:
            raise ValidationError({"detail": str(error)}) from error
        return Response({"mensaje": "Observación desestimada."})


class ResponderView(APIView):
    """La jurisdicción responde una observación."""

    @extend_schema(request=s.RespuestaSerializer, responses=s.MensajeSerializer)
    def post(self, request, observacion_id):
        _exigir(request.user, "resultado")
        presentacion_id = alcance.presentacion_de_la_observacion(observacion_id)
        if presentacion_id is None:
            raise NotFound("No existe esa observación.")
        _presentacion_permitida(request.user, presentacion_id)
        if not (puede_cargar(request.user) or puede_presentar(request.user)):
            raise PermissionDenied("Responde la jurisdicción.")
        pedido = s.RespuestaSerializer(data=request.data)
        pedido.is_valid(raise_exception=True)
        try:
            circuito.responder_observacion(
                observacion_id, request.user, pedido.validated_data["respuesta"]
            )
        except circuito.TransicionInvalida as error:
            raise ValidationError({"detail": str(error)}) from error
        return Response({"mensaje": "Respuesta registrada."})


class ExpedienteView(APIView):
    """Registra el número GDE, después de remitir el comprobante."""

    @extend_schema(request=s.ExpedienteSerializer, responses=s.MensajeSerializer)
    def post(self, request, presentacion_id):
        _exigir(request.user, "resultado")
        _presentacion_permitida(request.user, presentacion_id)
        pedido = s.ExpedienteSerializer(data=request.data)
        pedido.is_valid(raise_exception=True)
        try:
            circuito.registrar_expediente(
                presentacion_id, pedido.validated_data["expediente"], request.user
            )
        except circuito.TransicionInvalida as error:
            raise ValidationError({"detail": str(error)}) from error
        return Response({"mensaje": "Número de expediente registrado."})


class ComprobanteView(APIView):
    """El comprobante de presentación: constancia de la entrega."""

    @extend_schema(responses=s.ComprobanteSerializer)
    def get(self, request, presentacion_id):
        _exigir(request.user, "resultado")
        _presentacion_permitida(request.user, presentacion_id)
        datos = circuito.comprobante(presentacion_id)
        if not datos or datos.get("estado") not in ("PRESENTADA", "CONSOLIDADA"):
            raise NotFound("La presentación todavía no tiene comprobante.")
        return Response(s.ComprobanteSerializer(datos).data)


class RevisionView(APIView):
    """Bandeja del revisor técnico nacional: qué presentó cada jurisdicción."""

    @extend_schema(responses=s.RevisionSerializer)
    def get(self, request):
        _exigir(request.user, "revision")
        periodos, periodo = _periodos_y_elegido(request)
        es_revisor = puede_revisar(request.user)
        filas = []
        for f in (
            circuito.presentaciones_del_periodo(periodo["codigo"]) if periodo else []
        ):
            filas.append(
                {
                    **f,
                    "estado_legible": circuito.estado_legible(f["estado"]),
                    "acciones": [
                        {
                            "accion": a["accion"],
                            "etiqueta": a["etiqueta"],
                            "ayuda": a["ayuda"],
                        }
                        for a in circuito.acciones_disponibles(f, request.user)
                    ],
                    "puede_observar": es_revisor
                    and f["estado"] in circuito.ESTADOS_OBSERVABLES,
                }
            )
        datos = {
            "periodos": periodos,
            "periodo": periodo,
            "es_revisor": es_revisor,
            "presentaciones": filas,
        }
        return Response(s.RevisionSerializer(datos).data)


# ---------------------------------------------------------------------------
# Detalle de una importación
# ---------------------------------------------------------------------------


class DetalleView(APIView):
    """Lo que pasó con una importación: problemas del archivo y hallazgos."""

    @extend_schema(responses=s.DetalleSerializer)
    def get(self, request, importacion_id):
        _exigir(request.user, "resultado")
        imp = _importacion_permitida(request.user, importacion_id)
        resumen = svc.resumen_de_hallazgos(importacion_id)
        severidades = {r["severidad"] for r in resumen}
        datos = {
            "importacion": imp,
            "hojas": svc.hojas_con_hallazgos(importacion_id),
            "errores_archivo": svc.errores_del_archivo(importacion_id),
            "resumen": resumen,
            "severidad_unica": (
                next(iter(severidades)) if len(severidades) == 1 else None
            ),
            "puede_editar": imp["estado"] == "VALIDA",
            # Quién puede corregir: el rol, no sólo que haya datos. Por esto el
            # revisor veía «Ver y corregir datos» (27-09-2026).
            "puede_corregir": puede_editar_datos(request.user),
            "observaciones_abiertas": sum(
                1
                for o in circuito.observaciones_de_la_importacion(importacion_id)
                if o["estado"] == "ABIERTA"
            ),
            "descargas": {
                "errores": reverse("api_mir:errores_xlsx", args=[importacion_id]),
                "marcado": reverse("api_mir:marcado_xlsx", args=[importacion_id]),
            },
        }
        return Response(s.DetalleSerializer(datos).data)


class PaginaDeHallazgos(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 200


class HallazgosView(APIView):
    """Los hallazgos de una importación, filtrados y paginados."""

    @extend_schema(
        parameters=[
            OpenApiParameter("severidad", str),
            OpenApiParameter("hoja", str),
            OpenApiParameter("buscar", str),
            OpenApiParameter("page", int),
            OpenApiParameter("page_size", int),
        ],
        responses=s.PaginaDeHallazgosSerializer,
    )
    def get(self, request, importacion_id):
        _exigir(request.user, "resultado")
        _importacion_permitida(request.user, importacion_id)
        q = request.query_params
        filtros = {
            "severidad": q.get("severidad") or None,
            "hoja": q.get("hoja") or None,
            "buscar": q.get("buscar") or None,
        }
        paginador = PaginaDeHallazgos()
        tamano = paginador.get_page_size(request)
        try:
            pagina = max(1, int(q.get("page") or 1))
        except ValueError:
            pagina = 1
        total = svc.contar_hallazgos(importacion_id, **filtros)
        filas = svc.hallazgos_de(
            importacion_id, **filtros, limite=tamano, desde=(pagina - 1) * tamano
        )
        base = request.build_absolute_uri(request.path)

        def enlace(numero):
            if numero < 1 or (numero - 1) * tamano >= total:
                return None
            params = q.copy()
            params["page"] = numero
            return f"{base}?{params.urlencode()}"

        return Response(
            {
                "count": total,
                "next": enlace(pagina + 1),
                "previous": enlace(pagina - 1) if pagina > 1 else None,
                "results": s.HallazgoSerializer(filas, many=True).data,
            }
        )


class ErroresXlsxView(APIView):
    """El informe de la importación: cada problema, con su estado."""

    @extend_schema(responses={(200, XLSX): bytes})
    def get(self, request, importacion_id):
        _exigir(request.user, "resultado")
        _importacion_permitida(request.user, importacion_id)
        contenido = informes.planilla_de_errores(
            importacion_id, usuario=request.user.get_username()
        )
        if not contenido:
            raise NotFound("No existe esa importación.")
        return _descarga(contenido, informes.nombre_del_informe(importacion_id))


class MarcadoXlsxView(APIView):
    """El archivo que subió la jurisdicción, con las celdas marcadas."""

    @extend_schema(responses={(200, XLSX): bytes})
    def get(self, request, importacion_id):
        _exigir(request.user, "resultado")
        _importacion_permitida(request.user, importacion_id)
        contenido, nombre = informes.archivo_marcado(
            importacion_id, usuario=request.user.get_username()
        )
        if not contenido:
            raise NotFound(
                "No se conserva el archivo original de esa importación. "
                "Está disponible la lista de errores."
            )
        return _descarga(contenido, nombre)


class HistorialXlsxView(APIView):
    """Las correcciones hechas en el sistema sobre una importación, en un Excel."""

    @extend_schema(responses={(200, XLSX): bytes})
    def get(self, request, importacion_id):
        _exigir(request.user, "resultado")
        _importacion_permitida(request.user, importacion_id)
        contenido, nombre = informes.historial_de_cambios(
            importacion_id, usuario=request.user.get_username()
        )
        if not contenido:
            raise NotFound("No existe esa importación.")
        return _descarga(contenido, nombre)


# ---------------------------------------------------------------------------
# Edición de datos
# ---------------------------------------------------------------------------


class DatosView(APIView):
    """Los datos importados de una hoja, para revisar y corregir."""

    @extend_schema(
        parameters=[
            OpenApiParameter("hoja", int),
            OpenApiParameter("pagina", int),
            OpenApiParameter(
                "solo",
                str,
                description="«avisos»: las filas con advertencia; «observadas»: con observaciones sin resolver",
            ),
        ],
        responses=s.DatosSerializer,
    )
    def get(self, request, importacion_id):
        _exigir(request.user, "resultado")
        _importacion_permitida(request.user, importacion_id)
        contexto = edicion.contexto_de(importacion_id)
        # Las hojas de referencia no traen datos de la provincia: no se ofrecen.
        # (Siguen en el contexto: el nombre de cada tabla depende de cuántas
        # hojas tiene el archivo.)
        visibles = [
            h for h in (contexto or {}).get("hojas", []) if not h.get("referencia")
        ]
        if not visibles:
            raise NotFound("La importación no tiene datos para mostrar.")
        pedida = request.query_params.get("hoja")
        hoja = next((h for h in visibles if str(h["id"]) == str(pedida)), visibles[0])
        # Las observaciones de cada dato: la que está sin resolver o, si no
        # hay, la última que se resolvió. Las desestimadas no se muestran.
        observaciones = circuito.observaciones_de_la_importacion(importacion_id)
        por_celda: dict = {}
        for o in observaciones:
            if o["campo_id"] and o["estado"] != "DESESTIMADA":
                por_celda.setdefault((o["numero_fila"], o["campo_id"]), o)
        datos = edicion.datos_de_la_hoja(
            importacion_id,
            hoja,
            pagina=request.query_params.get("pagina", 1),
            solo_con_advertencia=request.query_params.get("solo") == "avisos",
            # «observadas»: las filas con alguna observación sin resolver.
            solo_filas=(
                sorted(
                    {
                        o["numero_fila"]
                        for o in observaciones
                        if o["estado"] == "ABIERTA"
                        and o["hoja"] == hoja["nombre_esperado"]
                    }
                )
                if request.query_params.get("solo") == "observadas"
                else None
            ),
        )
        salida = {
            "contexto": {
                "id": contexto["id"],
                "archivo_codigo": contexto["archivo_codigo"],
                "jurisdiccion": contexto["jurisdiccion"],
                "periodo": contexto["periodo"],
                "version": contexto["version"],
                "estado_presentacion": contexto["estado_presentacion"],
                "estado_legible": circuito.estado_legible(
                    contexto["estado_presentacion"]
                ),
                "editable": contexto["editable"],
                "presentacion_id": contexto["presentacion_id"],
            },
            "hojas": [
                {"id": h["id"], "nombre": h["nombre_esperado"]} for h in visibles
            ],
            "hoja": {"id": hoja["id"], "nombre": hoja["nombre_esperado"]},
            "puede_editar": puede_editar_datos(request.user) and contexto["editable"],
            # Observa el nivel nacional; responde la jurisdicción.
            "puede_observar": puede_revisar(request.user)
            and contexto["estado_presentacion"] in circuito.ESTADOS_OBSERVABLES,
            "puede_responder": puede_editar_datos(request.user),
            "observaciones": observaciones,
            "total": datos["total"],
            "pagina": datos["pagina"],
            "paginas": datos["paginas"],
            "con_advertencia": datos["con_advertencia"],
            "filas": [
                {
                    "numero_fila": f["numero_fila"],
                    "identificacion": f.get("identificacion") or "",
                    "estado": f.get("estado"),
                    "avisos": f["avisos"],
                    "celdas": [
                        {
                            "nombre": c["nombre"],
                            "titulo": c["titulo"],
                            "obligatorio": c["obligatorio"],
                            "tipo_dato": c["campo"].get("tipo_dato"),
                            "valor": c["valor"],
                            "opciones": c["opciones"],
                            "tiene_aviso": c["tiene_aviso"],
                            "campo_id": c["campo"]["id"],
                            "observacion": por_celda.get(
                                (f["numero_fila"], c["campo"]["id"])
                            ),
                        }
                        for c in f["celdas"]
                    ],
                }
                for f in datos["filas"]
            ],
            "historial": edicion.historial_de(importacion_id)[:50],
            "descarga_historial": reverse(
                "api_mir:historial_xlsx", args=[importacion_id]
            ),
        }
        return Response(s.DatosSerializer(salida).data)

    @extend_schema(
        request=s.CorreccionSerializer,
        responses={
            200: s.CorreccionHechaSerializer,
            409: s.HaceFaltaConfirmarSerializer,
        },
    )
    def post(self, request, importacion_id):
        _exigir(request.user, "resultado")
        _importacion_permitida(request.user, importacion_id)
        if not puede_editar_datos(request.user):
            raise PermissionDenied(
                "El nivel nacional no modifica datos provinciales: observa."
            )
        pedido = s.CorreccionSerializer(data=request.data)
        pedido.is_valid(raise_exception=True)
        d = pedido.validated_data
        try:
            resultado = edicion.editar(
                importacion_id=importacion_id,
                hoja_id=d["hoja_id"],
                numero_fila=d["numero_fila"],
                nombre_campo=d["campo"],
                valor_nuevo=d["valor"],
                usuario=request.user.get_username(),
                motivo=d.get("motivo", ""),
                en_cascada=d.get("en_cascada", False),
            )
        except edicion.HaceFaltaConfirmar as aviso:
            # 409: el pedido es correcto, pero antes hay que decidir qué pasa
            # con las filas de otros archivos que usan este dato.
            usos = [
                {**g, "archivo_nombre": svc.con_nombres_de_archivo(g["archivo"])}
                for g in aviso.usos
            ]
            return Response(
                s.HaceFaltaConfirmarSerializer(
                    {"detail": str(aviso), "usos": usos}
                ).data,
                status=409,
            )
        except edicion.EdicionNoPermitida as error:
            raise ValidationError({"detail": str(error)}) from error
        datos = {
            "sin_cambios": resultado["sin_cambios"],
            "en_cascada": resultado.get("en_cascada") or 0,
            "valor": "" if resultado.get("valor") is None else str(resultado["valor"]),
            "advertencias": resultado.get("advertencias") or 0,
            "observaciones": resultado.get("observaciones") or [],
        }
        return Response(s.CorreccionHechaSerializer(datos).data)


# ---------------------------------------------------------------------------
# Reglas
# ---------------------------------------------------------------------------


def _techo(regla):
    if not regla:
        return None
    return {
        "minimo": como_se_escribe(regla.get("minimo")),
        "maximo": como_se_escribe(regla.get("maximo")),
        "texto": regla.get("texto") or "",
        "compartida": bool(regla.get("compartida")),
    }


class ReglasView(APIView):
    """Qué se espera en cada columna de una hoja, y —antes de abrir el período—
    los cambios del administrador."""

    @extend_schema(
        parameters=[OpenApiParameter("hoja", str)], responses=s.ReglasSerializer
    )
    def get(
        self, request
    ):  # pylint: disable=too-many-locals  # arma una pantalla entera
        _exigir(request.user, "estructura")
        hojas = []
        # Con el nombre corto del archivo, no con su código (27-09-2026).
        # Si el archivo tiene una sola hoja, basta con el archivo.
        nombres = svc.nombres_cortos()
        disponibles = svc.hojas_disponibles()
        cuantas: dict[str, int] = {}
        for h in disponibles:
            cuantas[h["archivo"]] = cuantas.get(h["archivo"], 0) + 1
        for h in disponibles:
            archivo = nombres.get(h["archivo"], h["archivo"])
            etiqueta = (
                archivo if cuantas[h["archivo"]] == 1 else f'{archivo} — {h["hoja"]}'
            )
            hojas.append({"clave": f'{h["archivo"]}|{h["hoja"]}', "etiqueta": etiqueta})
        claves = [h["clave"] for h in hojas]
        pedida = request.query_params.get("hoja")
        elegida = pedida if pedida in claves else (claves[0] if claves else "")
        archivo, _, nombre_hoja = elegida.partition("|")
        ver_tecnico = puede_administrar(request.user)

        campos = []
        if archivo and nombre_hoja:
            for c in svc.reglas_de_hoja(archivo, nombre_hoja):
                reglas = [_para_editar(r) for r in c["reglas"]]
                techos = _dos_techos(reglas)
                campos.append(
                    {
                        "id": c["id"],
                        "letra": _letra(c["orden"]),
                        "titulo": titulo_completo(c),
                        "nombre": c["nombre"] if ver_tecnico else "",
                        "ayuda": c.get("ayuda") or "",
                        "obligatorio": bool(c["obligatorio"]),
                        # Un campo con obligatoriedad condicionada no puede ser
                        # además obligatorio siempre: la casilla queda trabada.
                        "condicionado": any(
                            r["tipo_regla"] == "OBLIGATORIO_SI" for r in reglas
                        ),
                        # Sobre una lista cerrada un rango no significa nada.
                        "numerico": c.get("tipo_dato") in ("ENTERO", "DECIMAL")
                        and not c.get("catalogo"),
                        "valores": valores_admitidos(c),
                        "rangos": {
                            "avisa": _techo(techos["avisa"]),
                            "frena": _techo(techos["frena"]),
                        },
                        "otras": [
                            {
                                "aplicacion_id": r["aplicacion_id"],
                                "severidad": r["severidad"],
                                "texto": r.get("texto") or "",
                            }
                            for r in _las_demas(reglas, techos)
                        ],
                    }
                )
        abierto = reglas_service.periodo_abierto()
        datos = {
            "hojas": hojas,
            "hoja": elegida,
            "ver_tecnico": ver_tecnico,
            # La definición se cambia antes de abrir el período, no con el
            # operativo en curso.
            "puede_editar": ver_tecnico and not abierto,
            "periodo_abierto": abierto or None,
            "campos": campos,
        }
        return Response(s.ReglasSerializer(datos).data)

    @extend_schema(
        request=s.CambiosDeReglasSerializer, responses=s.ReglasGuardadasSerializer
    )
    def post(self, request):
        _exigir(request.user, "estructura")
        if not puede_administrar(request.user):
            raise PermissionDenied("Sólo el administrador puede cambiar las reglas.")
        pedido = s.CambiosDeReglasSerializer(data=request.data)
        pedido.is_valid(raise_exception=True)
        cambios = {}
        for c in pedido.validated_data["cambios"]:
            cambio = {}
            if "obligatorio" in c:
                cambio["obligatorio"] = c["obligatorio"]
            if "advierte" in c:
                cambio["advierte"] = tuple(c["advierte"])
            if "bloquea" in c:
                cambio["bloquea"] = tuple(c["bloquea"])
            cambios[c["campo_id"]] = cambio
        severidades = {
            x["aplicacion_id"]: x["severidad"]
            for x in pedido.validated_data["severidades"]
        }
        if not cambios and not severidades:
            return Response(
                {"mensaje": "No había nada que guardar.", "detalle": [], "errores": []}
            )
        try:
            hecho = reglas_service.guardar_hoja(cambios, severidades)
        except reglas_service.ErroresDeValidacion as problema:
            return Response(
                {
                    "mensaje": "No se guardó ningún cambio: corregí eso y volvé a guardar.",
                    "detalle": [],
                    "errores": list(problema.errores),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except (ValueError, reglas_service.NoSePuede) as error:
            raise ValidationError(
                {"detail": str(error) or "No se indicó qué cambiar."}
            ) from error
        if not hecho["detalle"]:
            return Response(
                {
                    "mensaje": "Los valores eran los mismos: no se cambió nada.",
                    "detalle": [],
                    "errores": [],
                }
            )
        return Response(
            {
                "mensaje": "Guardado. "
                + (
                    "1 cambio."
                    if len(hecho["detalle"]) == 1
                    else f'{len(hecho["detalle"])} cambios.'
                ),
                "detalle": list(hecho["detalle"]),
                "errores": [],
            }
        )


# ---------------------------------------------------------------------------
# Nivel nacional: estado de situación, observaciones y administración
# (maqueta aprobada por el responsable funcional el 27-09-2026)
# ---------------------------------------------------------------------------


class SituacionView(APIView):
    """Cómo viene cada provincia del operativo en el período."""

    @extend_schema(
        parameters=[OpenApiParameter("periodo", str)], responses=s.SituacionSerializer
    )
    def get(self, request):
        _exigir(request.user, "situacion")
        periodos, periodo = _periodos_y_elegido(request)
        datos = (
            situacion.situacion(periodo["codigo"])
            if periodo
            else {
                "operativo": 0,
                "totales": dict.fromkeys(situacion.GRUPOS.values(), 0),
                "filas": [],
            }
        )
        return Response(
            s.SituacionSerializer(
                {"periodos": periodos, "periodo": periodo, **datos}
            ).data
        )


class ObservacionesDelPeriodoView(APIView):
    """Todas las observaciones del período, con filtros, para el seguimiento."""

    @extend_schema(
        parameters=[
            OpenApiParameter("periodo", str),
            OpenApiParameter("jurisdiccion", str),
            OpenApiParameter("estado", str),
        ],
        responses=s.ObservacionesDelPeriodoSerializer,
    )
    def get(self, request):
        _exigir(request.user, "observaciones")
        periodos, periodo = _periodos_y_elegido(request)
        jurisdiccion = request.query_params.get("jurisdiccion") or None
        estado = request.query_params.get("estado") or None
        filas = (
            situacion.observaciones_del_periodo(periodo["codigo"], jurisdiccion, estado)
            if periodo
            else []
        )
        return Response(
            s.ObservacionesDelPeriodoSerializer(
                {
                    "periodos": periodos,
                    "periodo": periodo,
                    "jurisdicciones": situacion.operativo(),
                    "filas": filas,
                }
            ).data
        )


class AdministracionView(APIView):
    """Los períodos y las provincias del operativo. Sólo el administrador."""

    @extend_schema(responses=s.AdministracionSerializer)
    def get(self, request):
        _exigir(request.user, "administracion")
        periodos = []
        for p in svc.periodos():
            totales = situacion.situacion(p["codigo"])["totales"]
            periodos.append({**p, "presentaron": totales["presentaron"]})
        return Response(
            s.AdministracionSerializer(
                {
                    "periodos": periodos,
                    "operativo": len(situacion.operativo()),
                    "jurisdicciones": situacion.jurisdicciones(),
                    "todas": JURISDICCIONES,
                }
            ).data
        )


class OperativoView(APIView):
    """Suma o saca una provincia del operativo."""

    @extend_schema(request=s.CambioDeOperativoSerializer, responses=s.MensajeSerializer)
    def post(self, request):
        _exigir(request.user, "administracion")
        pedido = s.CambioDeOperativoSerializer(data=request.data)
        pedido.is_valid(raise_exception=True)
        d = pedido.validated_data
        if d["nombre"] not in JURISDICCIONES:
            raise ValidationError({"detail": "Esa jurisdicción no existe."})
        try:
            situacion.cambiar_operativo(d["nombre"], d["en_el_operativo"], request.user)
        except circuito.TransicionInvalida as error:
            raise ValidationError({"detail": str(error)}) from error
        accion = "entra al" if d["en_el_operativo"] else "sale del"
        return Response({"mensaje": f'{d["nombre"]} {accion} operativo.'})


class ResumenDeCierreView(APIView):
    """Lo que hay y lo que falta, antes de cerrar el período para todas."""

    @extend_schema(responses=s.ResumenDeCierreSerializer)
    def get(self, request, codigo):
        _exigir(request.user, "administracion")
        periodo = next((p for p in svc.periodos() if p["codigo"] == codigo), None)
        if not periodo:
            raise NotFound("No existe ese período.")
        return Response(
            s.ResumenDeCierreSerializer(
                {"periodo": periodo, "grupos": situacion.resumen_de_cierre(codigo)}
            ).data
        )


class HistorialDeLaPresentacionView(APIView):
    """El historial de cambios de toda la presentación, junto."""

    @extend_schema(responses=s.HistorialDeLaPresentacionSerializer)
    def get(self, request, presentacion_id):
        _exigir(request.user, "resultado")
        _presentacion_permitida(request.user, presentacion_id)
        return Response(
            s.HistorialDeLaPresentacionSerializer(
                {"filas": situacion.historial_de_la_presentacion(presentacion_id)}
            ).data
        )
