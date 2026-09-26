"""Carga de archivos: subir de a uno, ver el resultado y el detalle.

La modalidad es la que define el análisis funcional para la primera versión:
**los archivos se cargan de a uno, y el operador indica de qué archivo se trata**.
El sistema no lo deduce del nombre: lo usa para verificar que el archivo sea el
declarado y que corresponda al período y a la jurisdicción en curso. Si no
corresponde, no se importa. El orden de importación lo controla el sistema, no
el operador.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import connection
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from runac.permissions import (
    SeccionPermitidaMixin,
    es_nacional,
    jurisdiccion_de,
    puede_cargar,
    puede_presentar,
)
from runac.services import alcance_service as alcance
from runac.services import circuito_service as circuito
from runac.services import importacion_service as svc


def jurisdiccion_en_curso(request) -> str:
    """La jurisdicción sobre la que se está trabajando.

    **Un usuario provincial trabaja sólo sobre la suya**, pida lo que pida: sale
    de su usuario, no de la dirección ni de la sesión. Hasta el 25-09-2026 la
    elegía el selector —una herramienta de prueba— y con eso un operador de
    Chubut podía cargar, ver y corregir en Chaco (hallazgo #10 de auditoría).

    El nivel nacional sí elige, sólo entre las que existen, y **la elección se
    recuerda**: si no, cada pantalla mostraba una jurisdicción distinta.

    Al integrar a SISOC esto desaparece: el alcance territorial lo resuelve el
    sistema.
    """
    if not es_nacional(request.user):
        return jurisdiccion_de(request.user)
    elegida = request.GET.get("jurisdiccion") or request.POST.get("jurisdiccion")
    if elegida in JURISDICCIONES:
        request.session["jurisdiccion"] = elegida
        return elegida
    guardada = request.session.get("jurisdiccion")
    return guardada if guardada in JURISDICCIONES else "Chubut"


# Nombre corto, para las vistas de este módulo.
_jurisdiccion = jurisdiccion_en_curso


def _ultima_importacion(filas, codigo) -> dict:
    """Cómo le fue al archivo que se acaba de importar.

    Se lee del registro de la importación y no de contadores calculados en la
    vista: un archivo rechazado por estructura no trae conteo de bloqueantes, y
    contar cero llevaba a anunciar «importación correcta» sobre algo que había
    fallado. El estado registrado es el que sabe la verdad.
    """
    vacio = {
        "recien_importado": None,
        "recien_estado": None,
        "recien_bloqueantes": 0,
        "recien_advertencias": 0,
        "recien_importacion_id": None,
    }
    if not codigo:
        return vacio

    for fila in filas:
        if fila.get("codigo") != codigo:
            continue
        imp = fila.get("importacion")
        if not imp:
            # Rechazado antes de registrarse: no hay importación que mostrar.
            return {**vacio, "recien_importado": codigo, "recien_estado": "FALLIDA"}
        return {
            "recien_importado": codigo,
            "recien_estado": imp.get("estado"),
            "recien_bloqueantes": imp.get("bloqueantes") or 0,
            "recien_advertencias": imp.get("advertencias") or 0,
            "recien_importacion_id": imp.get("id"),
        }
    return vacio


class CargarView(SeccionPermitidaMixin, LoginRequiredMixin, TemplateView):
    """Los archivos del período, con su estado y el botón para subir cada uno."""

    seccion = "cargar"
    template_name = "runac/cargar.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        periodo = self.request.GET.get("periodo") or "2026_T1"
        jurisdiccion = _jurisdiccion(self.request)
        estado = svc.estado_de_la_presentacion(jurisdiccion, periodo)

        filas = []
        for a in estado["archivos"]:
            faltan = svc.dependencias_faltantes(a["codigo"], jurisdiccion, periodo)
            filas.append(
                {
                    **a,
                    # Lo que nombra, esté importado o no: se muestra siempre,
                    # para que se sepa antes de intentar.
                    "necesita": svc.archivos_referenciados(a["codigo"], periodo),
                    "bloqueado_por": [f["codigo"] for f in faltan],
                    "nombre_sugerido": f'{a["codigo"]}_{periodo}_{jurisdiccion}.xlsx',
                }
            )

        pres = estado["presentacion"]
        estado_codigo = pres["estado"] if pres else "EN_CARGA"

        ctx.update(
            {
                "periodo_elegido": periodo,
                "periodos": svc.periodos(),
                "jurisdiccion": jurisdiccion,
                "jurisdicciones": JURISDICCIONES,
                "archivos": filas,
                "presentacion": pres,
                "estado_legible": circuito.estado_legible(estado_codigo),
                # Con la carga cerrada no se importa: primero hay que reabrirla.
                "carga_abierta": estado_codigo == "EN_CARGA",
                "puede_cargar": puede_cargar(self.request.user),
                "listo": estado["listo"],
            }
        )
        return ctx


class CargarArchivoView(SeccionPermitidaMixin, LoginRequiredMixin, View):
    """Sube UN archivo, declarado por el operador."""

    seccion = "cargar"

    def post(self, request, codigo):
        periodo = request.POST.get("periodo") or "2026_T1"
        jurisdiccion = _jurisdiccion(request)
        volver = (
            f'{reverse("runac:cargar")}?periodo={periodo}&jurisdiccion={jurisdiccion}'
        )

        if not puede_cargar(request.user):
            messages.error(request, "Tu rol no puede importar archivos.")
            return redirect(volver)

        fichero = request.FILES.get("archivo")
        if not fichero:
            messages.error(request, "No se seleccionó ningún archivo.")
            return redirect(volver)

        resultado = svc.importar_uno(
            codigo, fichero, jurisdiccion, periodo, request.user.get_username()
        )
        if resultado.get("rechazado"):
            messages.error(request, resultado["mensaje"])
            return redirect(volver)

        # El resultado se lee de la importación registrada y no de contadores
        # armados acá: un rechazo por estructura no trae conteo de bloqueantes,
        # y el aviso terminaba anunciando «importación correcta» sobre un
        # archivo que había fallado.
        return redirect(
            f'{reverse("runac:resultado")}?periodo={periodo}'
            f"&jurisdiccion={jurisdiccion}&importado={codigo}"
        )


class ResultadoView(SeccionPermitidaMixin, LoginRequiredMixin, TemplateView):
    """El estado del período: qué se importó, qué observó Nación y qué falta."""

    seccion = "resultado"
    template_name = "runac/resultado.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        periodo = self.request.GET.get("periodo") or "2026_T1"
        jurisdiccion = _jurisdiccion(self.request)
        estado = svc.estado_de_la_presentacion(jurisdiccion, periodo)

        filas = []
        for a in estado["archivos"]:
            imp = a.get("importacion")
            fila = {**a}
            if imp:
                fila["resumen"] = svc.resumen_de_hallazgos(imp["id"])[:6]
            filas.append(fila)

        pres = estado["presentacion"]
        estado_codigo = pres["estado"] if pres else "EN_CARGA"
        nombre, ayuda, _ = circuito.ESTADOS.get(
            estado_codigo, (estado_codigo, "", "secondary")
        )
        recien = self.request.GET.get("importado")

        ctx.update(
            {
                "periodo_elegido": periodo,
                "jurisdiccion": jurisdiccion,
                "jurisdicciones": JURISDICCIONES,
                "periodos": svc.periodos(),
                "archivos": filas,
                "presentacion": pres,
                "listo": estado["listo"],
                # Lo que se acaba de importar, para el aviso de resultado.
                **_ultima_importacion(filas, recien),
                "estado_legible": nombre,
                "estado_ayuda": ayuda,
                "pasos": _pasos_del_circuito(estado_codigo),
                "acciones": circuito.acciones_disponibles(
                    pres, self.request.user, estado["listo"]
                ),
                "observaciones": circuito.observaciones_de(pres["id"]) if pres else [],
                "puede_responder": puede_cargar(self.request.user)
                or puede_presentar(self.request.user),
                "puede_presentar": puede_presentar(self.request.user),
                "totales": {
                    "filas": sum(
                        (a["importacion"] or {}).get("filas_leidas", 0) or 0
                        for a in estado["archivos"]
                    ),
                    "validas": sum(
                        (a["importacion"] or {}).get("filas_incorporadas", 0) or 0
                        for a in estado["archivos"]
                    ),
                    "bloqueantes": sum(
                        (a["importacion"] or {}).get("bloqueantes", 0) or 0
                        for a in estado["archivos"]
                    ),
                    "advertencias": sum(
                        (a["importacion"] or {}).get("advertencias", 0) or 0
                        for a in estado["archivos"]
                    ),
                },
            }
        )
        return ctx


class DetalleView(SeccionPermitidaMixin, LoginRequiredMixin, TemplateView):
    """El detalle fila por fila de una importación."""

    seccion = "resultado"
    template_name = "runac/detalle.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        importacion_id = int(kwargs["importacion_id"])
        alcance.exigir_importacion(self.request.user, importacion_id)
        severidad = self.request.GET.get("severidad") or None
        hoja = self.request.GET.get("hoja") or None
        buscar = self.request.GET.get("buscar") or None

        with connection.cursor() as cur:
            cur.execute(
                """
                SELECT i.*, a.codigo AS archivo_codigo, av.titulo AS archivo_titulo,
                       av.numero AS version
                FROM mir_c2_importacion i
                LEFT JOIN mir_c1_archivo a ON a.id = i.archivo_id
                LEFT JOIN mir_c1_archivo_version av ON av.id = i.archivo_version_id
                WHERE i.id = %s
            """,
                [importacion_id],
            )
            columnas = [c[0] for c in cur.description]
            fila = cur.fetchone()
            importacion = dict(zip(columnas, fila)) if fila else None

            cur.execute(
                """SELECT DISTINCT nombre_hoja FROM mir_c2_reglas_incumplidas
                           WHERE importacion_id = %s AND nombre_hoja IS NOT NULL""",
                [importacion_id],
            )
            hojas = [r[0] for r in cur.fetchall()]

            # Los problemas del archivo entero van aparte de las reglas incumplidas.
            cur.execute(
                """SELECT tipo, hoja, numero_fila, esperado, encontrado, descripcion
                           FROM mir_c2_errores_de_importacion
                           WHERE importacion_id = %s ORDER BY id LIMIT 200""",
                [importacion_id],
            )
            columnas = [c[0] for c in cur.description]
            errores_archivo = [dict(zip(columnas, f)) for f in cur.fetchall()]

        hallazgos = svc.hallazgos_de(importacion_id, severidad, hoja, buscar)
        resumen = svc.resumen_de_hallazgos(importacion_id)
        # Una importación que entró tiene sólo advertencias, y una que falló casi
        # siempre sólo bloqueantes: repetir la palabra en cada fila es una columna
        # entera con el mismo valor, y ofrecer un filtro por algo que no varía no
        # filtra nada. Cuando están mezcladas —pasa en un archivo que falla y
        # además trae observaciones— las dos cosas sí hacen falta.
        #
        # Se mira el archivo COMPLETO y no lo que quedó filtrado: si se mirara lo
        # filtrado, elegir «bloqueantes» dejaría un solo valor a la vista, el
        # filtro desaparecería y no habría forma de volver.
        severidades = {r["severidad"] for r in resumen}
        ctx.update(
            {
                "importacion": importacion,
                "hojas": hojas,
                "errores_archivo": errores_archivo,
                "resumen": resumen,
                "hallazgos": hallazgos,
                "severidad_unica": (
                    next(iter(severidades)) if len(severidades) == 1 else None
                ),
                "filtro": {
                    "severidad": severidad or "",
                    "hoja": hoja or "",
                    "buscar": buscar or "",
                },
            }
        )
        return ctx


# Los nueve pasos del análisis funcional, agrupados como los ve la jurisdicción.
# Sirven para mostrar en qué punto del circuito está la presentación.
PASOS = [
    ("Carga", ("EN_CARGA",)),
    ("Validación", ("EN_CARGA",)),
    ("Corrección", ("EN_CARGA",)),
    ("Cierre de carga", ("CERRADA",)),
    ("Revisión nacional", ("EN_REVISION",)),
    ("Subsanación", ("OBSERVADA", "SUBSANADA")),
    ("Presentación", ("HABILITADA", "PRESENTADA")),
    ("Consolidación", ("CONSOLIDADA",)),
]


def _pasos_del_circuito(estado: str):
    return [
        {"nombre": nombre, "actual": estado in estados} for nombre, estados in PASOS
    ]


JURISDICCIONES = [
    "Buenos Aires",
    "CABA",
    "Catamarca",
    "Chaco",
    "Chubut",
    "Córdoba",
    "Corrientes",
    "Entre Ríos",
    "Formosa",
    "Jujuy",
    "La Pampa",
    "La Rioja",
    "Mendoza",
    "Misiones",
    "Neuquén",
    "Río Negro",
    "Salta",
    "San Juan",
    "San Luis",
    "Santa Cruz",
    "Santa Fe",
    "Santiago del Estero",
    "Tierra del Fuego",
    "Tucumán",
]
