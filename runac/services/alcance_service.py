"""De quién es cada cosa, y si este usuario la puede tocar.

El rol dice qué puede hacer una persona; la jurisdicción, **sobre qué datos**.
Un usuario provincial trabaja sólo sobre la suya; el nivel nacional, sobre
todas.

Hasta el 25-09-2026 las pantallas controlaban el rol pero no la jurisdicción:
un operador de Chubut que escribía la dirección a mano veía el detalle, bajaba
los errores y veía los datos de una importación de Chaco, y un responsable
podía cerrar la carga de otra provincia. Es el hallazgo #10 de la auditoría,
ampliado.

Para quien no es de esa jurisdicción, lo ajeno **no existe**: 404, no 403,
para no confirmar que el número corresponde a algo.
"""

from django.db import connection
from django.http import Http404

from runac.permissions import es_nacional, jurisdiccion_de


def es_suya(usuario, jurisdiccion: str | None) -> bool:
    """El nivel nacional ve todas; el provincial, sólo la propia."""
    if jurisdiccion is None:
        return False
    return es_nacional(usuario) or jurisdiccion == jurisdiccion_de(usuario)


def _una(sql: str, parametros: list):
    with connection.cursor() as cur:
        cur.execute(sql, parametros)
        fila = cur.fetchone()
    return fila[0] if fila else None


def jurisdiccion_de_la_presentacion(presentacion_id: int) -> str | None:
    return _una(
        """SELECT j.nombre FROM mir_c2_presentacion s
             JOIN mir_c2_jurisdiccion j ON j.id = s.jurisdiccion_id
            WHERE s.id = %s""",
        [presentacion_id],
    )


def jurisdiccion_de_la_importacion(importacion_id: int) -> str | None:
    return _una(
        """SELECT j.nombre FROM mir_c2_importacion i
             JOIN mir_c2_presentacion s ON s.id = i.presentacion_id
             JOIN mir_c2_jurisdiccion j ON j.id = s.jurisdiccion_id
            WHERE i.id = %s""",
        [importacion_id],
    )


def presentacion_de_la_observacion(observacion_id: int) -> int | None:
    return _una(
        "SELECT presentacion_id FROM mir_c2_observacion WHERE id = %s",
        [observacion_id],
    )


def exigir_presentacion(usuario, presentacion_id: int) -> str:
    """La jurisdicción de la presentación, o 404 si no es de este usuario."""
    jurisdiccion = jurisdiccion_de_la_presentacion(presentacion_id)
    if not es_suya(usuario, jurisdiccion):
        raise Http404("No existe esa presentación.")
    return jurisdiccion


def exigir_importacion(usuario, importacion_id: int) -> str:
    jurisdiccion = jurisdiccion_de_la_importacion(importacion_id)
    if not es_suya(usuario, jurisdiccion):
        raise Http404("No existe esa importación.")
    return jurisdiccion


def exigir_observacion(usuario, observacion_id: int) -> int:
    """La presentación de la observación, o 404 si no es de este usuario."""
    presentacion_id = presentacion_de_la_observacion(observacion_id)
    if presentacion_id is None:
        raise Http404("No existe esa observación.")
    exigir_presentacion(usuario, presentacion_id)
    return presentacion_id
