"""Descarga de las plantillas del período.

Se generan al pedirlas. Ver `runac/services/plantillas_service.py`: antes eran
archivos en disco y la provincia podía bajar una que ya no correspondía.
"""

import io
import shutil
import zipfile
from pathlib import Path

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import FileResponse, HttpResponse
from django.views.generic import TemplateView

from runac.permissions import SeccionPermitidaMixin

from runac.services import importacion_service as svc
from runac.services import plantillas_service as plantillas


class PlantillasView(SeccionPermitidaMixin, LoginRequiredMixin, TemplateView):
    seccion = "plantillas"
    template_name = "runac/plantillas.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        periodo = self.request.GET.get("periodo") or "2026_T1"
        archivos = svc.archivos_esperados(periodo)
        for a in archivos:
            a["nombre_plantilla"] = plantillas.nombre_de_archivo(a["codigo"], periodo)
        ctx["periodo_elegido"] = periodo
        ctx["periodos"] = svc.periodos()
        ctx["archivos"] = archivos
        return ctx


def descargar_plantilla(request, codigo, periodo):
    ruta = Path(plantillas.generar(codigo, periodo))
    # `FileResponse` cierra el archivo al terminar de mandarlo; la carpeta
    # temporal se borra acá porque ya está leído en memoria por el handler.
    respuesta = FileResponse(
        io.BytesIO(ruta.read_bytes()),
        as_attachment=True,
        filename=ruta.name,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    shutil.rmtree(ruta.parent, ignore_errors=True)
    return respuesta


def descargar_todas(request, periodo):
    """Todas las plantillas del período en un solo zip."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z:
        for a in svc.archivos_esperados(periodo):
            ruta = Path(plantillas.generar(a["codigo"], periodo))
            z.write(ruta, ruta.name)
            shutil.rmtree(ruta.parent, ignore_errors=True)
    buffer.seek(0)
    respuesta = HttpResponse(buffer.read(), content_type="application/zip")
    respuesta["Content-Disposition"] = (
        f'attachment; filename="RUNAC_plantillas_{periodo}.zip"'
    )
    return respuesta
