"""Reenvío de `/v2/<modulo>/` al servicio que sirve ese front.

Es la regla de SISOC para el front nuevo (`docs/implementaciones/frontend_v2.md`
§6): **todo entra por Django**, y Django reenvía. Así el front nuevo pasa por
el mismo login y el mismo middleware que el resto, y no hace falta tocar el
servidor web de adelante.

Reglas, las mismas que SISOC:

  - Los módulos y sus destinos salen de `settings.FRONTS_V2`, nunca del
    pedido. Un módulo desconocido da 404.
  - Sólo GET y HEAD. No se reenvían ni la galleta de sesión ni la
    autorización: el front es estático y no las necesita.
  - Exige sesión: sin sesión, al login actual con `next`.
  - Timeout corto: si el front está caído, 503 para esa ruta y el resto sigue.
  - Sin lógica: no transforma ni inyecta nada.
"""

import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.views.decorators.http import require_http_methods

# Lo que se devuelve tal cual viene del front. El resto de las cabeceras de la
# respuesta, no: las pone Django.
CABECERAS_QUE_PASAN = ("Content-Type", "ETag", "Last-Modified")


@login_required
@require_http_methods(["GET", "HEAD"])
def reenviar(request, modulo: str, ruta: str = ""):
    destino = settings.FRONTS_V2.get(modulo)
    if not destino:
        raise Http404("No hay front v2 para ese módulo.")

    url = f"{destino.rstrip('/')}/v2/{modulo}/{ruta}"
    try:
        respuesta = requests.request(
            request.method,
            url,
            params=request.GET,
            headers={"Accept": request.headers.get("Accept", "*/*")},
            timeout=settings.FRONTS_V2_TIMEOUT,
        )
    except requests.RequestException:
        return HttpResponse(
            "El front nuevo no responde. La versión actual sigue disponible.",
            status=503,
            content_type="text/plain; charset=utf-8",
        )

    salida = HttpResponse(respuesta.content, status=respuesta.status_code)
    for cabecera in CABECERAS_QUE_PASAN:
        if cabecera in respuesta.headers:
            salida[cabecera] = respuesta.headers[cabecera]

    # Los archivos con huella en el nombre no cambian nunca: se guardan un año.
    # La página de entrada, en cambio, se pide siempre, para que un despliegue
    # nuevo se vea sin vaciar la caché.
    if ruta.startswith("assets/"):
        salida["Cache-Control"] = "public, max-age=31536000, immutable"
    else:
        salida["Cache-Control"] = "no-cache"
    return salida
