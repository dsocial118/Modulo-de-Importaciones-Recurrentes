"""Datos que todas las pantallas necesitan tener a mano."""

from django.conf import settings

from runac.permissions import es_nacional, jurisdiccion_de, menu_de, nombre_del_rol


def datos_de_sesion(request):
    usuario = getattr(request, "user", None)
    autenticado = bool(usuario and usuario.is_authenticated)
    return {
        "es_prototipo": settings.RUNAC_ES_PROTOTIPO,
        "aviso_prototipo": settings.RUNAC_AVISO_PROTOTIPO,
        # El rol define qué puede hacer; la jurisdicción, sobre qué datos.
        "rol": nombre_del_rol(usuario) if autenticado else None,
        # Sólo la de quien pertenece a una: el nivel nacional no es de ninguna,
        # y el selector ya indica sobre cuál se está trabajando.
        "jurisdiccion": (
            jurisdiccion_de(usuario)
            if autenticado and not es_nacional(usuario)
            else None
        ),
        "es_nacional": es_nacional(usuario) if autenticado else False,
        # Cada rol ve sólo las secciones que le corresponden.
        "menu": menu_de(usuario) if autenticado else [],
    }
