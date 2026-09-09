"""Carga de archivos: subir de a uno, ver el resultado y el detalle.

La modalidad es la que define el análisis funcional para la primera versión:
**los archivos se cargan de a uno, y el operador indica de qué archivo se trata**.
El sistema no lo deduce del nombre, y el orden de importación lo controla el
sistema, no el operador.
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
    jurisdiccion_de,
    puede_cargar,
    puede_presentar,
)
from runac.services import circuito_service as circuito
from runac.services import importacion_service as svc


def jurisdiccion_en_curso(request) -> str:
    """La jurisdicción sobre la que se está trabajando.

    En el prototipo se puede elegir, y **la elección se recuerda**: si no, cada
    pantalla mostraba una jurisdicción distinta —Inicio la del usuario y Cargar
    la elegida— y eso confunde más de lo que ayuda.

    Al integrar a SISOC esto desaparece: el alcance territorial lo resuelve el
    sistema y el operador no elige nada.
    """
    elegida = request.GET.get("jurisdiccion") or request.POST.get("jurisdiccion")
    if elegida:
        request.session["jurisdiccion"] = elegida
        return elegida
    return (
        request.session.get("jurisdiccion") or jurisdiccion_de(request.user) or "Chaco"
    )


# Nombre corto, para las vistas de este módulo.
_jurisdiccion = jurisdiccion_en_curso


def _entero(valor) -> int:
    try:
        return int(valor)
    except (TypeError, ValueError):
        return 0


def _importacion_de(filas, codigo):
    """El id de la importación recién hecha, para enlazar sus dos informes."""
    if not codigo:
        return None
    for fila in filas:
        if fila.get("codigo") == codigo and fila.get("importacion"):
            return fila["importacion"]["id"]
    return None


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

        if resultado.get("nombre_inesperado"):
            messages.warning(
                request,
                f"El nombre «{fichero.name}» no se corresponde con el período o la "
                f'jurisdicción en curso. Se esperaba «{resultado["nombre_sugerido"]}». '
                f"Es una advertencia: el archivo se procesó igual.",
            )

        resumen = resultado.get("resumen") or []
        bloqueantes = sum((r or {}).get("bloqueantes", 0) or 0 for r in resumen)
        advertencias = sum((r or {}).get("advertencias", 0) or 0 for r in resumen)

        if bloqueantes:
            messages.error(
                request,
                f"{codigo}: se detectaron {bloqueantes} errores bloqueantes. "
                f"No se incorporó ningún registro de este archivo. "
                f"Hay que corregir el Excel y volver a importarlo.",
            )
        else:
            messages.success(request, f"{codigo}: se importó correctamente.")

        # El resultado se muestra además como aviso al llegar a la pantalla: si
        # sólo va en la franja de mensajes, se pierde entre el resto.
        return redirect(
            f'{reverse("runac:resultado")}?periodo={periodo}'
            f"&jurisdiccion={jurisdiccion}"
            f"&importado={codigo}&bloqueantes={bloqueantes}"
            f"&advertencias={advertencias}"
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
                "recien_importado": recien,
                "recien_bloqueantes": _entero(self.request.GET.get("bloqueantes")),
                "recien_advertencias": _entero(self.request.GET.get("advertencias")),
                "recien_importacion_id": _importacion_de(filas, recien),
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
        severidad = self.request.GET.get("severidad") or None
        hoja = self.request.GET.get("hoja") or None
        buscar = self.request.GET.get("buscar") or None

        with connection.cursor() as cur:
            cur.execute(
                """
                SELECT i.*, a.codigo AS archivo_codigo, av.titulo AS archivo_titulo,
                       av.numero AS version
                FROM runac_c2_importacion i
                LEFT JOIN runac_c1_archivo a ON a.id = i.archivo_id
                LEFT JOIN runac_c1_archivo_version av ON av.id = i.archivo_version_id
                WHERE i.id = %s
            """,
                [importacion_id],
            )
            columnas = [c[0] for c in cur.description]
            fila = cur.fetchone()
            importacion = dict(zip(columnas, fila)) if fila else None

            cur.execute(
                """SELECT DISTINCT nombre_hoja FROM runac_c2_reglas_incumplidas
                           WHERE importacion_id = %s AND nombre_hoja IS NOT NULL""",
                [importacion_id],
            )
            hojas = [r[0] for r in cur.fetchall()]

            # Los problemas del archivo entero van aparte de las reglas incumplidas.
            cur.execute(
                """SELECT tipo, hoja, numero_fila, esperado, encontrado, descripcion
                           FROM runac_c2_errores_de_importacion
                           WHERE importacion_id = %s ORDER BY id LIMIT 200""",
                [importacion_id],
            )
            columnas = [c[0] for c in cur.description]
            errores_archivo = [dict(zip(columnas, f)) for f in cur.fetchall()]

        ctx.update(
            {
                "importacion": importacion,
                "hojas": hojas,
                "errores_archivo": errores_archivo,
                "resumen": svc.resumen_de_hallazgos(importacion_id),
                "hallazgos": svc.hallazgos_de(importacion_id, severidad, hoja, buscar),
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
