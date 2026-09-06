"""Servicio de importación.

Toda la lógica vive acá; las vistas no deciden nada. Es la forma que pide SISOC
(`docs/ia/`), y la que hace que esto se pueda mudar al repositorio.

El motor de validación no está acá: está en `services/motor/`, es Python puro y
no sabe nada de Django ni de web.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.db import connection, transaction

# El motor se importa por ruta porque está pensado para correr también fuera de
# Django, desde la línea de comandos.
_MOTOR = Path(__file__).resolve().parent / "motor"
if str(_MOTOR) not in sys.path:
    sys.path.insert(0, str(_MOTOR))

import importar as motor_importar  # noqa: E402


def _fila_a_dict(cursor):
    columnas = [c[0] for c in cursor.description]
    return [dict(zip(columnas, fila)) for fila in cursor.fetchall()]


# ---------------------------------------------------------------------------
# Consultas de configuración
# ---------------------------------------------------------------------------

def periodos():
    with connection.cursor() as cur:
        cur.execute("""
            SELECT p.id, p.codigo, p.anio, p.numero, p.fecha_desde, p.fecha_hasta, p.estado,
                   (SELECT COUNT(*) FROM runac_c2_presentacion s WHERE s.periodo_id = p.id) AS presentaciones
            FROM runac_c2_periodo p ORDER BY p.anio DESC, p.numero DESC
        """)
        return _fila_a_dict(cur)


def periodo(codigo: str):
    with connection.cursor() as cur:
        cur.execute("SELECT * FROM runac_c2_periodo WHERE codigo = %s", [codigo])
        filas = _fila_a_dict(cur)
    return filas[0] if filas else None


def archivos_esperados(codigo_periodo: str):
    """Los archivos que la provincia tiene que presentar, con su estructura."""
    with connection.cursor() as cur:
        cur.execute("""
            SELECT a.id, a.codigo, a.nombre_esperado, a.titulo, a.orden_importacion, a.obligatorio,
                   COUNT(DISTINCT h.id) AS hojas,
                   COUNT(DISTINCT c.id) AS campos,
                   COUNT(DISTINCT c.catalogo_id) AS catalogos,
                   COUNT(DISTINCT cr.id) AS reglas
            FROM runac_c1_archivo a
            LEFT JOIN runac_c1_hoja h ON h.archivo_id = a.id
            LEFT JOIN runac_c1_campo c ON c.hoja_id = h.id
            LEFT JOIN runac_c1_campo_regla cr ON cr.campo_id = c.id
            GROUP BY a.id ORDER BY a.orden_importacion
        """)
        return _fila_a_dict(cur)


def campos_de(codigo_archivo: str):
    with connection.cursor() as cur:
        cur.execute("""
            SELECT h.nombre_esperado AS hoja, c.orden, c.nombre, c.titulo_esperado,
                   c.tipo_dato, c.longitud_maxima, c.obligatorio, c.ayuda,
                   d.nombre_esperado AS grupo, cat.codigo AS catalogo,
                   (SELECT COUNT(*) FROM runac_c1_catalogo_opcion o
                     WHERE o.catalogo_id = cat.id AND o.activo = 1) AS opciones,
                   (SELECT COUNT(*) FROM runac_c1_campo_regla cr WHERE cr.campo_id = c.id) AS reglas
            FROM runac_c1_campo c
            JOIN runac_c1_hoja h ON h.id = c.hoja_id
            JOIN runac_c1_archivo a ON a.id = h.archivo_id
            LEFT JOIN runac_c1_dimension d ON d.id = c.dimension_id
            LEFT JOIN runac_c1_catalogo cat ON cat.id = c.catalogo_id
            WHERE a.codigo = %s
            ORDER BY h.orden_procesamiento, c.orden
        """, [codigo_archivo])
        return _fila_a_dict(cur)


# ---------------------------------------------------------------------------
# Presentación
# ---------------------------------------------------------------------------

def presentacion_de(jurisdiccion: str, codigo_periodo: str, crear: bool = True):
    with connection.cursor() as cur:
        cur.execute("""
            SELECT s.* FROM runac_c2_presentacion s
            JOIN runac_c2_periodo p ON p.id = s.periodo_id
            WHERE s.jurisdiccion = %s AND p.codigo = %s
            ORDER BY s.version DESC LIMIT 1
        """, [jurisdiccion, codigo_periodo])
        filas = _fila_a_dict(cur)
        if filas:
            return filas[0]
        if not crear:
            return None
        cur.execute("SELECT id FROM runac_c2_periodo WHERE codigo = %s", [codigo_periodo])
        fila = cur.fetchone()
        if not fila:
            return None
        cur.execute("""
            INSERT INTO runac_c2_presentacion (periodo_id, jurisdiccion, version, estado)
            VALUES (%s, %s, 1, 'BORRADOR')
        """, [fila[0], jurisdiccion])
    return presentacion_de(jurisdiccion, codigo_periodo, crear=False)


def importaciones_de(presentacion_id: int):
    """La importación vigente de cada archivo, más el historial."""
    with connection.cursor() as cur:
        cur.execute("""
            SELECT i.*, a.codigo AS archivo_codigo, a.titulo AS archivo_titulo,
                   a.orden_importacion, a.obligatorio
            FROM runac_c2_importacion i
            LEFT JOIN runac_c2_estructura e ON e.id = i.estructura_id
            LEFT JOIN runac_c1_archivo a ON a.id = e.archivo_id
            WHERE i.presentacion_id = %s
            ORDER BY a.orden_importacion, i.iniciada_el DESC
        """, [presentacion_id])
        return _fila_a_dict(cur)


def estado_de_la_presentacion(jurisdiccion: str, codigo_periodo: str):
    """Resume, por archivo, si está cargado y cómo quedó."""
    pres = presentacion_de(jurisdiccion, codigo_periodo)
    esperados = archivos_esperados(codigo_periodo)
    if not pres:
        return {"presentacion": None, "archivos": esperados, "listo": False}

    vigentes = {}
    for imp in importaciones_de(pres["id"]):
        cod = imp["archivo_codigo"]
        if cod and cod not in vigentes and imp["estado"] != "REEMPLAZADO":
            vigentes[cod] = imp

    filas = []
    for a in esperados:
        imp = vigentes.get(a["codigo"])
        filas.append({**a, "importacion": imp,
                      "estado": imp["estado"] if imp else "SIN_CARGAR"})

    obligatorios = [f for f in filas if f["obligatorio"]]
    listo = bool(obligatorios) and all(
        f["estado"] in ("VALIDADO", "REQUIERE_REVISION", "NORMALIZADO") for f in obligatorios)
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
        cur.execute("""
            SELECT a.id, a.codigo, a.nombre_esperado, a.orden_importacion, a.obligatorio
            FROM runac_c1_archivo a ORDER BY a.orden_importacion
        """)
        esperados = _fila_a_dict(cur)
    reconocidos, sin_reconocer, faltantes, ambiguos = motor_importar.reconocer(str(carpeta), esperados)
    return {
        "reconocidos": sorted(reconocidos, key=lambda r: r["archivo"]["orden_importacion"]),
        "sin_reconocer": sin_reconocer,
        "faltantes": faltantes,
        "ambiguos": ambiguos,
        "carpeta": str(carpeta),
    }


def procesar(carpeta: Path, jurisdiccion: str, codigo_periodo: str, usuario: str,
             asignacion: dict[str, str] | None = None):
    """Corre el motor sobre la carpeta y devuelve el resumen.

    `asignacion` permite forzar qué archivo es cuál, cuando el usuario lo indicó
    a mano en la pantalla de reconocimiento.
    """
    import mysql.connector

    resultado = motor_importar.procesar_carpeta(
        carpeta=str(carpeta),
        jurisdiccion=jurisdiccion,
        periodo=codigo_periodo,
        usuario=usuario,
        asignacion=asignacion or {},
        conexion=dict(
            host=settings.DATABASES["default"]["HOST"],
            port=int(settings.DATABASES["default"]["PORT"]),
            user=settings.DATABASES["default"]["USER"],
            password=settings.DATABASES["default"]["PASSWORD"],
            database=settings.DATABASES["default"]["NAME"],
        ),
    )
    return resultado


def hallazgos_de(importacion_id: int, severidad: str | None = None,
                 hoja: str | None = None, buscar: str | None = None,
                 limite: int = 500):
    sql = """
        SELECT h.numero_fila, h.nombre_hoja, h.columna, h.nombre_campo, h.severidad,
               h.codigo, h.valor_encontrado, h.descripcion
        FROM runac_c2_hallazgo h WHERE h.importacion_id = %s
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
        cur.execute("""
            SELECT codigo, severidad, COUNT(*) AS casos, MIN(descripcion) AS ejemplo
            FROM runac_c2_hallazgo WHERE importacion_id = %s
            GROUP BY codigo, severidad ORDER BY casos DESC
        """, [importacion_id])
        return _fila_a_dict(cur)
