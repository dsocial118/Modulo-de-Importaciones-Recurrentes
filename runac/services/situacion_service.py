"""El panorama del nivel nacional: cómo viene cada provincia del operativo.

Pantallas nuevas del 27-09-2026, sobre la maqueta que aprobó el responsable
funcional: «Estado de situación», «Observaciones» y «Administración». Todo se
calcula a partir de lo que ya existe —las presentaciones, sus importaciones,
sus observaciones y el historial—; no hay tablas nuevas.

Las provincias del operativo son las jurisdicciones con `activa` (guion 36).
"""

from __future__ import annotations

from datetime import datetime

from django.db import connection

from runac.permissions import puede_administrar
from runac.services import circuito_service as circuito
from runac.services import importacion_service as svc

# Cómo se agrupan los estados para contar: lo que ve el nivel nacional.
GRUPOS = {
    "PRESENTADA": "presentaron",
    "CONSOLIDADA": "presentaron",
    "HABILITADA": "presentaron",
    "CERRADA": "en_revision",
    "EN_REVISION": "en_revision",
    "OBSERVADA": "en_revision",
    "SUBSANADA": "en_revision",
    "EN_CARGA": "cargando",
    "SIN_EMPEZAR": "sin_empezar",
}


def _filas(cur) -> list[dict]:
    nombres = [c[0] for c in cur.description]
    return [dict(zip(nombres, f)) for f in cur.fetchall()]


def operativo() -> list[str]:
    """Las provincias que tienen que presentar, en orden alfabético."""
    with connection.cursor() as cur:
        cur.execute(
            "SELECT nombre FROM mir_c2_jurisdiccion WHERE activa = 1 ORDER BY nombre"
        )
        return [f[0] for f in cur.fetchall()]


def jurisdicciones() -> list[dict]:
    """Todas las jurisdicciones dadas de alta, con su marca de operativo."""
    with connection.cursor() as cur:
        cur.execute("SELECT nombre, activa FROM mir_c2_jurisdiccion ORDER BY nombre")
        return [{"nombre": n, "en_el_operativo": bool(a)} for n, a in cur.fetchall()]


def cambiar_operativo(nombre: str, en_el_operativo: bool, usuario) -> None:
    """Suma o saca una provincia del operativo. Sólo el administrador."""
    if not puede_administrar(usuario):
        raise circuito.TransicionInvalida(
            "Sólo el administrador nacional define el operativo."
        )
    with connection.cursor() as cur:
        cur.execute("SELECT id FROM mir_c2_jurisdiccion WHERE nombre = %s", [nombre])
        fila = cur.fetchone()
        if fila:
            cur.execute(
                "UPDATE mir_c2_jurisdiccion SET activa = %s WHERE id = %s",
                [1 if en_el_operativo else 0, fila[0]],
            )
        else:
            cur.execute(
                """INSERT INTO mir_c2_jurisdiccion (codigo, nombre, modalidad, activa)
                   VALUES (%s, %s, 'PRESENTACION_PERIODICA', %s)""",
                [nombre.upper()[:20], nombre, 1 if en_el_operativo else 0],
            )


def _ultima_actividad(presentacion_id: int):
    """Lo último que pasó en la presentación: una carga, una corrección, una observación."""
    with connection.cursor() as cur:
        cur.execute(
            """
            SELECT GREATEST(
                COALESCE((SELECT MAX(i.terminada_el) FROM mir_c2_importacion i
                           WHERE i.presentacion_id = s.id), '1000-01-01'),
                COALESCE((SELECT MAX(h.fecha) FROM mir_c2_historial_cambios h
                           JOIN mir_c2_importacion i ON i.id = h.importacion_id
                           WHERE i.presentacion_id = s.id), '1000-01-01'),
                COALESCE((SELECT MAX(GREATEST(o.creada_el, COALESCE(o.respondida_el, o.creada_el)))
                           FROM mir_c2_observacion o WHERE o.presentacion_id = s.id), '1000-01-01'),
                COALESCE(s.cerrada_el, '1000-01-01'),
                COALESCE(s.habilitada_el, '1000-01-01'),
                COALESCE(s.presentada_el, '1000-01-01')
            )
            FROM mir_c2_presentacion s WHERE s.id = %s
            """,
            [presentacion_id],
        )
        fila = cur.fetchone()
    valor = fila[0] if fila else None
    if not valor or str(valor).startswith("1000-01-01"):
        return None
    # GREATEST con fechas en texto devuelve texto: se devuelve como fecha.
    return valor if isinstance(valor, datetime) else datetime.fromisoformat(str(valor))


def situacion(codigo_periodo: str) -> dict:
    """Una fila por provincia del operativo y los totales de arriba."""
    filas = []
    for nombre in operativo():
        estado = svc.estado_de_la_presentacion(nombre, codigo_periodo)
        pres = estado["presentacion"]
        archivos = estado["archivos"]
        importados = sum(1 for a in archivos if a.get("importada"))
        codigo_estado = pres["estado"] if pres else "EN_CARGA"
        if codigo_estado == "EN_CARGA" and not importados:
            codigo_estado = "SIN_EMPEZAR"
        observaciones = circuito.observaciones_de(pres["id"]) if pres else []
        cuenta = {e: 0 for e in ("ABIERTA", "RESPONDIDA", "SUBSANADA")}
        for o in observaciones:
            if o["estado"] in cuenta:
                cuenta[o["estado"]] += 1
        filas.append(
            {
                "jurisdiccion": nombre,
                "presentacion_id": pres["id"] if pres else None,
                "estado": codigo_estado,
                "estado_legible": (
                    "Sin empezar"
                    if codigo_estado == "SIN_EMPEZAR"
                    else circuito.estado_legible(codigo_estado)
                ),
                "archivos_importados": importados,
                "archivos_esperados": len(archivos),
                "faltan": [a["codigo"] for a in archivos if not a.get("importada")],
                "advertencias": sum(
                    (a["importacion"] or {}).get("advertencias") or 0
                    for a in archivos
                    if a.get("importada")
                ),
                "observaciones_abiertas": cuenta["ABIERTA"],
                "observaciones_respondidas": cuenta["RESPONDIDA"],
                "observaciones_subsanadas": cuenta["SUBSANADA"],
                "ultima_actividad": _ultima_actividad(pres["id"]) if pres else None,
            }
        )
    totales = {g: 0 for g in ("presentaron", "en_revision", "cargando", "sin_empezar")}
    for f in filas:
        totales[GRUPOS[f["estado"]]] += 1
    return {"operativo": len(filas), "totales": totales, "filas": filas}


def resumen_de_cierre(codigo_periodo: str) -> list[dict]:
    """Lo que hay y lo que falta, agrupado, para mostrar antes de cerrar el período."""
    grupos = [
        ("PRESENTADA", "Presentaron", ("PRESENTADA", "CONSOLIDADA")),
        ("HABILITADA", "Habilitadas, sin presentar", ("HABILITADA",)),
        (
            "EN_REVISION",
            "En revisión nacional",
            ("CERRADA", "EN_REVISION", "OBSERVADA", "SUBSANADA"),
        ),
        ("EN_CARGA", "Cargando", ("EN_CARGA",)),
        ("SIN_EMPEZAR", "Sin empezar", ("SIN_EMPEZAR",)),
    ]
    filas = situacion(codigo_periodo)["filas"]
    salida = []
    for clave, titulo, estados in grupos:
        del_grupo = [f for f in filas if f["estado"] in estados]
        salida.append(
            {
                "grupo": clave,
                "titulo": titulo,
                "cantidad": len(del_grupo),
                "provincias": [
                    {
                        "jurisdiccion": f["jurisdiccion"],
                        "faltan": (
                            [svc.con_nombres_de_archivo(c) for c in f["faltan"]]
                            if clave == "EN_CARGA"
                            else []
                        ),
                    }
                    for f in del_grupo
                ],
            }
        )
    return salida


def observaciones_del_periodo(
    codigo_periodo: str, jurisdiccion: str | None = None, estado: str | None = None
) -> list[dict]:
    """Todas las observaciones del período, para el seguimiento del nivel nacional."""
    sql = """
        SELECT o.id, o.presentacion_id, o.importacion_id, o.numero_fila, o.campo_id,
               o.identificador_registro, o.texto, o.estado, o.respuesta,
               o.creada_el, o.usuario_observa, o.respondida_el, o.usuario_responde,
               j.nombre AS jurisdiccion, a.codigo AS archivo_codigo,
               c.titulo_esperado AS campo_titulo
        FROM mir_c2_observacion o
        JOIN mir_c2_presentacion s ON s.id = o.presentacion_id
        JOIN mir_c2_periodo p ON p.id = s.periodo_id
        JOIN mir_c2_jurisdiccion j ON j.id = s.jurisdiccion_id
        LEFT JOIN mir_c2_importacion i ON i.id = o.importacion_id
        LEFT JOIN mir_c1_archivo a ON a.id = i.archivo_id
        LEFT JOIN mir_c1_campo c ON c.id = o.campo_id
        WHERE p.codigo = %s
    """
    parametros: list = [codigo_periodo]
    if jurisdiccion:
        sql += " AND j.nombre = %s"
        parametros.append(jurisdiccion)
    if estado:
        sql += " AND o.estado = %s"
        parametros.append(estado)
    sql += " ORDER BY o.estado = 'ABIERTA' DESC, o.creada_el DESC"
    with connection.cursor() as cur:
        cur.execute(sql, parametros)
        filas = _filas(cur)
    for f in filas:
        f["archivo_nombre"] = (
            svc.con_nombres_de_archivo(f["archivo_codigo"])
            if f["archivo_codigo"]
            else ""
        )
    return filas


def historial_de_la_presentacion(presentacion_id: int) -> list[dict]:
    """El historial de cambios de toda la presentación, de las importaciones vigentes."""
    with connection.cursor() as cur:
        cur.execute(
            """
            SELECT h.fecha, h.usuario, h.numero_fila, h.identificador_registro,
                   h.valor_anterior, h.valor_nuevo, h.motivo,
                   a.codigo AS archivo_codigo, c.titulo_esperado AS campo
            FROM mir_c2_historial_cambios h
            JOIN mir_c2_importacion i ON i.id = h.importacion_id
            JOIN mir_c1_archivo a ON a.id = i.archivo_id
            LEFT JOIN mir_c1_campo c ON c.id = h.campo_id
            WHERE i.presentacion_id = %s AND i.estado = 'VALIDA'
            ORDER BY h.fecha DESC, h.id DESC
            """,
            [presentacion_id],
        )
        filas = _filas(cur)
    for f in filas:
        f["archivo_nombre"] = svc.con_nombres_de_archivo(f["archivo_codigo"])
    return filas
