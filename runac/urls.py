from django.urls import path

from runac import views
from runac.views.plantillas import descargar_todas

app_name = "runac"

urlpatterns = [
    path("", views.InicioView.as_view(), name="inicio"),
    path("entrar/", views.EntrarView.as_view(), name="entrar"),
    path("salir/", views.salir, name="salir"),

    path("plantillas/", views.PlantillasView.as_view(), name="plantillas"),
    path("plantillas/<str:periodo>/todas/", descargar_todas, name="descargar_todas"),
    path("plantillas/<str:codigo>/<str:periodo>/", views.descargar_plantilla, name="descargar_plantilla"),

    path("cargar/", views.CargarView.as_view(), name="cargar"),
    path("cargar/procesar/", views.ProcesarView.as_view(), name="procesar"),
    path("resultado/", views.ResultadoView.as_view(), name="resultado"),
    path("resultado/<int:importacion_id>/", views.DetalleView.as_view(), name="detalle"),

    path("estructura/", views.EstructuraView.as_view(), name="estructura"),
    path("estructura/<str:codigo>/", views.CamposView.as_view(), name="campos"),
]
