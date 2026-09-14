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

CAMPO_CON_AVISO = "Pueblo originario (especificar)"

# Dos formas distintas de resolver la misma advertencia: completar el dato que
# faltaba, y corregir el campo que lo exigía. El historial muestra las dos.
CORRECCIONES = [
    (CAMPO_CON_AVISO, "Qom", "Lo informó la provincia por nota"),
    (CAMPO_CON_AVISO, "Mapuche", "Se verificó contra el expediente"),
    (
        "¿Se identifica con algún pueblo originario?",
        "No",
        "Estaba mal cargado: no se identifica con ningún pueblo",
    ),
]


def armar(borrar_antes: bool = True) -> dict:
    """Deja la presentación de Chubut completa y lista para mostrar.

    Devuelve un resumen de lo que hizo, para que quien la llame lo informe:
    la consola lo imprime y la pantalla lo muestra como aviso.
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
    campos = {c["titulo_esperado"]: c for c in edicion.campos_de_la_hoja(hoja["id"])}

    # Las filas se eligen de las que efectivamente tienen la advertencia, y
    # distintas entre sí: dos correcciones sobre la misma fila se leen como una
    # corrección de una corrección, que no es lo que se quiere mostrar.
    with connection.cursor() as cur:
        cur.execute(
            """SELECT DISTINCT numero_fila FROM runac_c2_reglas_incumplidas
                WHERE importacion_id = %s AND resuelta = 0 AND nombre_campo = %s
                ORDER BY numero_fila""",
            [importacion, CAMPO_CON_AVISO],
        )
        filas = [f[0] for f in cur.fetchall()]

    hechas = 0
    for numero, (titulo, valor, motivo) in zip(filas, CORRECCIONES):
        campo = campos.get(titulo)
        if not campo:
            continue
        edicion.editar(
            importacion, hoja["id"], numero, campo["nombre"], valor, "operador", motivo
        )
        hechas += 1
    return hechas
