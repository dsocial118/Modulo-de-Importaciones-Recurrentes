"""Pantalla de edición: corregir un dato ya importado.

Es el paso 5 del circuito, en su segunda forma: las advertencias se resuelven
acá, sin volver a importar el archivo. Los errores bloqueantes no llegan a esta
pantalla, porque un archivo con bloqueantes no incorpora ninguna fila.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from runac.permissions import SeccionPermitidaMixin, puede_editar_datos
from runac.services import edicion_service as edicion


class EdicionView(SeccionPermitidaMixin, LoginRequiredMixin, TemplateView):
    """Los datos importados de una hoja, para revisar y corregir."""

    seccion = "resultado"
    template_name = "runac/edicion.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        importacion_id = int(kwargs["importacion_id"])
        contexto = edicion.contexto_de(importacion_id)
        if not contexto:
            raise Http404("No existe esa importación.")
        if not contexto["hojas"]:
            raise Http404("La importación no tiene hojas definidas.")

        # Qué hoja se está mirando: la pedida, o la primera.
        pedida = self.request.GET.get("hoja")
        hoja = next(
            (h for h in contexto["hojas"] if str(h["id"]) == str(pedida)),
            contexto["hojas"][0],
        )

        datos = edicion.datos_de_la_hoja(
            importacion_id,
            hoja,
            pagina=self.request.GET.get("pagina", 1),
            solo_con_advertencia=self.request.GET.get("solo") == "avisos",
        )

        # Los valores admitidos de cada campo con lista cerrada: el operador
        # elige, no escribe.
        opciones = {
            c["nombre"]: edicion.opciones_de(c["catalogo"])
            for c in datos["campos"]
            if c.get("catalogo")
        }

        ctx.update(
            datos,
            opciones=opciones,
            puede_editar=(
                puede_editar_datos(self.request.user) and contexto["editable"]
            ),
            solo_avisos=self.request.GET.get("solo") == "avisos",
            historial=edicion.historial_de(importacion_id)[:20],
        )
        return ctx


class EditarCampoView(SeccionPermitidaMixin, LoginRequiredMixin, View):
    """Guarda la corrección de un dato. Responde en JSON o redirige."""

    seccion = "resultado"

    def post(self, request, importacion_id):
        if not puede_editar_datos(request.user):
            raise PermissionDenied(
                "El nivel nacional no modifica datos provinciales: observa."
            )

        try:
            resultado = edicion.editar(
                importacion_id=importacion_id,
                hoja_id=request.POST.get("hoja_id"),
                numero_fila=int(request.POST.get("numero_fila")),
                nombre_campo=request.POST.get("campo", ""),
                valor_nuevo=request.POST.get("valor", ""),
                usuario=request.user.get_username(),
                motivo=request.POST.get("motivo", ""),
            )
        except edicion.EdicionNoPermitida as e:
            if _pide_json(request):
                return JsonResponse({"ok": False, "error": str(e)}, status=400)
            messages.error(request, str(e))
            return self._volver(request, importacion_id)
        except (TypeError, ValueError):
            mensaje = "Faltan datos para identificar la celda que se quiere corregir."
            if _pide_json(request):
                return JsonResponse({"ok": False, "error": mensaje}, status=400)
            messages.error(request, mensaje)
            return self._volver(request, importacion_id)

        if _pide_json(request):
            return JsonResponse(
                {
                    "ok": True,
                    "sin_cambios": resultado["sin_cambios"],
                    "valor": (
                        "" if resultado["valor"] is None else str(resultado["valor"])
                    ),
                }
            )

        if resultado["sin_cambios"]:
            messages.info(request, "El valor era el mismo: no se registró un cambio.")
        else:
            messages.success(
                request, "Dato corregido. Queda registrado en el historial."
            )
        return self._volver(request, importacion_id)

    @staticmethod
    def _volver(request, importacion_id):
        destino = request.POST.get("volver")
        if destino:
            return redirect(destino)
        return redirect(reverse("runac:edicion", args=[importacion_id]))


def _pide_json(request) -> bool:
    """La edición en línea responde JSON; el formulario completo, una página."""
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"
