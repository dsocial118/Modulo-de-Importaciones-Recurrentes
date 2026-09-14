"""Datos que todas las pantallas necesitan tener a mano."""

from django.conf import settings

from runac.permissions import es_nacional, jurisdiccion_de, menu_de, nombre_del_rol


def _jurisdiccion_en_curso(request, usuario) -> str:
    """Sobre qué jurisdicción se está trabajando, en cualquier pantalla.

    La elección vive en la sesión: la escribe el selector, y acá sólo se lee.
    Si nunca se eligió ninguna, la del usuario.

    Al integrar a SISOC esto desaparece —el alcance territorial lo resuelve el
    sistema y no se elige nada—, pero mientras exista tiene que ser una sola
    para todas las pantallas.
    """
    elegida = getattr(request, "session", {}).get("jurisdiccion")
    return elegida or jurisdiccion_de(usuario)


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
        #
        # Se lee de la sesión, que es donde el selector deja la elegida. Antes
        # salía siempre del usuario, así que el encabezado decía una cosa en
        # Reglas y Plantillas —la jurisdicción del usuario— y otra en Inicio y
        # Cargar, que sí respetan la elección. La misma pantalla, dos respuestas.
        "jurisdiccion": (
            _jurisdiccion_en_curso(request, usuario)
            if autenticado and not es_nacional(usuario)
            else None
        ),
        "es_nacional": es_nacional(usuario) if autenticado else False,
        # Cada rol ve sólo las secciones que le corresponden.
        "menu": menu_de(usuario) if autenticado else [],
    }
