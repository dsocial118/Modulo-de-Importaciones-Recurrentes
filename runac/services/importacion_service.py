"""Servicio de importación.

Toda la lógica vive acá; las vistas no deciden nada. Es la forma que pide SISOC
(`docs/ia/`), y la que hace que esto se pueda mudar al repositorio.

El motor de validación no está acá: está en `services/motor/`, es Python puro y
no sabe nada de Django ni de web.
"""

from __future__ import annotations

import os
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.db import connection

# El motor se importa por ruta porque está pensado para correr también fuera de
# Django, desde la línea de comandos.
_MOTOR = Path(__file__).resolve().parent / "motor"
if str(_MOTOR) not in sys.path:
    sys.path.insert(0, str(_MOTOR))

# El import va aca y no arriba porque depende del sys.path que se arma
# unas lineas antes: el motor corre tambien fuera de Django.
import importar as motor_importar  # noqa: E402  # pylint: disable=wrong-import-position
from comun import (  # noqa: E402  # pylint: disable=wrong-import-position
    titulo_sin_instrucciones,
)


def _fila_a_dict(cursor):
    columnas = [c[0] for c in cursor.description]
    return [dict(zip(columnas, fila)) for fila in cursor.fetchall()]


# ---------------------------------------------------------------------------
# Consultas de configuración
# ---------------------------------------------------------------------------


def periodos():
    with connection.cursor() as cur:
        cur.execute(
            """
            SELECT p.id, p.codigo, p.anio, p.numero, p.fecha_desde, p.fecha_hasta, p.estado,
                   (SELECT COUNT(*) FROM runac_c2_presentacion s WHERE s.periodo_id = p.id) AS presentaciones
            FROM runac_c2_periodo p ORDER BY p.anio DESC, p.numero DESC
        """
        )
        return _fila_a_dict(cur)


def periodo(codigo: str):
    with connection.cursor() as cur:
        cur.execute("SELECT * FROM runac_c2_periodo WHERE codigo = %s", [codigo])
        filas = _fila_a_dict(cur)
    return filas[0] if filas else None


def archivos_esperados(codigo_periodo: str):
    """Los archivos que la provincia tiene que presentar, con su estructura."""
    with connection.cursor() as cur:
        # La estructura de un período es la de las VERSIONES que ese período usa.
        cur.execute(
            """
            SELECT a.id, a.codigo, av.id AS version_id, av.numero AS version,
                   av.nombre_esperado, a.descripcion AS nombre_archivo,
                   av.titulo, av.orden_importacion, av.obligatorio,
                   COUNT(DISTINCT h.id) AS hojas,
                   COUNT(DISTINCT c.id) AS campos,
                   COUNT(DISTINCT c.catalogo_id) AS catalogos,
                   COUNT(DISTINCT cr.id) AS reglas
            FROM runac_c2_periodo p
            JOIN runac_c2_periodo_archivo pa ON pa.periodo_id = p.id
            JOIN runac_c1_archivo_version av ON av.id = pa.archivo_version_id
            JOIN runac_c1_archivo a ON a.id = av.archivo_id
            LEFT JOIN runac_c1_hoja h ON h.archivo_version_id = av.id
            LEFT JOIN runac_c1_campo c ON c.hoja_id = h.id
            LEFT JOIN runac_c1_campo_regla cr ON cr.campo_id = c.id
            WHERE p.codigo = %s
            GROUP BY a.id, av.id ORDER BY av.orden_importacion
        """,
            [codigo_periodo],
        )
        archivos = _fila_a_dict(cur)

    # El titulo se limpia tambien al leerlo, y no solo al extraerlo: las
    # definiciones ya cargadas arrastran la consigna de la planilla pegada al
    # titulo, y regenerarlas por eso solo no vale la pena.
    for archivo in archivos:
        archivo["titulo"] = titulo_sin_instrucciones(archivo.get("titulo"))
        archivo["nombre"] = nombre_de_archivo(archivo)
    return archivos


# Como se llama un archivo cuando todavia no se le puso nombre. Se prefiere no
# decir nada antes que mostrar el titulo de una de sus hojas: el archivo de
# dispositivos penales tiene cinco, y ponerle el encabezado de la primera lo
# hacia parecer el listado de una sola.
def nombre_de_archivo(archivo: dict) -> str:
    """El nombre del archivo, que es un dato del archivo y no de sus hojas.

    Vive en «runac_c1_archivo.descripcion», la tabla que NO se versiona: el
    archivo se sigue llamando igual aunque cambie su estructura. Lo va a
    administrar el Responsable Nacional cuando exista el CRUD de archivos.

    Mientras el texto sea el autogenerado —«Archivo X de RUNAC. hoja…»— se
    devuelve vacio: es un relleno tecnico, no un nombre.
    """
    nombre = (archivo.get("nombre_archivo") or "").strip()
    return "" if nombre.startswith("Archivo ") else nombre


def campos_de(codigo_archivo: str):
    with connection.cursor() as cur:
        cur.execute(
            """
            SELECT h.nombre_esperado AS hoja, c.orden, c.nombre, c.titulo_esperado,
                   c.tipo_dato, c.longitud_maxima, c.obligatorio, c.ayuda,
                   d.nombre_esperado AS grupo, cat.codigo AS catalogo,
                   (SELECT COUNT(*) FROM runac_c1_catalogo_opcion o
                     WHERE o.catalogo_id = cat.id AND o.activo = 1) AS opciones,
                   (SELECT COUNT(*) FROM runac_c1_campo_regla cr WHERE cr.campo_id = c.id) AS reglas
            FROM runac_c1_campo c
            JOIN runac_c1_hoja h ON h.id = c.hoja_id
            JOIN runac_c1_archivo_version av ON av.id = h.archivo_version_id AND av.estado = 'VIGENTE'
            JOIN runac_c1_archivo a ON a.id = av.archivo_id
            LEFT JOIN runac_c1_dimension d ON d.id = c.dimension_id
            LEFT JOIN runac_c1_catalogo cat ON cat.id = c.catalogo_id
            WHERE a.codigo = %s
            ORDER BY h.orden_procesamiento, c.orden
        """,
            [codigo_archivo],
        )
        return _fila_a_dict(cur)


def presentacion_completa(presentacion_id: int) -> bool:
    """Si están importados todos los archivos obligatorios de la presentación.

    Se calcula **desde la presentación**, no desde parámetros de la petición: es
    la condición para cerrar la carga, y un dato que llega del navegador no
    puede decidirla.
    """
    with connection.cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(*) AS obligatorios,
                   SUM(EXISTS (
                       SELECT 1 FROM runac_c2_importacion i
                        WHERE i.presentacion_id = s.id
                          AND i.archivo_version_id = av.id
                          AND i.estado = 'VALIDA')) AS importados
              FROM runac_c2_presentacion s
              JOIN runac_c2_periodo_archivo pa ON pa.periodo_id = s.periodo_id
              JOIN runac_c1_archivo_version av ON av.id = pa.archivo_version_id
             WHERE s.id = %s AND av.obligatorio = 1
            """,
            [presentacion_id],
        )
        fila = cur.fetchone()

    if not fila:
        return False
    obligatorios, importados = fila[0] or 0, fila[1] or 0
    # Sin archivos obligatorios declarados no hay nada que dar por completo: una
    # presentación inexistente no puede considerarse cerrable.
    return obligatorios > 0 and importados == obligatorios


def hojas_disponibles():
    """Las hojas de datos, para el selector de la pantalla de reglas.

    Se lista Archivo — Hoja y no sólo archivo: un archivo con seis hojas
    volcadas una debajo de la otra no se consulta, se sufre.
    """
    with connection.cursor() as cur:
        cur.execute(
            """
            SELECT a.codigo AS archivo, h.nombre_esperado AS hoja,
                   av.titulo, COUNT(c.id) AS campos
            FROM runac_c1_hoja h
            JOIN runac_c1_archivo_version av ON av.id = h.archivo_version_id
                                            AND av.estado = 'VIGENTE'
            JOIN runac_c1_archivo a ON a.id = av.archivo_id
            LEFT JOIN runac_c1_campo c ON c.hoja_id = h.id
            GROUP BY a.codigo, h.id
            HAVING campos > 0
            ORDER BY av.orden_importacion, h.orden_procesamiento
        """
        )
        return _fila_a_dict(cur)


def reglas_de_hoja(codigo_archivo: str, nombre_hoja: str):
    """Qué se espera en cada columna de una hoja, en lenguaje llano.

    Es la pantalla que evita que el operador tenga que adivinar. No muestra
    contadores ni nombres técnicos: título, si es obligatorio, qué tipo de dato
    se espera, qué valores admite y qué condición tiene que cumplir.
    """
    with connection.cursor() as cur:
        cur.execute(
            """
            SELECT c.id, c.orden, c.titulo_esperado, c.tipo_dato,
                   c.longitud_maxima, c.obligatorio,
                   c.ayuda, d.nombre_esperado AS grupo,
                   cat.codigo AS catalogo, cat.nombre AS lista,
                   (SELECT COUNT(*) FROM runac_c1_catalogo_opcion o
                     WHERE o.catalogo_id = cat.id AND o.activo = 1) AS opciones,
                   (SELECT GROUP_CONCAT(o.valor_esperado ORDER BY o.orden SEPARATOR ' · ')
                      FROM runac_c1_catalogo_opcion o
                     WHERE o.catalogo_id = cat.id AND o.activo = 1) AS valores
            FROM runac_c1_campo c
            JOIN runac_c1_hoja h ON h.id = c.hoja_id
            JOIN runac_c1_archivo_version av ON av.id = h.archivo_version_id
                                            AND av.estado = 'VIGENTE'
            JOIN runac_c1_archivo a ON a.id = av.archivo_id
            LEFT JOIN runac_c1_dimension d ON d.id = c.dimension_id
            LEFT JOIN runac_c1_catalogo cat ON cat.id = c.catalogo_id
            WHERE a.codigo = %s AND h.nombre_esperado = %s
            ORDER BY c.orden
        """,
            [codigo_archivo, nombre_hoja],
        )
        campos = _fila_a_dict(cur)

        cur.execute(
            """
            SELECT cr.campo_id, cr.severidad, tr.nombre AS tipo_regla,
                   r.parametros,
                   COALESCE(NULLIF(cr.mensaje, ''), r.descripcion, r.nombre) AS texto
            FROM runac_c1_campo_regla cr
            JOIN runac_c1_regla r ON r.id = cr.regla_id
            JOIN runac_c1_tipo_regla tr ON tr.id = r.tipo_regla_id
            JOIN runac_c1_campo c ON c.id = cr.campo_id
            JOIN runac_c1_hoja h ON h.id = c.hoja_id
            JOIN runac_c1_archivo_version av ON av.id = h.archivo_version_id
                                            AND av.estado = 'VIGENTE'
            JOIN runac_c1_archivo a ON a.id = av.archivo_id
            WHERE a.codigo = %s AND h.nombre_esperado = %s
        """,
            [codigo_archivo, nombre_hoja],
        )
        reglas: dict[int, list] = {}
        for fila in _fila_a_dict(cur):
            reglas.setdefault(fila["campo_id"], []).append(fila)

    for campo in campos:
        campo["reglas"] = reglas.get(campo["id"], [])
    return campos


# ---------------------------------------------------------------------------
# Presentación
# ---------------------------------------------------------------------------


def presentacion_de(jurisdiccion: str, codigo_periodo: str, crear: bool = False):
    """La presentación de esa jurisdicción en ese período.

    `crear` es explícito y por omisión no crea: consultar el estado de una
    presentación creaba la presentación. Bastaba con que alguien mirara la
    pantalla de carga eligiendo otra provincia para que quedara dada de alta
    una presentación vacía que nadie inició.
    """
    with connection.cursor() as cur:
        cur.execute(
            """
            SELECT s.*, j.nombre AS jurisdiccion
            FROM runac_c2_presentacion s
            JOIN runac_c2_periodo p ON p.id = s.periodo_id
            JOIN runac_c2_jurisdiccion j ON j.id = s.jurisdiccion_id
            WHERE j.nombre = %s AND p.codigo = %s
            ORDER BY s.version DESC LIMIT 1
        """,
            [jurisdiccion, codigo_periodo],
        )
        filas = _fila_a_dict(cur)
        if filas:
            return filas[0]
        if not crear:
            return None
        cur.execute(
            "SELECT id FROM runac_c2_periodo WHERE codigo = %s", [codigo_periodo]
        )
        fila = cur.fetchone()
        if not fila:
            return None
        # La jurisdicción es una entidad: si no existe, se da de alta.
        cur.execute(
            "SELECT id FROM runac_c2_jurisdiccion WHERE nombre = %s", [jurisdiccion]
        )
        f_j = cur.fetchone()
        if f_j:
            jurisdiccion_id = f_j[0]
        else:
            cur.execute(
                """INSERT INTO runac_c2_jurisdiccion (codigo, nombre, modalidad, activa)
                           VALUES (%s, %s, 'PRESENTACION_PERIODICA', 1)""",
                [jurisdiccion.upper()[:20], jurisdiccion],
            )
            cur.execute(
                "SELECT id FROM runac_c2_jurisdiccion WHERE nombre = %s", [jurisdiccion]
            )
            jurisdiccion_id = cur.fetchone()[0]
        cur.execute(
            """
            INSERT INTO runac_c2_presentacion (periodo_id, jurisdiccion_id, version, estado)
            VALUES (%s, %s, 1, 'EN_CARGA')
        """,
            [fila[0], jurisdiccion_id],
        )
    return presentacion_de(jurisdiccion, codigo_periodo, crear=False)


def importaciones_de(presentacion_id: int):
    """La importación vigente de cada archivo, más el historial."""
    with connection.cursor() as cur:
        cur.execute(
            """
            SELECT i.*, a.codigo AS archivo_codigo, av.titulo AS archivo_titulo,
                   av.orden_importacion, av.obligatorio
            FROM runac_c2_importacion i
            LEFT JOIN runac_c1_archivo a ON a.id = i.archivo_id
            LEFT JOIN runac_c1_archivo_version av ON av.id = i.archivo_version_id
            WHERE i.presentacion_id = %s
            ORDER BY av.orden_importacion, i.iniciada_el DESC
        """,
            [presentacion_id],
        )
        return _fila_a_dict(cur)


def estado_de_la_presentacion(jurisdiccion: str, codigo_periodo: str):
    """Resume, por archivo, si está cargado y cómo quedó.

    Una jurisdicción que todavía no empezó devuelve **la misma forma** que una
    que ya cargó: los archivos que se esperan, todos en SIN_CARGAR. Antes
    devolvía los archivos tal como salen de la Capa 1, sin la clave `estado`, y
    quien los recorría se rompía.

    Eso no se notaba mientras consultar creaba la presentación: la rama del «no
    hay nada todavía» no llegaba a ejecutarse nunca. Al separar la consulta del
    alta quedó a la vista.
    """
    pres = presentacion_de(jurisdiccion, codigo_periodo)
    esperados = archivos_esperados(codigo_periodo)
    if not pres:
        return {
            "presentacion": None,
            "archivos": [
                {
                    **a,
                    "importacion": None,
                    "importada": False,
                    "estado": "SIN_CARGAR",
                }
                for a in esperados
            ],
            "listo": False,
        }

    # La importación vigente de cada archivo es la última que quedó VALIDA.
    # Las ANULADAS fueron reemplazadas; las FALLIDAS no incorporaron nada.
    vigentes, ultimos = {}, {}
    for imp in importaciones_de(pres["id"]):
        cod = imp["archivo_codigo"]
        if not cod:
            continue
        ultimos.setdefault(cod, imp)
        if cod not in vigentes and imp["estado"] == "VALIDA":
            vigentes[cod] = imp

    filas = []
    for a in esperados:
        imp = vigentes.get(a["codigo"])
        ultimo = ultimos.get(a["codigo"])
        filas.append(
            {
                **a,
                "importacion": imp or ultimo,
                "importada": bool(imp),
                "estado": (
                    (imp or ultimo)["estado"] if (imp or ultimo) else "SIN_CARGAR"
                ),
            }
        )

    obligatorios = [f for f in filas if f["obligatorio"]]
    # "Listo" es: todos los archivos obligatorios importados. Es la condición
    # para poder cerrar la carga, no para presentar.
    listo = bool(obligatorios) and all(f["importada"] for f in obligatorios)
    return {"presentacion": pres, "archivos": filas, "listo": listo}


# ---------------------------------------------------------------------------
# Carga
# ---------------------------------------------------------------------------


def guardar_archivos(archivos, jurisdiccion: str, codigo_periodo: str) -> Path:
    """Deja los archivos subidos en una carpeta propia de esta carga."""
    marca = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = Path(settings.RUNAC_CARGAS) / f"{jurisdiccion}_{codigo_periodo}_{marca}"
    destino.mkdir(parents=True, exist_ok=True)
    for f in archivos:
        with open(destino / f.name, "wb") as salida:
            for bloque in f.chunks():
                salida.write(bloque)
    return destino


def reconocer(carpeta: Path, codigo_periodo: str):
    """Empareja lo subido con lo que la Capa 1 espera. No procesa nada."""
    with connection.cursor() as cur:
        cur.execute(
            """
            SELECT a.id, a.codigo, av.id AS version_id,
                   av.nombre_esperado, av.orden_importacion, av.obligatorio
            FROM runac_c2_periodo p
            JOIN runac_c2_periodo_archivo pa ON pa.periodo_id = p.id
            JOIN runac_c1_archivo_version av ON av.id = pa.archivo_version_id
            JOIN runac_c1_archivo a ON a.id = av.archivo_id
            WHERE p.codigo = %s ORDER BY av.orden_importacion
        """,
            [codigo_periodo],
        )
        esperados = _fila_a_dict(cur)
    reconocidos, sin_reconocer, faltantes, ambiguos = motor_importar.reconocer(
        str(carpeta), esperados
    )
    return {
        "reconocidos": sorted(
            reconocidos, key=lambda r: r["archivo"]["orden_importacion"]
        ),
        "sin_reconocer": sin_reconocer,
        "faltantes": faltantes,
        "ambiguos": ambiguos,
        "carpeta": str(carpeta),
    }


def procesar(
    carpeta: Path,
    jurisdiccion: str,
    codigo_periodo: str,
    usuario: str,
    asignacion: dict[str, str] | None = None,
):
    """Corre el motor sobre la carpeta y devuelve el resumen.

    `asignacion` permite forzar qué archivo es cuál, cuando el usuario lo indicó
    a mano en la pantalla de reconocimiento.
    """
    resultado = motor_importar.procesar_carpeta(
        carpeta=str(carpeta),
        jurisdiccion=jurisdiccion,
        periodo=codigo_periodo,
        usuario=usuario,
        informe=str(settings.RUNAC_INFORMES),
        asignacion=asignacion or {},
        conexion={
            "host": settings.DATABASES["default"]["HOST"],
            "port": int(settings.DATABASES["default"]["PORT"]),
            "user": settings.DATABASES["default"]["USER"],
            "password": settings.DATABASES["default"]["PASSWORD"],
            "database": settings.DATABASES["default"]["NAME"],
        },
    )
    return resultado


def hallazgos_de(
    importacion_id: int,
    severidad: str | None = None,
    hoja: str | None = None,
    buscar: str | None = None,
    limite: int = 500,
):
    # Las reglas incumplidas son de un archivo que SÍ fue admitido. Los problemas
    # del archivo entero viven en runac_c2_errores_de_importacion.
    sql = """
        SELECT h.numero_fila, h.nombre_hoja, h.columna, h.nombre_campo, h.severidad,
               h.codigo, h.valor_encontrado, h.descripcion
        FROM runac_c2_reglas_incumplidas h WHERE h.importacion_id = %s
    """
    params: list = [importacion_id]
    if severidad:
        sql += " AND h.severidad = %s"
        params.append(severidad)
    if hoja:
        sql += " AND h.nombre_hoja = %s"
        params.append(hoja)
    if buscar:
        sql += " AND (h.descripcion LIKE %s OR h.nombre_campo LIKE %s)"
        params += [f"%{buscar}%", f"%{buscar}%"]
    sql += " ORDER BY h.numero_fila, h.severidad DESC LIMIT %s"
    params.append(limite)
    with connection.cursor() as cur:
        cur.execute(sql, params)
        return _fila_a_dict(cur)


def resumen_de_hallazgos(importacion_id: int):
    with connection.cursor() as cur:
        cur.execute(
            """
            SELECT codigo, severidad, COUNT(*) AS casos, MIN(descripcion) AS ejemplo
            FROM runac_c2_reglas_incumplidas WHERE importacion_id = %s
            GROUP BY codigo, severidad ORDER BY casos DESC
        """,
            [importacion_id],
        )
        return _fila_a_dict(cur)


# ---------------------------------------------------------------------------
# Carga de a un archivo
#
# El documento funcional define esta modalidad para la primera versión: el
# operador indica de qué archivo se trata, de modo que el sistema no necesita
# deducirlo del nombre, y el ORDEN lo controla el sistema.
# ---------------------------------------------------------------------------


def archivos_referenciados(codigo_archivo: str, codigo_periodo: str) -> list[str]:
    """Qué otros archivos necesita este, según lo que declara la Capa 1.

    La dependencia no es el orden: es la referencia. Un archivo depende de otro
    cuando alguno de sus campos tiene una regla que exige que el valor exista
    allá —«el dispositivo que nombra la nómina tiene que estar declarado en el
    archivo de dispositivos»—. Eso está en la configuración, se consulta, y no
    hay que mantenerlo en dos lugares.
    """
    with connection.cursor() as cur:
        cur.execute(
            """
            SELECT DISTINCT JSON_UNQUOTE(JSON_EXTRACT(r.parametros, '$.archivo'))
            FROM runac_c2_periodo_archivo pa
            JOIN runac_c2_periodo p ON p.id = pa.periodo_id
            JOIN runac_c1_archivo_version av ON av.id = pa.archivo_version_id
            JOIN runac_c1_archivo a ON a.id = av.archivo_id
            JOIN runac_c1_hoja h ON h.archivo_version_id = av.id
            JOIN runac_c1_campo c ON c.hoja_id = h.id
            JOIN runac_c1_campo_regla cr ON cr.campo_id = c.id
            JOIN runac_c1_regla r ON r.id = cr.regla_id
            JOIN runac_c1_tipo_regla tr ON tr.id = r.tipo_regla_id
            WHERE p.codigo = %s AND a.codigo = %s
              AND tr.nombre = 'EXISTE_EN_ARCHIVO'
            """,
            [codigo_periodo, codigo_archivo],
        )
        return [f[0] for f in cur.fetchall() if f[0]]


# Los archivos que describen la oferta —dónde puede estar un chico— van antes
# que los que describen a las personas. No es una referencia campo a campo: es
# el orden en que la presentación tiene sentido, y vale aunque todavía no esté
# declarada la regla de integridad que lo verifica dato por dato.
ARCHIVOS_DE_DISPOSITIVOS = ("DISP_PENAL", "DISP_SCP")


def dependencias_faltantes(codigo_archivo: str, jurisdiccion: str, codigo_periodo: str):
    """Archivos que deben estar importados antes que este.

    Son dos cosas distintas y las dos traban:

    1. **La política:** las nóminas van después de los dispositivos. Una nómina
       dice dónde está alojado un chico; si el dispositivo todavía no se declaró,
       la nómina habla de algo que para el sistema no existe.
    2. **La referencia declarada en la Capa 1:** además, un archivo espera a los
       que nombra campo a campo —la nómina penal al archivo de dispositivos
       penales— y eso verifica que cada valor exista.

    Un tiempo sólo estuvo la segunda, y quedó floja: como la referencia del MPE
    no estaba declarada, se podía importar antes que los dispositivos. La
    política no depende de que esa declaración exista.
    """
    esperados = {a["codigo"] for a in archivos_esperados(codigo_periodo)}
    requeridos = set(archivos_referenciados(codigo_archivo, codigo_periodo))
    if codigo_archivo not in ARCHIVOS_DE_DISPOSITIVOS:
        requeridos |= {c for c in ARCHIVOS_DE_DISPOSITIVOS if c in esperados}
    if not requeridos:
        return []
    estado = estado_de_la_presentacion(jurisdiccion, codigo_periodo)
    return [
        a
        for a in estado["archivos"]
        if a["codigo"] in requeridos and not a.get("importada")
    ]


# Lo que se acepta recibir. El tope no sale de un cálculo: es holgado para las
# planillas reales —la más grande de las de prueba no llega a 1 MB— y corta el
# archivo enorme que llenaría el disco antes de que nadie lo mire.
EXTENSIONES_ADMITIDAS = (".xlsx", ".xlsm")
TAMANO_MAXIMO = 40 * 1024 * 1024


def _nombre_de_archivo_seguro(nombre: str) -> str:
    """El nombre tal como llegó, sin nada que sirva para salir de la carpeta.

    El nombre lo elige quien sube el archivo y se usa para armar una ruta en el
    disco: `../../algo.xlsx` escribiría fuera del directorio de cargas. Se
    conserva sólo el último tramo y se descartan los separadores.
    """
    limpio = os.path.basename(str(nombre or "").replace("\\", "/"))
    limpio = re.sub(r"[^A-Za-z0-9 ._\-áéíóúüñÁÉÍÓÚÜÑ]", "_", limpio).strip(". ")
    return limpio[:150] or "archivo.xlsx"


def _archivo_admisible(fichero) -> str | None:
    """Devuelve el motivo por el que no se puede recibir, o None si se puede."""
    nombre = _nombre_de_archivo_seguro(fichero.name)
    if not nombre.lower().endswith(EXTENSIONES_ADMITIDAS):
        return (
            "Sólo se reciben planillas de Excel "
            f'({", ".join(EXTENSIONES_ADMITIDAS)}).'
        )
    tamano = getattr(fichero, "size", None) or 0
    if tamano > TAMANO_MAXIMO:
        return (
            f"El archivo pesa {tamano // (1024 * 1024)} MB y el máximo admitido "
            f"es {TAMANO_MAXIMO // (1024 * 1024)} MB."
        )
    if tamano == 0:
        return "El archivo está vacío."
    return None


# Estados de la presentación en los que todavía se puede importar. Son los
# mismos en los que se puede corregir un dato: mientras la carga esté abierta o
# la provincia esté subsanando lo que Nación observó.
ESTADOS_QUE_ADMITEN_CARGA = ("EN_CARGA", "OBSERVADA", "SUBSANADA")


def _se_puede_importar(jurisdiccion: str, codigo_periodo: str) -> str | None:
    """Por qué no se puede importar en este período, o None si se puede.

    Son dos puertas distintas. El **período** lo abre y lo cierra Nación para
    todas las provincias: fuera de la ventana de presentación no se recibe
    nada. El **estado de la presentación** es de esa provincia: con la carga
    cerrada primero hay que reabrirla, y eso lo decide el circuito.

    Faltaban las dos. El período tenía un estado que no controlaba nada, y una
    presentación cerrada volvía a EN_CARGA sola al subir un archivo.
    """
    datos = periodo(codigo_periodo)
    if not datos:
        return f"El período {codigo_periodo} no está definido."
    if datos["estado"] != "ABIERTO":
        legibles = {
            "PREPARACION": "todavía no se abrió",
            "CERRADO": "ya se cerró",
        }
        return (
            f"El período {codigo_periodo} {legibles.get(datos['estado'], 'no está abierto')}: "
            "no se pueden importar archivos."
        )

    pres = presentacion_de(jurisdiccion, codigo_periodo, crear=False)
    if pres and pres["estado"] not in ESTADOS_QUE_ADMITEN_CARGA:
        return (
            f'La presentación de {jurisdiccion} está en «{pres["estado"]}»: '
            "para importar, primero hay que reabrir la carga."
        )
    return None


def _comparable(texto: str) -> str:
    """Forma comparable de un texto: sin tildes, sin separadores, en minúsculas.

    Sirve para que «Entre Ríos» y «EntreRios» sean la misma jurisdicción y para
    que no importe si el archivo usa guiones, guiones bajos o espacios.
    """
    limpio = unicodedata.normalize("NFD", str(texto or "").lower())
    limpio = "".join(c for c in limpio if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", limpio)


def _nombre_corresponde(
    nombre: str, codigo_archivo: str, codigo_periodo: str, jurisdiccion: str
) -> bool:
    """¿El nombre del archivo es el que corresponde a esta celda de la grilla?

    Se pide que **empiece** por el código del archivo y que nombre el período y
    la jurisdicción en curso. Se admite lo que venga después —por ejemplo el
    sufijo `_CON_ERRORES` de los archivos de prueba—, porque lo que importa es
    que el archivo no sea de otro trimestre, de otra provincia ni de otra
    planilla.
    """
    limpio = _comparable(Path(nombre).stem)
    return (
        limpio.startswith(_comparable(codigo_archivo))
        and _comparable(codigo_periodo) in limpio
        and _comparable(jurisdiccion) in limpio
    )


def importar_uno(
    codigo_archivo: str, fichero, jurisdiccion: str, codigo_periodo: str, usuario: str
):
    """Importa un único archivo, declarado por el operador.

    Devuelve el resumen del motor. Si faltan dependencias, no se procesa: se
    informa qué falta, como pide el documento.
    """
    # Lo primero es si el archivo se puede recibir: antes de leerlo, de
    # guardarlo y de consultar nada.
    motivo = _archivo_admisible(fichero)
    if motivo:
        return {"rechazado": True, "codigo": codigo_archivo, "mensaje": motivo}

    motivo = _se_puede_importar(jurisdiccion, codigo_periodo)
    if motivo:
        return {"rechazado": True, "codigo": codigo_archivo, "mensaje": motivo}

    faltan = dependencias_faltantes(codigo_archivo, jurisdiccion, codigo_periodo)
    if faltan:
        return {
            "rechazado": True,
            "faltan": [f["codigo"] for f in faltan],
            "mensaje": (
                "No se puede importar %s todavía: primero hay que importar %s, "
                "porque este archivo los referencia."
                % (codigo_archivo, ", ".join(f["codigo"] for f in faltan))
            ),
        }

    # El nombre del archivo se controla ANTES de guardarlo y de procesarlo: un
    # archivo que no corresponde a este período o a esta jurisdicción no entra.
    # Era una advertencia y se procesaba igual, de modo que un archivo de otra
    # provincia podía incorporarse a la presentación en curso.
    nombre = _nombre_de_archivo_seguro(fichero.name)
    esperado = f"{codigo_archivo}_{codigo_periodo}_{jurisdiccion}.xlsx"
    if not _nombre_corresponde(nombre, codigo_archivo, codigo_periodo, jurisdiccion):
        return {
            "rechazado": True,
            "codigo": codigo_archivo,
            "nombre_sugerido": esperado,
            "mensaje": (
                f"El nombre «{nombre}» no corresponde a este archivo, "
                f"este período y esta jurisdicción. Se espera «{esperado}». "
                "El archivo no se importó."
            ),
        }

    marca = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = (
        Path(settings.RUNAC_CARGAS)
        / f"{jurisdiccion}_{codigo_periodo}_{codigo_archivo}_{marca}"
    )
    destino.mkdir(parents=True, exist_ok=True)
    ruta = destino / nombre
    with open(ruta, "wb") as salida:
        for bloque in fichero.chunks():
            salida.write(bloque)

    # La asignación fuerza qué archivo es cuál: el operador ya lo declaró, así
    # que el nombre del fichero no condiciona nada.
    resultado = procesar(
        carpeta=destino,
        jurisdiccion=jurisdiccion,
        codigo_periodo=codigo_periodo,
        usuario=usuario,
        asignacion={nombre: codigo_archivo},
    )
    resultado["rechazado"] = False
    resultado["codigo"] = codigo_archivo
    resultado["nombre_sugerido"] = esperado
    return resultado
