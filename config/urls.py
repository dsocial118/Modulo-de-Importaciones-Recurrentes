from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView

from runac.views.front_v2 import reenviar


def salud(_request):
    """Para el chequeo del compose: responde si Django atiende, sin tocar la base."""
    return HttpResponse("ok", content_type="text/plain")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("salud/", salud),
    # Front v2 (React): la API y el reenvío al servicio que sirve cada front.
    path("api/mir/", include("runac.api_urls")),
    path("api/esquema/", SpectacularAPIView.as_view(), name="esquema"),
    path("v2/<str:modulo>/", reenviar),
    path("v2/<str:modulo>/<path:ruta>", reenviar),
    path("", include("runac.urls")),
]
