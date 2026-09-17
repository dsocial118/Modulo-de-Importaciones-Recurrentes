"""Genera el código DBML para pegar en https://dbdiagram.io

    python dbml.py --salida <archivo.dbml> [--capas 1,2,3] [--incluir-receptoras]

Lee la estructura real de la base de trabajo, así el diagrama siempre refleja
lo que hay y no lo que creemos que hay.

Por defecto NO incluye las tablas receptoras generadas
(mir_c2_<archivo>_v<n>[_<hoja>]): son decenas de tablas con hasta 64 columnas
cada una y harían el diagrama ilegible. Se agregan con --incluir-receptoras.
"""

from __future__ import annotations

import argparse
import os
import re

import mysql.connector

CONEXION = dict(
    host=os.environ.get("RUNAC_DB_HOST", "mysql"),
    port=3306,
    user="root",
    password="runac_local",
    database="runac",
)

GRUPOS = {
    "1": ("Capa 1 — definición de los archivos", "mir_c1_"),
    "2": ("Capa 2 — importación y staging", "mir_c2_"),
    "3": ("Capa 3 — base consolidada", "mir_c3_"),
}


def escapar(texto: str | None) -> str:
    if not texto:
        return ""
    t = str(texto).replace("\\", "\\\\").replace("'", "\\'").replace("\n", " ").strip()
    return t


def tipo_dbml(column_type: str) -> str:
    """dbdiagram entiende los tipos de MySQL casi tal cual; se limpia el ruido."""
    t = column_type
    t = re.sub(r"\s+unsigned|\s+zerofill", "", t, flags=re.I)
    if t.startswith("enum("):
        return t  # dbdiagram lo muestra como está
    return t


def main():
    p = argparse.ArgumentParser(description="Genera el DBML del modelo de RUNAC.")
    p.add_argument("--salida", default="/trabajo/capa1/DER_runac.dbml")
    p.add_argument("--capas", default="1,2,3")
    p.add_argument("--incluir-receptoras", action="store_true")
    args = p.parse_args()
    capas = [c.strip() for c in args.capas.split(",")]
    prefijos = tuple(GRUPOS[c][1] for c in capas if c in GRUPOS)

    cn = mysql.connector.connect(**CONEXION)
    cur = cn.cursor(dictionary=True)

    cur.execute(
        """
        SELECT TABLE_NAME, TABLE_COMMENT FROM information_schema.TABLES
        WHERE TABLE_SCHEMA = 'runac' ORDER BY TABLE_NAME
    """
    )
    tablas = []
    for t in cur.fetchall():
        n = t["TABLE_NAME"]
        if not n.startswith(prefijos):
            continue
        # Las receptoras se reconocen por llevar la versión en el nombre
        # (mir_c2_<archivo>_v<n>[_<hoja>]); las de control, no.
        if not args.incluir_receptoras and re.search(r"^mir_c2_.+_v\d+(_.+)?$", n):
            continue
        tablas.append(t)
    nombres = {t["TABLE_NAME"] for t in tablas}

    cur.execute(
        """
        SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_KEY,
               EXTRA, COLUMN_COMMENT, ORDINAL_POSITION, COLUMN_DEFAULT
        FROM information_schema.COLUMNS WHERE TABLE_SCHEMA='runac'
        ORDER BY TABLE_NAME, ORDINAL_POSITION
    """
    )
    columnas: dict[str, list] = {}
    for c in cur.fetchall():
        columnas.setdefault(c["TABLE_NAME"], []).append(c)

    cur.execute(
        """
        SELECT k.TABLE_NAME, k.COLUMN_NAME, k.REFERENCED_TABLE_NAME, k.REFERENCED_COLUMN_NAME
        FROM information_schema.KEY_COLUMN_USAGE k
        WHERE k.TABLE_SCHEMA='runac' AND k.REFERENCED_TABLE_NAME IS NOT NULL
        ORDER BY k.TABLE_NAME, k.COLUMN_NAME
    """
    )
    fks = [
        f
        for f in cur.fetchall()
        if f["TABLE_NAME"] in nombres and f["REFERENCED_TABLE_NAME"] in nombres
    ]

    cur.execute(
        """
        SELECT TABLE_NAME, INDEX_NAME, GROUP_CONCAT(COLUMN_NAME ORDER BY SEQ_IN_INDEX) AS COLS
        FROM information_schema.STATISTICS
        WHERE TABLE_SCHEMA='runac' AND NON_UNIQUE=0 AND INDEX_NAME <> 'PRIMARY'
        GROUP BY TABLE_NAME, INDEX_NAME
    """
    )
    unicos: dict[str, list] = {}
    for i in cur.fetchall():
        unicos.setdefault(i["TABLE_NAME"], []).append(i)

    lineas: list[str] = []
    w = lineas.append

    w("// ===========================================================================")
    w("// RUNAC — modelo de datos")
    w("// Generado desde la base de trabajo. Pegar en https://dbdiagram.io")
    w("// ===========================================================================")
    w("")
    w("Project RUNAC {")
    w("  database_type: 'MySQL'")
    w("  Note: '''")
    w(
        "    Registro Único Nacional de Medidas de Protección y Medidas Penales Juveniles."
    )
    w("")
    w("    Capa 1: describe los archivos que se esperan recibir. Metadatos, no datos.")
    w(
        "    Capa 2: recibe las importaciones. Sus tablas receptoras se GENERAN leyendo la Capa 1."
    )
    w("    Capa 3: base consolidada. Modela la realidad, no el Excel.")
    w("  '''")
    w("}")
    w("")

    for t in tablas:
        nombre = t["TABLE_NAME"]
        w(f"Table {nombre} {{")
        for c in columnas.get(nombre, []):
            partes = []
            if c["COLUMN_KEY"] == "PRI":
                partes.append("pk")
            if "auto_increment" in (c["EXTRA"] or ""):
                partes.append("increment")
            if c["IS_NULLABLE"] == "NO" and c["COLUMN_KEY"] != "PRI":
                partes.append("not null")
            es_unica = any(
                u["COLS"] == c["COLUMN_NAME"] for u in unicos.get(nombre, [])
            )
            if es_unica:
                partes.append("unique")
            if c["COLUMN_COMMENT"]:
                partes.append(f"note: '{escapar(c['COLUMN_COMMENT'])}'")
            sufijo = f" [{', '.join(partes)}]" if partes else ""
            w(f'  {c["COLUMN_NAME"]} {tipo_dbml(c["COLUMN_TYPE"])}{sufijo}')

        compuestos = [u for u in unicos.get(nombre, []) if "," in u["COLS"]]
        if compuestos:
            w("")
            w("  indexes {")
            for u in compuestos:
                w(f'    ({u["COLS"]}) [unique]')
            w("  }")

        if t["TABLE_COMMENT"]:
            w("")
            w(f"  Note: '{escapar(t['TABLE_COMMENT'])}'")
        w("}")
        w("")

    w("// --- relaciones ---")
    for f in fks:
        w(
            f'Ref: {f["TABLE_NAME"]}.{f["COLUMN_NAME"]} > '
            f'{f["REFERENCED_TABLE_NAME"]}.{f["REFERENCED_COLUMN_NAME"]}'
        )
    w("")

    w("// --- agrupación visual ---")
    for c in capas:
        if c not in GRUPOS:
            continue
        titulo, prefijo = GRUPOS[c]
        del_grupo = [
            t["TABLE_NAME"] for t in tablas if t["TABLE_NAME"].startswith(prefijo)
        ]
        if not del_grupo:
            continue
        w(f'TableGroup "{titulo}" {{')
        for n in del_grupo:
            w(f"  {n}")
        w("}")
        w("")

    os.makedirs(os.path.dirname(args.salida), exist_ok=True)
    with open(args.salida, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lineas))

    print(f"dbml: {args.salida}")
    print(f"  tablas:     {len(tablas)}")
    print(f"  relaciones: {len(fks)}")
    cur.close()
    cn.close()


if __name__ == "__main__":
    main()
