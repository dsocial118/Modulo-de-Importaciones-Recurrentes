"""Carga de archivos: subir, reconocer, procesar y ver el resultado."""

from pathlib import Path

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import connection
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from runac.permissions import jurisdiccion_de
from runac.services import importacion_service as svc


def _jurisdiccion(request) -> str:
    """En el prototipo la jurisdicción puede venir del usuario o elegirse."""
    return (request.GET.get("jurisdiccion")
            or request.POST.get("jurisdiccion")
            or jurisdiccion_de(request.user)
            or request.session.get("jurisdiccion")
            or "Chaco")


class CargarView(LoginRequiredMixin, TemplateView):
    """Paso 1: elegir los archivos. Paso 2: confirmar el reconocimiento."""

    template_name = "runac/cargar.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["periodo_elegido"] = self.request.GET.get("periodo") or "2026_T1"
        ctx["periodos"] = svc.periodos()
        ctx["jurisdiccion"] = _jurisdiccion(self.request)
        ctx["jurisdicciones"] = JURISDICCIONES
        return ctx

    def post(self, request, *args, **kwargs):
        archivos = request.FILES.getlist("archivos")
        periodo = request.POST.get("periodo", "2026_T1")
        jurisdiccion = _jurisdiccion(request)
        if not archivos:
            messages.error(request, "No se seleccionó ningún archivo.")
            return redirect(f'{reverse("runac:cargar")}?periodo={periodo}')

        carpeta = svc.guardar_archivos(archivos, jurisdiccion, periodo)
        reconocimiento = svc.reconocer(carpeta, periodo)

        request.session["carga"] = {
            "carpeta": str(carpeta), "periodo": periodo, "jurisdiccion": jurisdiccion,
        }
        return render(request, "runac/reconocer.html", {
            "reconocimiento": reconocimiento,
            "periodo_elegido": periodo,
            "jurisdiccion": jurisdiccion,
            "todos_los_archivos": svc.archivos_esperados(periodo),
            "puede_procesar": not reconocimiento["ambiguos"] and bool(reconocimiento["reconocidos"]),
        })


class ProcesarView(LoginRequiredMixin, View):
    """Paso 3: correr el motor sobre lo que se confirmó."""

    def post(self, request, *args, **kwargs):
        carga = request.session.get("carga")
        if not carga:
            messages.error(request, "Se perdió el contexto de la carga. Volvé a subir los archivos.")
            return redirect("runac:cargar")

        asignacion = {k.removeprefix("asignar_"): v
                      for k, v in request.POST.items()
                      if k.startswith("asignar_") and v and v != "ninguno"}

        resultado = svc.procesar(
            carpeta=Path(carga["carpeta"]),
            jurisdiccion=carga["jurisdiccion"],
            codigo_periodo=carga["periodo"],
            usuario=request.user.get_username(),
            asignacion=asignacion,
        )
        request.session["ultimo_resultado"] = {
            "periodo": carga["periodo"], "jurisdiccion": carga["jurisdiccion"],
            "presentacion_id": resultado.get("presentacion_id"),
        }
        return redirect(f'{reverse("runac:resultado")}?periodo={carga["periodo"]}'
                        f'&jurisdiccion={carga["jurisdiccion"]}')


class ResultadoView(LoginRequiredMixin, TemplateView):
    """Paso 4: el resumen de lo que pasó, por archivo."""

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

        ctx.update({
            "periodo_elegido": periodo, "jurisdiccion": jurisdiccion,
            "archivos": filas, "presentacion": estado["presentacion"],
            "listo": estado["listo"],
            "totales": {
                "filas": sum((a["importacion"] or {}).get("filas_totales", 0) or 0 for a in estado["archivos"]),
                "validas": sum((a["importacion"] or {}).get("filas_validas", 0) or 0 for a in estado["archivos"]),
                "bloqueantes": sum((a["importacion"] or {}).get("bloqueantes", 0) or 0 for a in estado["archivos"]),
                "advertencias": sum((a["importacion"] or {}).get("advertencias", 0) or 0 for a in estado["archivos"]),
            },
        })
        return ctx


class DetalleView(LoginRequiredMixin, TemplateView):
    """El detalle fila por fila de una importación."""

    template_name = "runac/detalle.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        importacion_id = int(kwargs["importacion_id"])
        severidad = self.request.GET.get("severidad") or None
        hoja = self.request.GET.get("hoja") or None
        buscar = self.request.GET.get("buscar") or None

        with connection.cursor() as cur:
            cur.execute("""
                SELECT i.*, a.codigo AS archivo_codigo, a.titulo AS archivo_titulo
                FROM runac_c2_importacion i
                LEFT JOIN runac_c2_estructura e ON e.id = i.estructura_id
                LEFT JOIN runac_c1_archivo a ON a.id = e.archivo_id
                WHERE i.id = %s
            """, [importacion_id])
            columnas = [c[0] for c in cur.description]
            fila = cur.fetchone()
            importacion = dict(zip(columnas, fila)) if fila else None

            cur.execute("""SELECT DISTINCT nombre_hoja FROM runac_c2_hallazgo
                           WHERE importacion_id = %s AND nombre_hoja IS NOT NULL""", [importacion_id])
            hojas = [r[0] for r in cur.fetchall()]

        ctx.update({
            "importacion": importacion,
            "hojas": hojas,
            "resumen": svc.resumen_de_hallazgos(importacion_id),
            "hallazgos": svc.hallazgos_de(importacion_id, severidad, hoja, buscar),
            "filtro": {"severidad": severidad or "", "hoja": hoja or "", "buscar": buscar or ""},
        })
        return ctx


JURISDICCIONES = [
    "Buenos Aires", "CABA", "Catamarca", "Chaco", "Chubut", "Córdoba", "Corrientes",
    "Entre Ríos", "Formosa", "Jujuy", "La Pampa", "La Rioja", "Mendoza", "Misiones",
    "Neuquén", "Río Negro", "Salta", "San Juan", "San Luis", "Santa Cruz", "Santa Fe",
    "Santiago del Estero", "Tierra del Fuego", "Tucumán",
]
