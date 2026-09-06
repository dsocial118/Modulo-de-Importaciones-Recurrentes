"""Datos que todas las pantallas necesitan tener a mano."""

from django.conf import settings


def datos_de_sesion(request):
    return {
        "es_prototipo": settings.RUNAC_ES_PROTOTIPO,
        "aviso_prototipo": settings.RUNAC_AVISO_PROTOTIPO,
    }
