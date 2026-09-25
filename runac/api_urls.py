"""Rutas de la API del front v2, bajo `/api/mir/`."""

from django.urls import path

from runac import api_views

app_name = "api_mir"

urlpatterns = [
    path("sesion/", api_views.SesionView.as_view(), name="sesion"),
    path("inicio/", api_views.InicioView.as_view(), name="inicio"),
]
