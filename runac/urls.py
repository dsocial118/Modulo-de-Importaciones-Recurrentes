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
    path(
        "plantillas/<str:codigo>/<str:periodo>/",
        views.descargar_plantilla,
        name="descargar_plantilla",
    ),
    path("cargar/", views.CargarView.as_view(), name="cargar"),
    path(
        "cargar/<str:codigo>/", views.CargarArchivoView.as_view(), name="cargar_archivo"
    ),
    path("resultado/", views.ResultadoView.as_view(), name="resultado"),
    path(
        "resultado/<int:importacion_id>/", views.DetalleView.as_view(), name="detalle"
    ),
    # Circuito: cierre de carga, revisión, observaciones y presentación.
    # Las rutas con nombre propio van ANTES que la genérica de acción, que si no
    # se las come.
    path("revision/", views.RevisionView.as_view(), name="revision"),
    path(
        "presentacion/<int:presentacion_id>/observar/",
        views.ObservarView.as_view(),
        name="observar",
    ),
    path(
        "presentacion/<int:presentacion_id>/expediente/",
        views.ExpedienteView.as_view(),
        name="expediente",
    ),
    path(
        "presentacion/<int:presentacion_id>/comprobante/",
        views.ComprobanteView.as_view(),
        name="comprobante",
    ),
    path(
        "presentacion/<int:presentacion_id>/<str:accion>/",
        views.AccionView.as_view(),
        name="accion",
    ),
    path(
        "observacion/<int:observacion_id>/responder/",
        views.ResponderView.as_view(),
        name="responder",
    ),
    # Edición de datos: el paso 5 del circuito, para las advertencias.
    path(
        "resultado/<int:importacion_id>/datos/",
        views.EdicionView.as_view(),
        name="edicion",
    ),
    path(
        "resultado/<int:importacion_id>/datos/editar/",
        views.EditarCampoView.as_view(),
        name="editar_campo",
    ),
    # Informes de errores: lo que el operador se lleva para corregir el Excel.
    path(
        "resultado/<int:importacion_id>/errores.xlsx",
        views.PlanillaDeErroresView.as_view(),
        name="planilla_errores",
    ),
    path(
        "resultado/<int:importacion_id>/marcado.xlsx",
        views.ArchivoMarcadoView.as_view(),
        name="archivo_marcado",
    ),
    path("reglas/", views.ReglasView.as_view(), name="estructura"),
    path(
        "periodo/estado/",
        views.EstadoDelPeriodoView.as_view(),
        name="estado_del_periodo",
    ),
    # Herramienta de prueba: no forma parte del sistema.
    path(
        "pruebas/borrar-importaciones/",
        views.BorrarImportacionesView.as_view(),
        name="borrar_importaciones",
    ),
]
