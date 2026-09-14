"""Arma la presentación de demostración. Herramienta de prueba, no es el sistema.

Es la contraparte de `borrar_todas_las_importaciones`: una deja el prototipo
vacío para volver a probar, la otra lo deja con una presentación completa para
mostrar. Sin las dos, limpiar antes de una demostración es un viaje de ida.

Vive en un servicio y no en el comando de consola porque lo usan los dos: el
comando `manage.py armar_demo` y el botón del inicio. Al integrar a SISOC se va
con el resto del prototipo.
"""

from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection

from runac.services import circuito_service as circuito
from runac.services import edicion_service as edicion
from runac.services import importacion_service as svc

ARCHIVOS = Path(__file__).resolve().parent.parent / "demo"
JURISDICCION = "Chubut"
PERIODO = "2026_T1"

# El MPI va con la variante que trae advertencias, a propósito: un archivo
# perfecto no permite mostrar la corrección dentro del sistema, que es la mitad
# interesante del circuito.
PLAN = [
    ("DISP_PENAL", "DISP_PENAL_2026_T1_Chubut.xlsx"),
    ("DISP_SCP", "DISP_SCP_2026_T1_Chubut.xlsx"),
    ("MPI", "MPI_2026_T1_Chubut_CON_ADVERTENCIAS.xlsx"),
    ("MPE", "MPE_2026_T1_Chubut.xlsx"),
    ("MPJ_DAE", "MPJ_DAE_2026_T1_Chubut.xlsx"),
]

# Cómo se corrige cada tipo de advertencia sembrada. Se toma la primera fila que
# la tenga sin resolver y se la arregla.
#
# Antes esto apuntaba a UN campo fijo. El día que el generador dejó de sembrar
# esa advertencia en particular —la condición que la dispara se sortea— la demo
# quedó con el historial vacío y no se notó hasta mirarlo. Ahora depende de lo
# que el archivo efectivamente trajo, y con una lista más larga que las que se
# van a usar.
CORRECCIONES = [
    ("edad", "15", "Se verificó contra la fecha de nacimiento"),
    ("fecha_del_relevamiento", "02/03/2026", "Estaba cargada con una fecha futura"),
    ("pueblo_originario_especificar", "Qom", "Lo informó la provincia por nota"),
    ("tipo_de_discapacidad", "Motora", "Se completó con lo que informó el dispositivo"),
]

# Suficientes para que el historial tenga contenido, y no tantas como para que
# no quede nada que mostrar corrigiendo en vivo.
A_CORREGIR = 3


def armar(borrar_antes: bool = True) -> dict:
    """Deja la presentación de Chubut completa y lista para mostrar.

    Devuelve un resumen de lo que hizo, para que quien la llame lo informe: la
    consola lo imprime y la pantalla lo muestra como aviso.
    """
    resumen = {"borrado": None, "importados": [], "rechazados": [], "correcciones": 0}

    if borrar_antes:
        resumen["borrado"] = circuito.borrar_todas_las_importaciones()

    for codigo, nombre in PLAN:
        ruta = ARCHIVOS / nombre
        if not ruta.exists():
            raise FileNotFoundError(f"Falta el archivo de demostración: {ruta}")
        with open(ruta, "rb") as fh:
            subido = SimpleUploadedFile(nombre, fh.read())
        resultado = svc.importar_uno(codigo, subido, JURISDICCION, PERIODO, "operador")
        if resultado.get("rechazado"):
            resumen["rechazados"].append((codigo, resultado["mensaje"]))
        else:
            resumen["importados"].append(codigo)

    resumen["correcciones"] = _corregir()
    resumen["estado"] = svc.estado_de_la_presentacion(JURISDICCION, PERIODO)
    return resumen


def _corregir() -> int:
    """Deja hechas unas correcciones, para que el historial no esté vacío."""
    with connection.cursor() as cur:
        cur.execute(
            """SELECT i.id FROM runac_c2_importacion i
                 JOIN runac_c1_archivo a ON a.id = i.archivo_id
                WHERE a.codigo = 'MPI' AND i.estado = 'VALIDA'
                ORDER BY i.id DESC LIMIT 1"""
        )
        fila = cur.fetchone()
    if not fila:
        return 0

    importacion = fila[0]
    contexto = edicion.contexto_de(importacion)
    hoja = contexto["hojas"][0]
    campos = {c["nombre"]: c for c in edicion.campos_de_la_hoja(hoja["id"])}

    hechas = 0
    for nombre, valor, motivo in CORRECCIONES:
        if hechas >= A_CORREGIR:
            break
        campo = campos.get(nombre)
        if not campo:
            continue
        numero = _fila_con_aviso(importacion, hoja, campo)
        if numero is None:
            continue
        try:
            edicion.editar(
                importacion, hoja["id"], numero, nombre, valor, "operador", motivo
            )
        except edicion.EdicionNoPermitida:
            # Una corrección que el sistema no acepta —un valor que quedó fuera
            # del catálogo, por ejemplo— se saltea. Dejar la demo a medio armar
            # por un dato de ejemplo mal elegido es peor que tener una
            # corrección menos en el historial.
            continue
        hechas += 1
    return hechas


def _fila_con_aviso(importacion: int, hoja: dict, campo: dict):
    """La primera fila con una advertencia sin resolver en ese campo."""
    with connection.cursor() as cur:
        cur.execute(
            """SELECT MIN(numero_fila) FROM runac_c2_reglas_incumplidas
                WHERE importacion_id = %s AND nombre_hoja = %s
                  AND nombre_campo = %s AND resuelta = 0""",
            [importacion, hoja["nombre_esperado"], campo["titulo_esperado"]],
        )
        fila = cur.fetchone()
    return fila[0] if fila else None
