"""La plantilla se genera cuando se la baja, no antes.

Hasta el 22-09-2026 las plantillas eran archivos en disco, generados una vez y
servidos tal cual. Eso produce una clase entera de error: se corrige la Capa 1 y
la provincia sigue bajando la planilla vieja, sin que nada avise. Pasó, y costó
caro: la plantilla del MPE tenía 41 columnas —generada desde la versión anterior
del archivo— cuando la definición vigente tenía 31. Quien la bajaba veía adentro
del MPE los datos del chico, que ya se habían mudado al legajo.

Generarla tarda menos de un segundo, así que se genera al pedirla. No hay copia
en disco que pueda quedar vieja, no hay paso que alguien tenga que acordarse de
correr, y no hace falta detectar qué cambió: si la definición cambió, la
plantilla ya salió distinta.

Es el pendiente #64, y saca del medio la mitad del #49.
"""

from __future__ import annotations

import os
import sys
import tempfile

from django.db import connection

# El generador está pensado para correr también fuera de Django, así que se
# importa por ruta, igual que el importador.
_MOTOR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "services", "motor")
if _MOTOR not in sys.path:
    sys.path.insert(0, _MOTOR)

import plantilla as motor_plantilla  # noqa: E402  # pylint: disable=wrong-import-position


class _CursorConNombres:
    """El cursor de Django devuelve tuplas y el generador espera diccionarios.

    Es un adaptador de seis líneas: preferible a que el generador sepa de Django,
    porque tiene que poder correrse también desde la línea de comandos.
    """

    def __init__(self, cursor):
        self._cursor = cursor

    def execute(self, sql, params=None):
        return self._cursor.execute(sql, params or ())

    def _nombres(self):
        return [c[0] for c in self._cursor.description]

    def fetchall(self):
        nombres = self._nombres()
        return [dict(zip(nombres, fila)) for fila in self._cursor.fetchall()]

    def fetchone(self):
        nombres = self._nombres()
        fila = self._cursor.fetchone()
        return dict(zip(nombres, fila)) if fila else None


def generar(codigo: str, periodo: str, filas_vacias: int = 200) -> str:
    """Arma la plantilla de ese archivo y devuelve la ruta del .xlsx.

    Queda en una carpeta temporal: la borra quien la sirvió, después de mandarla.
    """
    carpeta = tempfile.mkdtemp(prefix="plantilla_")
    with connection.cursor() as cursor:
        return motor_plantilla.generar(
            _CursorConNombres(cursor), codigo, carpeta, filas_vacias, periodo
        )


def nombre_de_archivo(codigo: str, periodo: str) -> str:
    return f"{codigo}_{periodo}_MODELO.xlsx"
