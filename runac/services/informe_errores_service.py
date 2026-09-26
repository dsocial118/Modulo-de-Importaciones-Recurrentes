"""Los dos Excel de una importación. Cada uno tiene un solo trabajo.

1. `archivo_marcado` — **el archivo para corregir.** Es el mismo Excel que se
   subió, con cada problema marcado en su celda: rojo si bloquea, ámbar si
   advierte, y un comentario que dice qué hacer. Abre directo en el primer
   problema. Se corrige ahí y se vuelve a subir tal cual: el importador sólo
   mira las hojas y columnas que espera, así que lo que agregamos no molesta.

2. `planilla_de_errores` — **el informe de la importación.** Para saber qué
   pasó y cómo sigue: una tabla con filtros, un problema por fila, con un
   «Estado» que dice si ya se corrigió en el sistema —por quién y cuándo— y
   que se puede seguir a mano (Pendiente, Corregido, Está bien así, A
   consultar). Es lo que hace falta tener dos archivos: el marcado es una foto
   del Excel que se subió; el informe dice cómo sigue.

Los dos terminan con una solapa «Resumen» —al final: se abre directo en lo que
hay que mirar— con la fecha y hora de la importación, quién la hizo y cuándo se
generó el informe. Rediseñados el 26-09-2026 con el responsable funcional; las
maquetas están en `analisis_funcional\\Maqueta_*.xlsx`.

Ninguno de los dos escribe en la base.
"""

from __future__ import annotations

import io
import os
import re
from datetime import datetime
from typing import Any

from django.db import connection
from openpyxl import Workbook, load_workbook
from openpyxl.comments import Comment
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, Side
from openpyxl.worksheet.datavalidation import DataValidation

from runac.services import excel_estilo as e
from runac.services import plantillas_service

plantilla = plantillas_service.motor_plantilla
en_palabras = plantilla.en_palabras

# Los estados con que se sigue cada problema en el informe. Sólo «Corregido»
# lo pone el sistema; los demás los marca quien lo revisa, en su Excel.
ESTADOS = [
    ("Pendiente", "todavía no se miró", e.PENDIENTE),
    ("Corregido", "se corrigió, en el sistema o en el Excel", e.INFO),
    (
        "Está bien así",
        "se revisó y el dato es correcto aunque la regla lo marque: por ejemplo, una cantidad que supera lo "
        "esperable pero es real",
        e.BIEN,
    ),
    ("A consultar", "hay que preguntarle a alguien antes de decidir", e.ADVERTENCIA),
]


def _filas(cursor) -> list[dict[str, Any]]:
    columnas = [c[0] for c in cursor.description]
    return [dict(zip(columnas, fila)) for fila in cursor.fetchall()]


def datos_de_la_importacion(importacion_id: int) -> dict[str, Any]:
    """Cabecera, problemas, correcciones hechas y las opciones de las listas."""
    with connection.cursor() as cur:
        cur.execute(
            """
            SELECT i.id, i.nombre_archivo, i.ruta_archivo, i.estado, i.usuario,
                   i.filas_leidas, i.filas_incorporadas, i.bloqueantes, i.advertencias,
                   i.iniciada_el, i.archivo_version_id,
                   a.codigo AS archivo_codigo, a.descripcion AS archivo_nombre,
                   av.numero AS version, av.que_es_una_fila,
                   j.nombre AS jurisdiccion, p.codigo AS periodo
            FROM mir_c2_importacion i
            LEFT JOIN mir_c1_archivo a ON a.id = i.archivo_id
            LEFT JOIN mir_c1_archivo_version av ON av.id = i.archivo_version_id
            LEFT JOIN mir_c2_presentacion s ON s.id = i.presentacion_id
            LEFT JOIN mir_c2_jurisdiccion j ON j.id = s.jurisdiccion_id
            LEFT JOIN mir_c2_periodo p ON p.id = s.periodo_id
            WHERE i.id = %s
            """,
            [importacion_id],
        )
        cabecera = _filas(cur)
        if not cabecera:
            return {}
        cabecera = cabecera[0]

        cur.execute(
            """
            SELECT r.nombre_hoja, r.numero_fila, r.columna, r.nombre_campo, r.campo_id,
                   r.severidad, r.codigo, r.valor_encontrado, r.descripcion,
                   r.identificador_registro, r.resuelta, c.catalogo_id
            FROM mir_c2_reglas_incumplidas r
            JOIN mir_c2_importacion i ON i.id = r.importacion_id
            LEFT JOIN mir_c1_campo c ON c.id = r.campo_id
            -- El orden de las hojas lo manda la Capa 1, no el alfabeto. Ordenado
            -- por nombre, el informe abria por CAD y seguia por CRC: el operador
            -- lo recorre contra su Excel, donde las hojas estan en otro orden.
            LEFT JOIN mir_c1_hoja h
                   ON h.archivo_version_id = i.archivo_version_id
                  AND h.nombre_esperado = r.nombre_hoja
            WHERE r.importacion_id = %s
            ORDER BY COALESCE(h.orden_procesamiento, 99), r.nombre_hoja,
                     r.numero_fila, r.columna
            """,
            [importacion_id],
        )
        reglas = _filas(cur)

        cur.execute(
            """
            SELECT tipo, hoja, numero_fila, esperado, encontrado, descripcion
            FROM mir_c2_errores_de_importacion
            WHERE importacion_id = %s ORDER BY id
            """,
            [importacion_id],
        )
        archivo = _filas(cur)

        # Lo que el motor haya encontrado en una hoja de referencia no se
        # informa: esas hojas no se validan desde el 26-09-2026 (#87), y las
        # importaciones anteriores tienen hallazgos guardados en ellas.
        cur.execute(
            "SELECT nombre_esperado FROM mir_c1_hoja WHERE archivo_version_id = %s AND referencia",
            [cabecera["archivo_version_id"]],
        )
        referencia = {fila[0] for fila in cur.fetchall()}
        reglas = [r for r in reglas if r["nombre_hoja"] not in referencia]
        archivo = [a for a in archivo if a["hoja"] not in referencia]

        cur.execute(
            """
            SELECT numero_fila, campo_id, valor_anterior, valor_nuevo, usuario, fecha
            FROM mir_c2_historial_cambios WHERE importacion_id = %s ORDER BY id
            """,
            [importacion_id],
        )
        cambios = {(h["numero_fila"], h["campo_id"]): h for h in _filas(cur)}

        opciones: dict[int, list[str]] = {}
        catalogos = {r["catalogo_id"] for r in reglas if r["catalogo_id"]}
        if catalogos:
            cur.execute(
                "SELECT catalogo_id, valor_esperado FROM mir_c1_catalogo_opcion "
                "WHERE activo = 1 AND catalogo_id IN ("
                + ",".join(["%s"] * len(catalogos))
                + ") "
                "ORDER BY catalogo_id, orden, id",
                list(catalogos),
            )
            for fila in _filas(cur):
                opciones.setdefault(fila["catalogo_id"], []).append(
                    fila["valor_esperado"]
                )

    return {
        "cabecera": cabecera,
        "reglas": reglas,
        "archivo": archivo,
        "cambios": cambios,
        "opciones": opciones,
    }


# ---------------------------------------------------------------------------
# Lo que comparten los dos
# ---------------------------------------------------------------------------


def _inofensivo(valor):
    """Un texto que Excel no va a interpretar como fórmula.

    Todo lo que sale a estos informes viene de un archivo que subió una
    provincia. Excel trata como fórmula cualquier celda que empiece con `=`,
    `+`, `-` o `@`, así que un valor como `=HYPERLINK(...)` escrito en la
    planilla se ejecutaría en la máquina de quien abre el informe. Se marcan
    esas celdas como texto explícito y el valor se muestra tal cual vino: es un
    informe de lo que el archivo decía, y eso incluye lo que decía mal.
    """
    if isinstance(valor, str) and valor[:1] in ("=", "+", "-", "@"):
        return ("texto", valor)
    return (None, valor)


def _celda(hoja, fila: int, columna: int, valor):
    """Escribe una celda sin dejar que su contenido se convierta en fórmula."""
    formato, contenido = _inofensivo(valor)
    celda = hoja.cell(row=fila, column=columna, value=contenido)
    if formato == "texto":
        celda.data_type = "s"
        celda.quotePrefix = True
    return celda


def _que_hacer(regla: dict, opciones: dict) -> str:
    return en_palabras.problema_en_palabras(
        regla["codigo"], regla["descripcion"], opciones.get(regla.get("catalogo_id"))
    )


def _base_del_nombre(cabecera: dict) -> str:
    return os.path.splitext(
        cabecera.get("nombre_archivo") or f'importacion_{cabecera["id"]}'
    )[0]


def _resumen(
    wb,
    cab,
    titulo,
    para_que,
    conteo,
    tarjetas,
    notas,
    generado,
    vinculos=None,
    ultima="Ir al primero",
):
    """La solapa «Resumen»: de qué importación se trata y qué tipo de problemas trae."""
    ws = wb.create_sheet("Resumen")
    for col, ancho in zip("BCDEFG", (24, 16, 16, 16, 16, 16)):
        ws.column_dimensions[col].width = ancho
    e.portada(
        ws,
        titulo,
        f'{cab["archivo_codigo"]} · {cab.get("archivo_nombre") or ""} · {cab["jurisdiccion"]} · {cab["periodo"]}',
        para_que,
    )
    e.tarjetas(ws, 7, tarjetas)
    incorporo = cab["estado"] == "VALIDA"
    datos = [
        (
            "Resultado",
            (
                f'Se incorporaron las {cab["filas_incorporadas"]} filas.'
                if incorporo
                else "No se incorporó ninguna fila: hay errores bloqueantes."
            ),
        ),
        ("Nombre recibido", cab["nombre_archivo"]),
        ("Versión de la estructura", f'v{cab["version"]}'),
        ("Importado el", e.ahora_legible(cab["iniciada_el"])),
        ("Importado por", cab.get("usuario")),
        ("Informe generado el", e.ahora_legible(generado)),
    ]
    fila = 10
    for etiqueta, valor in datos:
        ws.cell(row=fila, column=2, value=etiqueta).font = e.fuente(
            size=10, color=e.TINTA2
        )
        c = _celda(ws, fila, 3, valor)
        c.font = e.fuente(size=10, color=e.TINTA, bold=etiqueta == "Resultado")
        ws.merge_cells(start_row=fila, start_column=3, end_row=fila, end_column=7)
        fila += 1

    fila += 1
    ws.cell(row=fila, column=2, value="Qué tipo de problemas hay").font = e.fuente(
        size=12, bold=True, color=e.TINTA
    )
    fila += 1
    for col, texto in ((2, "Problema"), (5, "Gravedad"), (6, "Cantidad"), (7, ultima)):
        ws.cell(row=fila, column=col, value=texto).font = e.fuente(
            size=9, bold=True, color="FFFFFF"
        )
    for col in range(2, 8):
        ws.cell(row=fila, column=col).fill = e.relleno(e.NAV)
    ws.merge_cells(start_row=fila, start_column=2, end_row=fila, end_column=4)
    if not conteo:
        fila += 1
        ws.cell(row=fila, column=2, value="El archivo no registró problemas.").font = (
            e.fuente(size=10, color=e.TINTA)
        )
    for tipo, gravedad, cantidad, ultimo in conteo:
        fila += 1
        ws.cell(row=fila, column=2, value=tipo)
        ws.merge_cells(start_row=fila, start_column=2, end_row=fila, end_column=4)
        ws.cell(row=fila, column=6, value=cantidad)
        ws.cell(row=fila, column=7, value=ultimo)
        for col in range(2, 8):
            c = ws.cell(row=fila, column=col)
            c.font = e.fuente(size=10, color=e.TINTA)
            c.border = Border(bottom=Side(style="thin", color=e.LINEA))
        g = ws.cell(row=fila, column=5, value=en_palabras.GRAVEDAD[gravedad])
        e.etiqueta(g, e.POR_GRAVEDAD[gravedad])
        if vinculos and vinculos.get(tipo):
            ws.cell(row=fila, column=7).hyperlink = vinculos[tipo]
            ws.cell(row=fila, column=7).font = e.fuente(
                size=10, color=e.TEAL, underline="single"
            )
        for col in (6, 7):
            ws.cell(row=fila, column=col).alignment = Alignment(horizontal="center")

    fila += 2
    for etiqueta, texto in notas:
        ws.cell(row=fila, column=2, value=etiqueta).font = e.fuente(
            size=10, bold=True, color=e.TINTA
        )
        c = ws.cell(row=fila, column=3, value=texto)
        c.font = e.fuente(size=10, color=e.TINTA2)
        c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.merge_cells(start_row=fila, start_column=3, end_row=fila, end_column=7)
        e.alto_para(ws, fila, [texto], 75)
        fila += 1
    e.para_imprimir(
        ws, f'MIR · {cab["archivo_codigo"]} · {cab["jurisdiccion"]} · {cab["periodo"]}'
    )
    return ws


def _ordenado(conteo: dict) -> list:
    """Primero lo que bloquea, y dentro de cada gravedad lo más frecuente."""
    return sorted(conteo.items(), key=lambda kv: (kv[0][1] != "BLOQUEANTE", -kv[1][0]))


# ---------------------------------------------------------------------------
# 1. El informe de la importación
# ---------------------------------------------------------------------------


def planilla_de_errores(importacion_id: int, generado: datetime | None = None) -> bytes:
    """El informe: un problema por fila, con su estado, y el resumen al final."""
    datos = datos_de_la_importacion(importacion_id)
    if not datos:
        return b""
    return armar_informe(datos, generado or datetime.now())


def nombre_del_informe(importacion_id: int) -> str:
    datos = datos_de_la_importacion(importacion_id)
    return f'{_base_del_nombre(datos["cabecera"])}_INFORME.xlsx' if datos else ""


def armar_informe(datos: dict, generado: datetime) -> bytes:
    cab = datos["cabecera"]
    wb = Workbook()
    ws = wb.active
    ws.title = "Problemas"
    fila_de = cab.get("que_es_una_fila") or "Registro"
    e.encabezado(
        ws,
        [
            "Hoja",
            "Fila",
            "Celda",
            fila_de,
            "Campo",
            "Valor",
            "Gravedad",
            "Qué hay que hacer",
            "Estado",
            "Corrección en el sistema",
        ],
        [12, 6, 7, 30, 28, 16, 12, 52, 15, 32],
    )
    ayuda = Comment(
        "Para seguir cada problema. Se puede cambiar:\n\n"
        + "\n".join(f"· {estado}: {que}." for estado, que, _ in ESTADOS)
        + "\n\nLo que se marca acá queda en este Excel. Lo que se corrige en el sistema llega marcado «Corregido».",
        "MIR",
    )
    ayuda.width, ayuda.height = 380, 250
    ws["I1"].comment = ayuda

    conteo: dict = {}
    corregidos = 0
    filas = [
        {
            "hoja": r["nombre_hoja"],
            "fila": r["numero_fila"],
            "celda": f'{r["columna"] or ""}{r["numero_fila"] or ""}',
            "quien": r["identificador_registro"] or "—",
            "campo": r["nombre_campo"],
            "valor": en_palabras.fecha_legible(r["valor_encontrado"]),
            "gravedad": r["severidad"],
            "que": _que_hacer(r, datos["opciones"]),
            "resuelta": bool(r["resuelta"]),
            "cambio": datos["cambios"].get((r["numero_fila"], r["campo_id"])),
        }
        for r in datos["reglas"]
    ] + [
        # Los problemas del archivo entero, como una fila vacía en el medio.
        {
            "hoja": a["hoja"],
            "fila": a["numero_fila"],
            "celda": f'A{a["numero_fila"]}' if a["numero_fila"] else "",
            "quien": "—",
            "campo": "—",
            "valor": a["encontrado"],
            "gravedad": "BLOQUEANTE",
            "que": en_palabras.problema_en_palabras(a["tipo"], a["descripcion"]),
            "resuelta": False,
            "cambio": None,
        }
        for a in datos["archivo"]
    ]
    for f in filas:
        cambio = f["cambio"]
        corregidos += f["resuelta"]
        # La fila se calcula: `append([])` no avanza sobre una fila sin celdas,
        # y cada problema pisaba al anterior.
        n = ws.max_row + 1
        valores = [
            f["hoja"],
            f["fila"],
            f["celda"],
            f["quien"],
            f["campo"],
            f["valor"] if f["valor"] not in (None, "") else "(vacío)",
            en_palabras.GRAVEDAD[f["gravedad"]],
            f["que"],
            "Corregido" if f["resuelta"] else "Pendiente",
            (
                (
                    f'{cambio["valor_anterior"]} → {cambio["valor_nuevo"]} · {cambio["usuario"]} · '
                    f'{e.ahora_legible(cambio["fecha"])}'
                )
                if f["resuelta"] and cambio
                else ""
            ),
        ]
        for col, valor in enumerate(valores, start=1):
            e.cuerpo(_celda(ws, n, col, valor))
        for col in (2, 3):
            ws.cell(row=n, column=col).alignment = Alignment(
                horizontal="center", vertical="top"
            )
        e.etiqueta(ws.cell(row=n, column=7), e.POR_GRAVEDAD[f["gravedad"]])
        e.alto_para(ws, n, [f["que"], f["quien"], f["campo"]], 50)
        clave = (en_palabras.tipo_de_problema(f["que"]), f["gravedad"])
        total, pendientes = conteo.get(clave, (0, 0))
        conteo[clave] = (total + 1, pendientes + (0 if f["resuelta"] else 1))

    ultima = max(ws.max_row, 2)
    # El estado es un desplegable, y su color lo sigue aunque se lo cambie a mano.
    rango = f"I2:I{ultima + 300}"
    dv = DataValidation(
        type="list",
        formula1='"' + ",".join(s for s, _, _ in ESTADOS) + '"',
        allow_blank=True,
    )
    dv.error, dv.errorTitle = "Elegí un estado de la lista.", "Estado"
    ws.add_data_validation(dv)
    dv.add(rango)
    for estado, _, tono in ESTADOS:
        ws.conditional_formatting.add(
            rango,
            FormulaRule(
                formula=[f'$I2="{estado}"'],
                fill=e.relleno(tono["sup"]),
                font=Font(name=e.LETRA, bold=True, color=tono["tin"]),
            ),
        )
    ws.auto_filter.ref = f"A1:J{ultima}"
    e.para_imprimir(
        ws,
        f'MIR · Informe {cab["archivo_codigo"]} · {cab["jurisdiccion"]} · {cab["periodo"]}',
        "1:1",
    )

    total = len(filas)
    _resumen(
        wb,
        cab,
        "Informe de la importación",
        "Para saber qué pasó y cómo sigue: cada problema y su estado. Para arreglar el Excel se usa el «Archivo "
        "para corregir».",
        [(t, g, tot, pend) for (t, g), (tot, pend) in _ordenado(conteo)],
        [
            ("Filas", cab["filas_leidas"] or 0, e.PENDIENTE),
            (
                "Bloqueantes",
                sum(1 for f in filas if f["gravedad"] == "BLOQUEANTE"),
                e.BLOQUEANTE,
            ),
            (
                "Advertencias",
                sum(1 for f in filas if f["gravedad"] == "ADVERTENCIA"),
                e.ADVERTENCIA,
            ),
            ("Corregidas", corregidos, e.INFO),
            ("Pendientes", total - corregidos, e.PENDIENTE),
        ],
        [(estado, que[0].upper() + que[1:] + ".") for estado, que, _ in ESTADOS],
        generado,
        ultima="Pendientes",
    )
    wb.active = 0
    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


# ---------------------------------------------------------------------------
# 2. El archivo para corregir
# ---------------------------------------------------------------------------


def archivo_marcado(
    importacion_id: int, generado: datetime | None = None
) -> tuple[bytes, str]:
    """El Excel que se subió, con los problemas marcados. (b"", "") si no se conserva."""
    datos = datos_de_la_importacion(importacion_id)
    if not datos:
        return b"", ""
    cab = datos["cabecera"]
    ruta = cab.get("ruta_archivo")
    if not ruta or not os.path.exists(ruta):
        return b"", ""
    with connection.cursor() as cursor:
        definicion = plantilla.leer_definicion(
            plantillas_service._CursorConNombres(cursor),
            cab["archivo_codigo"],
            cab["archivo_version_id"],
        )
    contenido = armar_archivo_para_corregir(
        load_workbook(ruta), datos, definicion, generado or datetime.now()
    )
    return contenido, f"{_base_del_nombre(cab)}_PARA_CORREGIR.xlsx"


def armar_archivo_para_corregir(
    libro, datos: dict, definicion: dict, generado: datetime
) -> bytes:
    cab = datos["cabecera"]
    hojas = {h["nombre_esperado"]: h for h in definicion["hojas"]}
    referencia = {n for n, h in hojas.items() if h.get("referencia")}

    # Quedan las hojas que pide el archivo y la de listas (sin ella no andan
    # los desplegables). Lo que se agregó, fuera; las de referencia, ocultas.
    for nombre in list(libro.sheetnames):
        if nombre in referencia:
            libro[nombre].sheet_state = "hidden"
        elif nombre not in hojas and nombre.lower() != "listas":
            del libro[nombre]
    # «Listas» sin mayúsculas, como en las plantillas nuevas. openpyxl compara
    # los nombres sin mayúsculas, así que se pasa por uno intermedio; y se
    # actualizan los desplegables que la nombran.
    if "LISTAS" in libro.sheetnames:
        libro["LISTAS"].title = "listas_tmp"
        libro["listas_tmp"].title = "Listas"
        for ws in libro.worksheets:
            for dv in ws.data_validations.dataValidation:
                if dv.formula1:
                    dv.formula1 = dv.formula1.replace("LISTAS", "Listas")

    # El título de cada columna explica qué va: lo que antes decía la hoja de
    # instrucciones, ahora en el comentario, con las mismas palabras que el
    # instructivo. Los colores de la plantilla no se tocan.
    for nombre, hoja in hojas.items():
        if nombre in referencia or nombre not in libro.sheetnames:
            continue
        ws = libro[nombre]
        for campo in hoja["campos"]:
            celda = ws.cell(row=hoja["fila_encabezados"], column=campo["orden"])
            celda.comment = plantilla._comentario_del_campo(
                campo, definicion.get("titulos")
            )

    por_celda: dict = {}
    for r in datos["reglas"]:
        if (
            r["nombre_hoja"] in libro.sheetnames
            and r["nombre_hoja"] not in referencia
            and r["columna"]
            and r["numero_fila"]
        ):
            por_celda.setdefault(
                (r["nombre_hoja"], f'{r["columna"]}{r["numero_fila"]}'), []
            ).append(r)

    primero, conteo, vinculos = None, {}, {}
    for (nombre, ref), rs in por_celda.items():
        ws = libro[nombre]
        gravedad = (
            "BLOQUEANTE"
            if any(r["severidad"] == "BLOQUEANTE" for r in rs)
            else "ADVERTENCIA"
        )
        tono = e.POR_GRAVEDAD[gravedad]
        try:
            c = ws[ref]
        except (ValueError, KeyError):
            continue
        c.fill = e.relleno(tono["sup"])
        c.font = Font(name=c.font.name, size=c.font.size, bold=True, color=tono["tin"])
        lado = Side(style="thin", color=tono["bor"])
        c.border = Border(left=lado, right=lado, top=lado, bottom=lado)
        texto = "\n\n".join(
            f'{en_palabras.GRAVEDAD[r["severidad"]]}\n{_que_hacer(r, datos["opciones"])}'
            for r in rs
        )
        comentario = Comment(texto, "MIR")
        comentario.width, comentario.height = 300, 90 + 55 * (len(rs) - 1)
        c.comment = comentario
        primero = primero or (nombre, ref)
        for r in rs:
            clave = (
                en_palabras.tipo_de_problema(_que_hacer(r, datos["opciones"])),
                r["severidad"],
            )
            conteo[clave] = conteo.get(clave, 0) + 1
            vinculos.setdefault(clave[0], f"#'{nombre}'!{ref}")

    for a in datos["archivo"]:
        if (
            a["hoja"] in libro.sheetnames
            and a["hoja"] not in referencia
            and a["numero_fila"]
        ):
            ws = libro[a["hoja"]]
            for col in range(1, min(ws.max_column, 80) + 1):
                ws.cell(row=a["numero_fila"], column=col).fill = e.relleno(
                    e.BLOQUEANTE["sup"]
                )
            que = en_palabras.problema_en_palabras(a["tipo"], a["descripcion"])
            comentario = Comment(f"Bloqueante\n{que}", "MIR")
            comentario.width, comentario.height = 300, 90
            ws.cell(row=a["numero_fila"], column=1).comment = comentario
            clave = (en_palabras.tipo_de_problema(que), "BLOQUEANTE")
            conteo[clave] = conteo.get(clave, 0) + 1
            vinculos.setdefault(clave[0], f"#'{a['hoja']}'!A{a['numero_fila']}")
            primero = primero or (a["hoja"], f'A{a["numero_fila"]}')

    bloqueantes = sum(n for (_, g), n in conteo.items() if g == "BLOQUEANTE")
    advertencias = sum(n for (_, g), n in conteo.items() if g == "ADVERTENCIA")
    _resumen(
        libro,
        cab,
        "Archivo para corregir",
        "Es el mismo Excel que se subió, con cada problema marcado en su celda. Pasá el mouse sobre la celda para "
        "ver qué corregir y, después, volvé a subirlo tal cual.",
        [
            (t, g, n, "Ver")
            for (t, g), n in sorted(
                conteo.items(), key=lambda kv: (kv[0][1] != "BLOQUEANTE", -kv[1])
            )
        ],
        [
            ("Filas", cab["filas_leidas"] or 0, e.PENDIENTE),
            ("Bloqueantes", bloqueantes, e.BLOQUEANTE),
            ("Advertencias", advertencias, e.ADVERTENCIA),
        ],
        [
            (
                "Colores de las celdas",
                "Rojo: bloqueante, impide la importación. Ámbar: advertencia, no la impide.",
            ),
            (
                "Colores de los títulos",
                "Celeste: dato obligatorio. Gris: opcional. Pasá el mouse por un título para "
                "ver qué va, los valores posibles y los controles.",
            ),
        ],
        generado,
        vinculos=vinculos,
    )

    # Abre en el primer problema. Lo que se desplaza es el panel de abajo: la
    # vista general no se toca, o se corre lo inmovilizado.
    if primero:
        nombre, ref = primero
        libro.active = libro.sheetnames.index(nombre)
        vista = libro[nombre].sheet_view
        fila = int(re.sub(r"\D", "", ref))
        if vista.pane:
            vista.pane.topLeftCell = (
                f"A{max(fila - 4, hojas[nombre]['fila_encabezados'] + 1)}"
            )
        for seleccion in vista.selection:
            seleccion.activeCell = seleccion.sqref = ref
    else:
        libro.active = libro.sheetnames.index("Resumen")
    for ws in libro.worksheets:
        ws.sheet_view.tabSelected = ws is libro.active

    buffer = io.BytesIO()
    libro.save(buffer)
    return buffer.getvalue()
