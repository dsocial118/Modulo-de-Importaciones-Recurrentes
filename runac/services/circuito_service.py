"""Circuito de carga, revisión y presentación.

Implementa los nueve pasos del análisis funcional. Las transiciones de estado
viven acá y en ningún otro lado: las vistas piden acciones, no cambian estados.

    EN_CARGA --cerrar carga--> CERRADA --abrir revision--> EN_REVISION
        ^                                                       |
        |                                          +------------+------------+
        |                                          |                         |
   cerrar carga                                observar            sin observaciones
        |                                          |                         |
    SUBSANADA <--responder-- OBSERVADA <-----------+                    HABILITADA
                                                                             |
                                                                        presentar
                                                                             |
                                                    CONSOLIDADA <------- PRESENTADA

Reglas del documento funcional:

  - El nivel nacional NO modifica datos provinciales: solo observa.
  - El ciclo observacion-subsanacion no tiene limite de rondas.
  - La presentacion es el ultimo acto, y solo se habilita cuando el revisor
    tecnico nacional concluyo la revision.
  - Para volver a importar despues del cierre hay que reabrir la carga, de modo
    que el revisor no trabaje sobre datos que cambiaron abajo.
"""

from __future__ import annotations

import re

from django.db import connection

from runac.permissions import puede_administrar, puede_presentar, puede_revisar


# Que accion puede ejecutarse desde cada estado, y quien.
#   accion: (estados de origen, estado destino, quien puede)
ACCIONES = {
    "cerrar_carga": (("EN_CARGA", "SUBSANADA"), "CERRADA", "responsable"),
    "reabrir_carga": (("CERRADA", "OBSERVADA", "SUBSANADA"), "EN_CARGA", "responsable"),
    "abrir_revision": (("CERRADA",), "EN_REVISION", "revisor"),
    "habilitar": (("EN_REVISION", "CERRADA"), "HABILITADA", "revisor"),
    "devolver": (("EN_REVISION", "HABILITADA"), "OBSERVADA", "revisor"),
    "presentar": (("HABILITADA",), "PRESENTADA", "responsable"),
    "consolidar": (("PRESENTADA",), "CONSOLIDADA", "sistema"),
}

ETIQUETAS = {
    "cerrar_carga": "Cerrar la carga",
    "reabrir_carga": "Reabrir la carga",
    "abrir_revision": "Comenzar la revisión",
    "habilitar": "Habilitar la presentación",
    "devolver": "Devolver a la jurisdicción",
    "presentar": "Presentar el período",
    "consolidar": "Consolidar",
}

AYUDAS = {
    "cerrar_carga": "Declara terminada la carga del período y la envía a revisión nacional.",
    "reabrir_carga": "Vuelve la presentación a carga. Es lo que habilita a importar de nuevo un archivo.",
    "abrir_revision": "Toma la presentación para revisarla.",
    "habilitar": "Concluye la revisión y habilita a la jurisdicción a presentar formalmente.",
    "devolver": "Devuelve la presentación a la jurisdicción para que subsane.",
    "presentar": "Acto formal. Genera el comprobante para remitir por GDE.",
    "consolidar": "Incorpora los datos de la Capa 2 a la base consolidada.",
}

# Como se muestra cada estado y que significa, en el lenguaje del documento.
ESTADOS = {
    "EN_CARGA": (
        "En carga",
        "La jurisdicción está cargando y corrigiendo.",
        "secondary",
    ),
    "CERRADA": ("Carga cerrada", "Enviada a revisión nacional.", "info"),
    "EN_REVISION": (
        "En revisión",
        "El revisor técnico nacional la está revisando.",
        "info",
    ),
    "OBSERVADA": (
        "Observada",
        "Tiene observaciones y volvió a la jurisdicción.",
        "warning",
    ),
    "SUBSANADA": (
        "Subsanada",
        "Se respondieron las observaciones; falta cerrar la carga.",
        "warning",
    ),
    "HABILITADA": (
        "Habilitada para presentar",
        "La revisión concluyó sin observaciones pendientes.",
        "success",
    ),
    "PRESENTADA": (
        "Presentada",
        "Presentación formal realizada. Comprobante disponible.",
        "success",
    ),
    "CONSOLIDADA": (
        "Consolidada",
        "Los datos se incorporaron a la base consolidada.",
        "dark",
    ),
}


class TransicionInvalida(Exception):
    pass


def estado_legible(codigo: str) -> str:
    return ESTADOS.get(codigo, (codigo, "", "secondary"))[0]


def _rol_permitido(usuario, quien: str) -> bool:
    if quien == "responsable":
        return puede_presentar(usuario)
    if quien == "revisor":
        return puede_revisar(usuario)
    return bool(usuario.is_superuser)


def acciones_disponibles(presentacion, usuario, listo: bool = True) -> list[dict]:
    """Las acciones que este usuario puede ejecutar sobre esta presentación."""
    if not presentacion:
        return []
    estado = presentacion.get("estado")
    salida = []
    for accion, (origen, destino, quien) in ACCIONES.items():
        if accion == "consolidar" or estado not in origen:
            continue
        if not _rol_permitido(usuario, quien):
            continue
        # No se puede cerrar la carga si falta algun archivo obligatorio.
        if accion == "cerrar_carga" and not listo:
            continue
        salida.append(
            {
                "accion": accion,
                "destino": destino,
                "etiqueta": ETIQUETAS[accion],
                "ayuda": AYUDAS[accion],
            }
        )
    return salida


def ejecutar(presentacion_id: int, accion: str, usuario, listo: bool = True) -> str:
    """Aplica una transición. Valida estado de origen y rol."""
    if accion not in ACCIONES:
        raise TransicionInvalida("La acción solicitada no existe.")
    origen, destino, quien = ACCIONES[accion]

    with connection.cursor() as cur:
        cur.execute(
            "SELECT estado FROM mir_c2_presentacion WHERE id = %s", [presentacion_id]
        )
        fila = cur.fetchone()
        if not fila:
            raise TransicionInvalida("No existe la presentación.")
        estado = fila[0]

        if estado not in origen:
            raise TransicionInvalida(
                f"No se puede {ETIQUETAS[accion].lower()} cuando la presentación "
                f"está en «{estado_legible(estado)}»."
            )
        if not _rol_permitido(usuario, quien):
            raise TransicionInvalida(f"Tu rol no puede {ETIQUETAS[accion].lower()}.")
        if accion == "cerrar_carga" and not listo:
            raise TransicionInvalida(
                "Faltan archivos obligatorios por importar. No se puede cerrar la carga."
            )

        usr = usuario.get_username()
        if accion == "reabrir_carga":
            # Reabrir deshace el cierre: la revision anterior queda sin efecto.
            cur.execute(
                """UPDATE mir_c2_presentacion
                           SET estado = %s, cerrada_el = NULL, habilitada_el = NULL
                           WHERE id = %s""",
                [destino, presentacion_id],
            )
        elif accion == "cerrar_carga":
            cur.execute(
                """UPDATE mir_c2_presentacion
                           SET estado = %s, cerrada_el = NOW(), usuario_cierra = %s
                           WHERE id = %s""",
                [destino, usr, presentacion_id],
            )
        elif accion == "habilitar":
            cur.execute(
                """UPDATE mir_c2_presentacion
                           SET estado = %s, habilitada_el = NOW(), usuario_habilita = %s
                           WHERE id = %s""",
                [destino, usr, presentacion_id],
            )
        elif accion == "presentar":
            cur.execute(
                """UPDATE mir_c2_presentacion
                           SET estado = %s, presentada_el = NOW(), usuario_presenta = %s
                           WHERE id = %s""",
                [destino, usr, presentacion_id],
            )
        elif accion == "consolidar":
            cur.execute(
                """UPDATE mir_c2_presentacion
                           SET estado = %s, consolidada_el = NOW()
                           WHERE id = %s""",
                [destino, presentacion_id],
            )
        else:
            cur.execute(
                "UPDATE mir_c2_presentacion SET estado = %s WHERE id = %s",
                [destino, presentacion_id],
            )
    return destino


# ---------------------------------------------------------------------------
# Observaciones
# ---------------------------------------------------------------------------


def observaciones_de(presentacion_id: int, solo_abiertas: bool = False) -> list[dict]:
    sql = """
        SELECT o.*, a.codigo AS archivo_codigo
        FROM mir_c2_observacion o
        LEFT JOIN mir_c2_importacion i ON i.id = o.importacion_id
        LEFT JOIN mir_c1_archivo a ON a.id = i.archivo_id
        WHERE o.presentacion_id = %s
    """
    if solo_abiertas:
        sql += " AND o.estado = 'ABIERTA'"
    sql += " ORDER BY o.creada_el DESC"
    with connection.cursor() as cur:
        cur.execute(sql, [presentacion_id])
        columnas = [c[0] for c in cur.description]
        return [dict(zip(columnas, f)) for f in cur.fetchall()]


def crear_observacion(presentacion_id: int, usuario, texto: str, ubicacion=None):
    """El revisor observa; no modifica el dato.

    `ubicacion` acota la observacion a un punto concreto: importacion, fila y
    registro. Va agrupado porque son tres datos de la misma cosa.
    """
    ubicacion = ubicacion or {}
    importacion_id = ubicacion.get("importacion_id")
    numero_fila = ubicacion.get("numero_fila")
    identificador_registro = ubicacion.get("identificador_registro")
    if not puede_revisar(usuario):
        raise TransicionInvalida(
            "Sólo el revisor técnico nacional puede formular observaciones."
        )
    if not (texto or "").strip():
        raise TransicionInvalida("La observación no puede estar vacía.")
    with connection.cursor() as cur:
        cur.execute(
            """
            INSERT INTO mir_c2_observacion
                (presentacion_id, importacion_id, numero_fila, identificador_registro,
                 texto, estado, usuario_observa)
            VALUES (%s, %s, %s, %s, %s, 'ABIERTA', %s)
        """,
            [
                presentacion_id,
                importacion_id or None,
                numero_fila or None,
                identificador_registro or None,
                texto.strip(),
                usuario.get_username(),
            ],
        )
        cur.execute(
            """UPDATE mir_c2_presentacion SET estado = 'OBSERVADA'
                        WHERE id = %s AND estado IN ('EN_REVISION','CERRADA','HABILITADA')""",
            [presentacion_id],
        )


def responder_observacion(observacion_id: int, usuario, respuesta: str):
    """La jurisdicción responde. Si no quedan abiertas, pasa a SUBSANADA."""
    if not (respuesta or "").strip():
        raise TransicionInvalida("La respuesta no puede estar vacía.")
    with connection.cursor() as cur:
        cur.execute(
            """UPDATE mir_c2_observacion
                       SET respuesta = %s, estado = 'RESPONDIDA',
                           respondida_el = NOW(), usuario_responde = %s
                       WHERE id = %s""",
            [respuesta.strip(), usuario.get_username(), observacion_id],
        )
        cur.execute(
            "SELECT presentacion_id FROM mir_c2_observacion WHERE id = %s",
            [observacion_id],
        )
        fila = cur.fetchone()
        if not fila:
            return
        presentacion_id = fila[0]
        cur.execute(
            """SELECT COUNT(*) FROM mir_c2_observacion
                        WHERE presentacion_id = %s AND estado = 'ABIERTA'""",
            [presentacion_id],
        )
        if cur.fetchone()[0] == 0:
            cur.execute(
                """UPDATE mir_c2_presentacion SET estado = 'SUBSANADA'
                            WHERE id = %s AND estado = 'OBSERVADA'""",
                [presentacion_id],
            )


def registrar_expediente(presentacion_id: int, numero: str, usuario):
    """El número GDE se incorpora después de remitir el comprobante.

    Su ausencia no impide la consolidación: es un resguardo documental de la
    jurisdicción, no una instancia de validación.
    """
    if not puede_presentar(usuario):
        raise TransicionInvalida(
            "Sólo el responsable provincial puede registrar el expediente."
        )
    with connection.cursor() as cur:
        cur.execute(
            "UPDATE mir_c2_presentacion SET expediente = %s WHERE id = %s",
            [(numero or "").strip()[:100], presentacion_id],
        )


# Lo que puede pasar a ser un período. PREPARACION es hacia atrás: se usa
# mientras la estructura todavía se puede tocar.
ESTADOS_DE_PERIODO = ("PREPARACION", "ABIERTO", "CERRADO")


def cambiar_estado_del_periodo(codigo: str, estado: str, usuario) -> str:
    """Abre o cierra un período para todas las jurisdicciones.

    Es la ventana de presentación: mientras el período no está ABIERTO no se
    recibe ningún archivo, y una vez CERRADO tampoco. Lo decide el nivel
    nacional, no la provincia.
    """
    if not puede_administrar(usuario):
        raise TransicionInvalida("Sólo el nivel nacional abre y cierra un período.")
    if estado not in ESTADOS_DE_PERIODO:
        raise TransicionInvalida(f"«{estado}» no es un estado de período.")
    with connection.cursor() as cur:
        cur.execute(
            "UPDATE mir_c2_periodo SET estado = %s WHERE codigo = %s",
            [estado, codigo],
        )
        if not cur.rowcount:
            raise TransicionInvalida(f"El período {codigo} no está definido.")
    return estado


def borrar_todas_las_importaciones() -> dict:
    """Deja el sistema sin ninguna importación, en todas las jurisdicciones.

    **Es una herramienta de prueba y no forma parte del sistema.** Está porque
    durante las pruebas hace falta repetir el mismo circuito muchas veces:
    importar un archivo que anduvo, cambiarle algo, ver si pincha. Sin esto hay
    que ir a la base a mano.

    Al integrar el módulo a SISOC, esto se va con el resto de las herramientas de prueba.
    """
    borrados = {"filas": 0, "importaciones": 0, "presentaciones": 0, "periodos": 0}
    with connection.cursor() as cur:
        # Las tablas receptoras no están declaradas en ningún lado: su nombre se
        # deduce por convención al crearlas. Se las reconoce porque son las
        # únicas de la Capa 2 que cuelgan de una importación.
        cur.execute(
            """
            SELECT c.TABLE_NAME
              FROM information_schema.COLUMNS c
             WHERE c.TABLE_SCHEMA = DATABASE()
               AND c.COLUMN_NAME = 'importacion_id'
               AND c.TABLE_NAME LIKE 'mir_c2_%'
               AND c.TABLE_NAME NOT IN ('mir_c2_reglas_incumplidas',
                                        'mir_c2_errores_de_importacion',
                                        'mir_c2_historial_cambios',
                                        'mir_c2_observacion')
        """
        )
        tablas = [f[0] for f in cur.fetchall()]

        for tabla in tablas:
            # El nombre sale del catálogo de la base, no de la petición. Aun
            # así se comprueba antes de interpolarlo.
            if not re.fullmatch(r"mir_c2_[a-z0-9_]{1,50}", tabla or ""):
                continue
            cur.execute(f"DELETE FROM `{tabla}`")
            borrados["filas"] += cur.rowcount

        for tabla in (
            "mir_c2_reglas_incumplidas",
            "mir_c2_errores_de_importacion",
            "mir_c2_historial_cambios",
            "mir_c2_observacion",
        ):
            cur.execute(f"DELETE FROM `{tabla}`")

        cur.execute("DELETE FROM mir_c2_importacion")
        borrados["importaciones"] = cur.rowcount
        cur.execute("DELETE FROM mir_c2_presentacion")
        borrados["presentaciones"] = cur.rowcount

        # Y se reabre el período. Sin esto la herramienta dejaba el sistema a
        # medio camino: borraba todo pero, si el período había quedado cerrado
        # —probando el circuito, por ejemplo—, no se podía volver a importar
        # nada y no quedaba forma obvia de salir. «Volver a empezar» incluye
        # poder empezar.
        cur.execute(
            "UPDATE mir_c2_periodo SET estado = 'ABIERTO' WHERE estado <> 'ABIERTO'"
        )
        borrados["periodos"] = cur.rowcount

    return borrados


def comprobante(presentacion_id: int) -> dict:
    """Los datos que identifican la presentación, para el comprobante."""
    with connection.cursor() as cur:
        cur.execute(
            """
            SELECT s.id, s.version, s.estado, s.presentada_el, s.usuario_presenta,
                   s.expediente, j.nombre AS jurisdiccion,
                   p.codigo AS periodo, p.fecha_desde, p.fecha_hasta
            FROM mir_c2_presentacion s
            JOIN mir_c2_jurisdiccion j ON j.id = s.jurisdiccion_id
            JOIN mir_c2_periodo p ON p.id = s.periodo_id
            WHERE s.id = %s
        """,
            [presentacion_id],
        )
        columnas = [c[0] for c in cur.description]
        fila = cur.fetchone()
        if not fila:
            return {}
        datos = dict(zip(columnas, fila))

        cur.execute(
            """
            SELECT a.codigo, i.nombre_archivo, i.filas_incorporadas, i.iniciada_el
            FROM mir_c2_importacion i
            JOIN mir_c1_archivo a ON a.id = i.archivo_id
            WHERE i.presentacion_id = %s AND i.estado = 'VALIDA'
            ORDER BY a.codigo
        """,
            [presentacion_id],
        )
        columnas = [c[0] for c in cur.description]
        datos["archivos"] = [dict(zip(columnas, f)) for f in cur.fetchall()]
    return datos
