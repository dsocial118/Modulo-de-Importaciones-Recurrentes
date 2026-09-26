"""Acciones del circuito: cierre de carga, revisión, observaciones y presentación.

Las vistas no deciden nada: piden una acción al servicio, que valida el estado
de origen y el rol. Si no corresponde, el servicio levanta TransicionInvalida y
acá se muestra como mensaje.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import TemplateView

from runac.permissions import (
    SeccionPermitidaMixin,
    es_nacional,
    puede_administrar,
    puede_revisar,
)
from runac.services import alcance_service as alcance
from runac.services import circuito_service as circuito
from runac.services import demo_service
from runac.services import informe_errores_service as informes
from runac.services import importacion_service as svc


def _volver(request, presentacion_id=None):
    """A dónde vuelve el operador después de una acción del circuito.

    El destino viaja en el formulario, así que lo escribe el navegador y puede
    escribirlo cualquiera: un enlace preparado con `?volver=https://…` mandaba
    a la persona a otro sitio después de operar, con la sesión abierta y la
    apariencia de seguir dentro del sistema. Sólo se aceptan destinos de esta
    misma aplicación.
    """
    destino = request.POST.get("volver") or request.GET.get("volver")
    if destino and url_has_allowed_host_and_scheme(
        destino, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return redirect(destino)
    periodo = request.POST.get("periodo") or "2026_T1"
    jurisdiccion = request.POST.get("jurisdiccion") or ""
    return redirect(
        f'{reverse("runac:resultado")}?periodo={periodo}'
        f"&jurisdiccion={jurisdiccion}"
    )


class AccionView(SeccionPermitidaMixin, LoginRequiredMixin, View):
    """Ejecuta una transición del circuito."""

    seccion = "resultado"

    def post(self, request, presentacion_id, accion):
        alcance.exigir_presentacion(request.user, presentacion_id)
        # La completitud se calcula desde la presentación de la URL y no desde
        # lo que manda el formulario. Antes salía de la jurisdicción enviada por
        # el navegador y, si faltaba, el valor por defecto era «listo»: bastaba
        # omitir un parámetro para cerrar una carga incompleta.
        try:
            nuevo = circuito.ejecutar(
                presentacion_id,
                accion,
                request.user,
                listo=svc.presentacion_completa(presentacion_id),
            )
            messages.success(
                request,
                f"{circuito.ETIQUETAS[accion]}: la presentación quedó en "
                f"«{circuito.estado_legible(nuevo)}».",
            )
        except circuito.TransicionInvalida as e:
            messages.error(request, str(e))
        return _volver(request, presentacion_id)


class ObservarView(SeccionPermitidaMixin, LoginRequiredMixin, View):
    """El revisor nacional formula una observación. No modifica el dato."""

    seccion = "revision"

    def post(self, request, presentacion_id):
        alcance.exigir_presentacion(request.user, presentacion_id)
        try:
            circuito.crear_observacion(
                presentacion_id,
                request.user,
                texto=request.POST.get("texto", ""),
                ubicacion={
                    "importacion_id": request.POST.get("importacion_id") or None,
                    "numero_fila": request.POST.get("numero_fila") or None,
                    "identificador_registro": (
                        request.POST.get("identificador_registro") or None
                    ),
                },
            )
            messages.success(
                request,
                "Observación registrada. La presentación volvió "
                "a la jurisdicción para su subsanación.",
            )
        except circuito.TransicionInvalida as e:
            messages.error(request, str(e))
        return _volver(request, presentacion_id)


class ResponderView(SeccionPermitidaMixin, LoginRequiredMixin, View):
    """La jurisdicción responde una observación."""

    seccion = "resultado"

    def post(self, request, observacion_id):
        alcance.exigir_observacion(request.user, observacion_id)
        try:
            circuito.responder_observacion(
                observacion_id, request.user, request.POST.get("respuesta", "")
            )
            messages.success(request, "Respuesta registrada.")
        except circuito.TransicionInvalida as e:
            messages.error(request, str(e))
        return _volver(request)


class ExpedienteView(SeccionPermitidaMixin, LoginRequiredMixin, View):
    """Registra el número GDE, después de remitir el comprobante."""

    seccion = "resultado"

    def post(self, request, presentacion_id):
        alcance.exigir_presentacion(request.user, presentacion_id)
        try:
            circuito.registrar_expediente(
                presentacion_id, request.POST.get("expediente", ""), request.user
            )
            messages.success(request, "Número de expediente registrado.")
        except circuito.TransicionInvalida as e:
            messages.error(request, str(e))
        return _volver(request, presentacion_id)


class ComprobanteView(SeccionPermitidaMixin, LoginRequiredMixin, TemplateView):
    """El comprobante de presentación: constancia de la entrega."""

    seccion = "resultado"

    template_name = "runac/comprobante.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        presentacion_id = int(kwargs["presentacion_id"])
        alcance.exigir_presentacion(self.request.user, presentacion_id)
        ctx["comprobante"] = circuito.comprobante(presentacion_id)
        return ctx


class RevisionView(SeccionPermitidaMixin, LoginRequiredMixin, TemplateView):
    """Bandeja del revisor técnico nacional: qué presentó cada jurisdicción."""

    seccion = "revision"
    template_name = "runac/revision.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        periodo = self.request.GET.get("periodo") or "2026_T1"
        filas = circuito.presentaciones_del_periodo(periodo)

        for f in filas:
            f["estado_legible"] = circuito.estado_legible(f["estado"])
            f["color"] = circuito.ESTADOS.get(f["estado"], ("", "", "secondary"))[2]
            f["acciones"] = circuito.acciones_disponibles(f, self.request.user)

        ctx.update(
            {
                "presentaciones": filas,
                "periodo_elegido": periodo,
                "periodos": svc.periodos(),
                "es_revisor": puede_revisar(self.request.user),
                "es_nacional": es_nacional(self.request.user),
            }
        )
        return ctx


class PlanillaDeErroresView(SeccionPermitidaMixin, LoginRequiredMixin, View):
    """Descarga un Excel con los errores, una hoja por cada hoja del archivo."""

    seccion = "resultado"

    def get(self, request, importacion_id):
        alcance.exigir_importacion(request.user, importacion_id)
        contenido = informes.planilla_de_errores(importacion_id)
        if not contenido:
            raise Http404("No existe esa importación.")
        return _descarga(contenido, f"errores_importacion_{importacion_id}.xlsx")


class ArchivoMarcadoView(SeccionPermitidaMixin, LoginRequiredMixin, View):
    """Descarga el archivo que subió el operador, con las celdas marcadas.

    Es la salida que sirve para corregir: se abre, se ve qué está mal y dónde,
    se corrige y se vuelve a importar.
    """

    seccion = "resultado"

    def get(self, request, importacion_id):
        alcance.exigir_importacion(request.user, importacion_id)
        contenido, nombre = informes.archivo_marcado(importacion_id)
        if not contenido:
            messages.warning(
                request,
                "No se conserva el archivo original de esa importación, así que no "
                "se puede devolver marcado. Está disponible la planilla de errores.",
            )
            return redirect(reverse("runac:detalle", args=[importacion_id]))
        return _descarga(contenido, nombre)


def _descarga(contenido: bytes, nombre: str) -> HttpResponse:
    respuesta = HttpResponse(
        contenido,
        content_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
    )
    respuesta["Content-Disposition"] = f'attachment; filename="{nombre}"'
    return respuesta


class EstadoDelPeriodoView(SeccionPermitidaMixin, LoginRequiredMixin, View):
    """Abre o cierra el período. Es la ventana de presentación.

    Mientras el período no está abierto no se recibe ningún archivo, y una vez
    cerrado tampoco. Lo decide el nivel nacional para todas las jurisdicciones,
    no cada provincia para la suya.
    """

    seccion = "inicio"

    def post(self, request):
        codigo = request.POST.get("periodo") or "2026_T1"
        try:
            estado = circuito.cambiar_estado_del_periodo(
                codigo, request.POST.get("estado") or "", request.user
            )
        except circuito.TransicionInvalida as error:
            messages.error(request, str(error))
        else:
            messages.success(request, f"El período {codigo} quedó en «{estado}».")
            if estado == "PREPARACION":
                cargadas = circuito.volver_atras_es_provisorio(codigo)
                aviso = (
                    "Volver a preparación es una herramienta de prueba: en el "
                    "sistema real, con el período abierto la definición no se toca."
                )
                if cargadas:
                    aviso += (
                        f" Y este período ya tiene {cargadas} importaciones: lo que "
                        "cambies ahora no es contra lo que esas provincias presentaron."
                    )
                messages.warning(request, aviso)
        return redirect(f'{reverse("runac:inicio")}?periodo={codigo}')


class ArmarDemoView(SeccionPermitidaMixin, LoginRequiredMixin, View):
    """Deja una presentación completa para mostrar. La contraparte de borrar.

    **Herramienta de prueba, no parte del sistema.** Va junto al botón de
    borrar porque son un par: una limpia para volver a probar y la otra deja
    algo que mostrar. Sin las dos, limpiar antes de una demostración es un
    viaje de ida.
    """

    seccion = "inicio"

    def post(self, request):
        if not puede_administrar(request.user):
            messages.error(
                request, "Sólo el administrador puede armar la demostración."
            )
            return redirect("runac:inicio")

        resumen = demo_service.armar()
        if resumen["rechazados"]:
            for codigo, motivo in resumen["rechazados"]:
                messages.error(request, f"{codigo}: {motivo}")
        messages.success(
            request,
            f'Demostración armada: {len(resumen["importados"])} archivos importados '
            f'y {resumen["correcciones"]} correcciones registradas, sobre '
            f"{demo_service.JURISDICCION}. Es una función de prueba.",
        )
        return redirect(
            f'{reverse("runac:inicio")}?jurisdiccion={demo_service.JURISDICCION}'
        )


class BorrarImportacionesView(SeccionPermitidaMixin, LoginRequiredMixin, View):
    """Deja el sistema sin ninguna importación.

    **Herramienta de prueba, no parte del sistema.** Existe porque durante las
    pruebas hay que repetir el mismo circuito muchas veces: importar un archivo
    que anduvo, cambiarle algo y ver si falla.

    Sólo la ve el administrador: si estuviera al alcance del operador, alguien
    la toca durante una demostración. Va arriba de todo en el inicio, junto al
    selector de jurisdicción, porque son las dos herramientas de prueba y
    conviene buscarlas en el mismo lugar.
    """

    seccion = "inicio"

    def post(self, request):
        if not puede_administrar(request.user):
            messages.error(
                request, "Sólo el administrador puede borrar las importaciones."
            )
            return redirect("runac:inicio")

        borrados = circuito.borrar_todas_las_importaciones()
        messages.warning(
            request,
            "Se borraron todas las importaciones de todas las jurisdicciones: "
            f'{borrados["presentaciones"]} presentaciones, '
            f'{borrados["importaciones"]} importaciones y '
            f'{borrados["filas"]} registros.'
            + (" El período se reabrió." if borrados["periodos"] else "")
            + " Es una función de prueba.",
        )
        return redirect("runac:inicio")
