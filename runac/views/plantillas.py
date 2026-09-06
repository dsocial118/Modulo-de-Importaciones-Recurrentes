"""Descarga de las plantillas del período."""

import io
import zipfile
from pathlib import Path

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import FileResponse, Http404, HttpResponse
from django.views.generic import TemplateView

from runac.services import importacion_service as svc


def _ruta_de_plantilla(codigo: str, periodo: str) -> Path:
    return Path(settings.RUNAC_PLANTILLAS) / f"{codigo}_{periodo}_MODELO.xlsx"


class PlantillasView(LoginRequiredMixin, TemplateView):
    template_name = "runac/plantillas.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        periodo = self.request.GET.get("periodo") or "2026_T1"
        archivos = svc.archivos_esperados(periodo)
        for a in archivos:
            ruta = _ruta_de_plantilla(a["codigo"], periodo)
            a["existe"] = ruta.exists()
            a["kb"] = int(ruta.stat().st_size / 1024) if ruta.exists() else None
        ctx["periodo_elegido"] = periodo
        ctx["periodos"] = svc.periodos()
        ctx["archivos"] = archivos
        return ctx


def descargar_plantilla(request, codigo, periodo):
    ruta = _ruta_de_plantilla(codigo, periodo)
    if not ruta.exists():
        raise Http404("Todavía no se generó la plantilla de ese archivo.")
    return FileResponse(open(ruta, "rb"), as_attachment=True, filename=ruta.name)


def descargar_todas(request, periodo):
    """Todas las plantillas del período en un solo zip."""
    archivos = svc.archivos_esperados(periodo)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z:
        for a in archivos:
            ruta = _ruta_de_plantilla(a["codigo"], periodo)
            if ruta.exists():
                z.write(ruta, ruta.name)
    buffer.seek(0)
    respuesta = HttpResponse(buffer.read(), content_type="application/zip")
    respuesta["Content-Disposition"] = f'attachment; filename="RUNAC_plantillas_{periodo}.zip"'
    return respuesta
