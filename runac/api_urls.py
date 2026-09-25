"""Rutas de la API del front v2, bajo `/api/mir/`."""

from django.urls import path

from runac import api_views as v

app_name = "api_mir"

urlpatterns = [
    path("sesion/", v.SesionView.as_view(), name="sesion"),
    path("inicio/", v.InicioView.as_view(), name="inicio"),
    path(
        "periodos/<str:codigo>/estado/",
        v.EstadoDelPeriodoView.as_view(),
        name="estado_del_periodo",
    ),
    # Plantillas
    path("plantillas/", v.PlantillasView.as_view(), name="plantillas"),
    path(
        "plantillas/<str:periodo>/todas/",
        v.PlantillasTodasView.as_view(),
        name="plantillas_todas",
    ),
    path(
        "plantillas/<str:periodo>/<str:codigo>/",
        v.PlantillaView.as_view(),
        name="plantilla",
    ),
    # Carga
    path("carga/", v.CargaView.as_view(), name="carga"),
    path("carga/<str:codigo>/", v.CargarArchivoView.as_view(), name="cargar_archivo"),
    # Resultado y circuito
    path("resultado/", v.ResultadoView.as_view(), name="resultado"),
    path("revision/", v.RevisionView.as_view(), name="revision"),
    path(
        "presentaciones/<int:presentacion_id>/observaciones/",
        v.ObservarView.as_view(),
        name="observar",
    ),
    path(
        "presentaciones/<int:presentacion_id>/expediente/",
        v.ExpedienteView.as_view(),
        name="expediente",
    ),
    path(
        "presentaciones/<int:presentacion_id>/comprobante/",
        v.ComprobanteView.as_view(),
        name="comprobante",
    ),
    path(
        "presentaciones/<int:presentacion_id>/acciones/<str:accion>/",
        v.AccionView.as_view(),
        name="accion",
    ),
    path(
        "observaciones/<int:observacion_id>/respuesta/",
        v.ResponderView.as_view(),
        name="responder",
    ),
    # Una importación
    path(
        "importaciones/<int:importacion_id>/", v.DetalleView.as_view(), name="detalle"
    ),
    path(
        "importaciones/<int:importacion_id>/hallazgos/",
        v.HallazgosView.as_view(),
        name="hallazgos",
    ),
    path(
        "importaciones/<int:importacion_id>/errores.xlsx",
        v.ErroresXlsxView.as_view(),
        name="errores_xlsx",
    ),
    path(
        "importaciones/<int:importacion_id>/marcado.xlsx",
        v.MarcadoXlsxView.as_view(),
        name="marcado_xlsx",
    ),
    path(
        "importaciones/<int:importacion_id>/datos/", v.DatosView.as_view(), name="datos"
    ),
    # Reglas
    path("reglas/", v.ReglasView.as_view(), name="reglas"),
    # Herramientas de prueba: no forman parte del sistema.
    path("pruebas/armar-demo/", v.ArmarDemoView.as_view(), name="armar_demo"),
    path(
        "pruebas/borrar-importaciones/",
        v.BorrarImportacionesView.as_view(),
        name="borrar_importaciones",
    ),
]
