"""Entrada al prototipo y pantalla de inicio."""

from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.views.generic import TemplateView

from runac.services import importacion_service as svc
from runac.permissions import (
    SeccionPermitidaMixin,
    menu_de,
    puede_administrar,
    rol_de,
)
from runac.views.carga import JURISDICCIONES, jurisdiccion_en_curso


class EntrarView(LoginView):
    template_name = "runac/entrar.html"
    redirect_authenticated_user = True


def salir(request):
    logout(request)
    return redirect("runac:entrar")


class InicioView(SeccionPermitidaMixin, LoginRequiredMixin, TemplateView):
    """Punto de partida: elegir período y ver cómo viene la presentación."""

    seccion = "inicio"
    template_name = "runac/inicio.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["accesos"] = accesos_de(self.request.user)
        periodos = svc.periodos()
        elegido = self.request.GET.get("periodo") or (
            periodos[0]["codigo"] if periodos else None
        )

        ctx["periodos"] = periodos
        ctx["periodo_elegido"] = elegido
        ctx["periodo"] = svc.periodo(elegido) if elegido else None
        ctx["rol"] = rol_de(self.request.user)
        ctx["jurisdiccion"] = jurisdiccion_en_curso(self.request)
        ctx["jurisdicciones"] = JURISDICCIONES
        ctx["puede_administrar"] = puede_administrar(self.request.user)

        if elegido and ctx["jurisdiccion"]:
            estado = svc.estado_de_la_presentacion(ctx["jurisdiccion"], elegido)
            ctx.update(estado)
            listos = [
                a
                for a in estado["archivos"]
                if a["estado"] != "SIN_CARGAR"
                and a["estado"] not in ("CON_ERRORES", "ESTRUCTURA_INVALIDA")
            ]
            ctx["cargados"] = len(listos)
            ctx["total_archivos"] = len(estado["archivos"])
            ctx["avance"] = (
                int(len(listos) * 100 / len(estado["archivos"]))
                if estado["archivos"]
                else 0
            )
        return ctx


# Qué hace cada sección, en una línea. Se muestra en los accesos del inicio.
DETALLE_DE_SECCION = {
    "plantillas": "Los Excel modelo del período, con las listas al día.",
    "cargar": "De a uno, indicando cuál es. El sistema controla el orden.",
    "resultado": "Qué entró, qué falta corregir, y el cierre de carga.",
    "revision": "Observaciones, habilitación y presentación del período.",
    "estructura": "Qué se espera en cada columna de cada archivo.",
}


def accesos_de(usuario) -> list[dict]:
    """Los accesos del inicio: el menú del rol, sin la propia pantalla."""
    return [
        {**seccion, "detalle": DETALLE_DE_SECCION.get(seccion["clave"], "")}
        for seccion in menu_de(usuario)
        if seccion["clave"] != "inicio"
    ]
