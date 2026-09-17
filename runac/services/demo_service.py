"""Arma la presentación de demostración. Herramienta de prueba, no es el sistema.

Es la contraparte de `borrar_todas_las_importaciones`: una deja el sistema
vacío para volver a probar, la otra lo deja con una presentación completa para
mostrar. Sin las dos, limpiar antes de una demostración es un viaje de ida.

Vive en un servicio y no en el comando de consola porque lo usan los dos: el
comando `manage.py armar_demo` y el botón del inicio. Al integrar a SISOC se va
con el resto de las herramientas de prueba.
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

# Los CINCO archivos van con la variante que trae advertencias.
#
# Antes sólo el MPI las traía y los otros cuatro entraban perfectos: la
# presentación quedaba con una sola pantalla que mostrara algo, y las
# advertencias que había eran todas del mismo tipo. Una presentación real no se
# parece a eso —los problemas aparecen repartidos y de distinta clase—, y esta
# demostración se usa justamente para mostrar cómo se ve una importación de
# verdad.
#
# Los cinco entran igual: una advertencia observa, no rechaza. Que el archivo
# entre CON problemas anotados es lo que hay que poder mostrar.
PLAN = [
    ("DISP_PENAL", "DISP_PENAL_2026_T1_Chubut_CON_ADVERTENCIAS.xlsx"),
    ("DISP_SCP", "DISP_SCP_2026_T1_Chubut_CON_ADVERTENCIAS.xlsx"),
    ("MPI", "MPI_2026_T1_Chubut_CON_ADVERTENCIAS.xlsx"),
    ("MPE", "MPE_2026_T1_Chubut_CON_ADVERTENCIAS.xlsx"),
    ("MPJ_DAE", "MPJ_DAE_2026_T1_Chubut_CON_ADVERTENCIAS.xlsx"),
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
    ("MPI", "edad", "15", "Se verificó contra la fecha de nacimiento"),
    (
        "MPI",
        "fecha_del_relevamiento",
        "02/03/2026",
        "Estaba cargada con una fecha futura",
    ),
    ("MPI", "tipo_de_discapacidad", "Motora", "Lo informó el dispositivo"),
    ("MPI", "pueblo_originario_especificar", "Qom", "Lo informó la provincia por nota"),
    # Del archivo de dispositivos, para que el historial no sea de un archivo
    # solo: la corrección de una dotación absurda es el caso más fácil de contar.
    (
        "DISP_PENAL",
        "cantidad_de_agentes_equipo_tecnico_y_profesional_incluye_efd962",
        "24",
        "Se había informado la dotación de toda la provincia",
    ),
    (
        "DISP_PENAL",
        "cantidad_agentes_de_salud",
        "6",
        "Corregido con el parte del dispositivo",
    ),
    (
        "MPE",
        "fecha_de_inicio_mpe",
        "02/03/2026",
        "La fecha estaba adelantada un año",
    ),
]

# Suficientes para que el historial tenga contenido, y no tantas como para que
# no quede nada que mostrar corrigiendo en vivo.
A_CORREGIR = 5


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


def _importacion_de(codigo: str):
    """La última importación válida de ese archivo."""
    with connection.cursor() as cur:
        cur.execute(
            """SELECT i.id FROM mir_c2_importacion i
                 JOIN mir_c1_archivo a ON a.id = i.archivo_id
                WHERE a.codigo = %s AND i.estado = 'VALIDA'
                ORDER BY i.id DESC LIMIT 1""",
            [codigo],
        )
        fila = cur.fetchone()
    return fila[0] if fila else None


def _corregir() -> int:
    """Deja hechas unas correcciones, para que el historial no esté vacío.

    Recorre varios archivos, no uno: con los cinco trayendo advertencias, un
    historial armado sobre el MPI solo deja la impresión de que la corrección
    dentro del sistema sirve para las nóminas y no para los dispositivos.
    """
    hechas = 0
    for codigo, nombre, valor, motivo in CORRECCIONES:
        if hechas >= A_CORREGIR:
            break
        importacion = _importacion_de(codigo)
        if importacion is None:
            continue
        contexto = edicion.contexto_de(importacion)
        # El campo puede estar en cualquiera de las hojas del archivo: los
        # dispositivos penales tienen cinco.
        objetivo = None
        for hoja in contexto["hojas"]:
            campos = {c["nombre"]: c for c in edicion.campos_de_la_hoja(hoja["id"])}
            campo = campos.get(nombre)
            if not campo:
                continue
            numero = _fila_con_aviso(importacion, hoja, campo)
            if numero is not None:
                objetivo = (hoja, numero)
                break
        if objetivo is None:
            continue
        hoja, numero = objetivo
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
            """SELECT MIN(numero_fila) FROM mir_c2_reglas_incumplidas
                WHERE importacion_id = %s AND nombre_hoja = %s
                  AND nombre_campo = %s AND resuelta = 0""",
            [importacion, hoja["nombre_esperado"], campo["titulo_esperado"]],
        )
        fila = cur.fetchone()
    return fila[0] if fila else None
