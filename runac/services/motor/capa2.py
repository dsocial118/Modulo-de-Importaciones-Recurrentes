"""Genera TODA la Capa 2 leyendo la Capa 1.

    python capa2.py <carpeta_capa1> --periodo 2026_T1 [--archivos MPI,MPE] [--aplicar]

Produce un único .sql con:

  1. las tablas fijas de control (jurisdicción, período, período-archivo,
     presentación, importación, errores de importación, reglas incumplidas,
     observación, historial de cambios), iguales para cualquier archivo y para
     cualquier proyecto de importación;

  2. las tablas receptoras de cada hoja de cada archivo, generadas leyendo la
     Capa 1: UNA por hoja y versión de estructura.

Una sola tabla receptora y no dos: como la importación es restrictiva, un
archivo con errores bloqueantes no entra, así que todo dato incorporado pudo
convertirse a su tipo. El valor que provocó cada incumplimiento queda en
runac_c2_reglas_incumplidas, y los valores previos a cada corrección en
runac_c2_historial_cambios.

Nada de esto se escribe a mano. Si cambia la Capa 1, se vuelve a correr.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime

from comun import abrev, nombre_tabla_receptora, sql_texto as q

# Tablas fijas de control, en orden inverso de dependencia (para el DROP).
TABLAS_CONTROL = [
    "runac_c2_historial_cambios",
    "runac_c2_observacion",
    "runac_c2_reglas_incumplidas",
    "runac_c2_errores_de_importacion",
    "runac_c2_importacion",
    "runac_c2_presentacion",
    "runac_c2_periodo_archivo",
    "runac_c2_periodo",
    "runac_c2_jurisdiccion",
]


def tipo_sql(campo: dict) -> str:
    t = campo["tipo_dato"]
    if t == "FECHA":
        return "date"
    if t == "HORA":
        return "time"
    if t == "ENTERO":
        return "bigint"
    if t == "DECIMAL":
        return "decimal(18,4)"
    # El comentario de runac_c1_campo.longitud_maxima lo dice: sin longitud,
    # la columna receptora se crea como TEXT.
    return (
        f'varchar({campo["longitud_maxima"]})'
        if campo.get("longitud_maxima")
        else "text"
    )


def tablas_receptoras(
    mapa: dict, codigo: str, periodo: str, version: int, salida: list
) -> list[dict]:
    w = salida.append
    generadas = []
    varias = len(mapa["hojas"]) > 1

    for h in mapa["hojas"]:
        tabla = nombre_tabla_receptora(codigo, h["nombre"], varias, version)
        firma = "|".join(
            f'{c["orden"]}:{c["nombre_tecnico"]}:{c["tipo_dato"]}:{c.get("longitud_maxima") or ""}'
            for c in h["columnas"]
        )
        huella = hashlib.sha1(firma.encode("utf-8")).hexdigest()

        w("-- ------------------------------------------------------------------")
        w(
            f'-- {codigo} v{version} / hoja "{h["nombre"]}" — {len(h["columnas"])} columnas'
        )
        w(f"-- huella de la estructura: {huella[:16]}")
        w("-- ------------------------------------------------------------------")
        w(f"DROP TABLE IF EXISTS `{tabla}`;")
        w(f"CREATE TABLE `{tabla}` (")
        w("  `id` bigint PRIMARY KEY AUTO_INCREMENT COMMENT 'Identificador interno.',")
        w(
            "  `importacion_id` bigint NOT NULL COMMENT 'Importación a la que pertenece la fila.',"
        )
        w(
            "  `numero_fila` int NOT NULL COMMENT 'Número de fila en el Excel, tal como lo ve quien completa la planilla.',"
        )
        w(
            "  `estado` ENUM('VALIDA','CON_ADVERTENCIA','EDITADA') NOT NULL DEFAULT 'VALIDA' "
            "COMMENT 'Resultado de la validación de la fila. Las filas con bloqueantes no llegan a incorporarse.',"
        )
        w(
            "  `hash_contenido` char(40) COMMENT 'Huella del contenido, para detectar duplicados exactos y cambios entre períodos.',"
        )
        for c in h["columnas"]:
            com = f'{c["letra"]} — {c["titulo"]}' + (
                " (valor de catálogo)" if c.get("catalogo_huella") else ""
            )
            nulo = "NOT NULL" if c.get("obligatorio") else "NULL"
            w(f'  `{c["nombre_tecnico"]}` {tipo_sql(c)} {nulo} COMMENT {q(com[:255])},')
        w(f"  UNIQUE KEY `{abrev(tabla, 50)}_fila` (`importacion_id`, `numero_fila`)")
        comentario_tabla = (
            f'Datos de {codigo} v{version}, hoja "{h["nombre"]}". Generada desde la Capa 1. '
            "salidaólo entran filas que superaron las validaciones bloqueantes."
        )
        w(f") COMMENT = {q(comentario_tabla[:1000])};")
        w("")
        w(
            f"ALTER TABLE `{tabla}` ADD FOREIGN KEY (`importacion_id`) REFERENCES `runac_c2_importacion` (`id`);"
        )
        w("")
        generadas.append(
            {
                "codigo": codigo,
                "hoja": h["nombre"],
                "tabla": tabla,
                "columnas": len(h["columnas"]),
                "huella": huella,
            }
        )
    return generadas


def registrar_periodo_archivo(
    codigos: list[str], periodo: str, version: int, salida: list
) -> None:
    """Qué versión de cada archivo rige en el período. Una fila por archivo,
    no por hoja: el versionado es por archivo."""
    w = salida.append
    w("-- ------------------------------------------------------------------")
    w("-- Qué versión de cada archivo rige en este período.")
    w("-- Si el período siguiente no tiene cambios, apunta a las mismas")
    w("-- versiones y no se duplica ninguna definición.")
    w("-- ------------------------------------------------------------------")
    for codigo in codigos:
        w("INSERT INTO runac_c2_periodo_archivo (periodo_id, archivo_version_id)")
        w("  SELECT p.id, av.id")
        w("    FROM runac_c2_periodo p, runac_c1_archivo a")
        w("    JOIN runac_c1_archivo_version av ON av.archivo_id = a.id")
        w(
            f"   WHERE p.codigo = {q(periodo)} AND a.codigo = {q(codigo)} AND av.numero = {version}"
        )
        w("  ON DUPLICATE KEY UPDATE periodo_id = VALUES(periodo_id);")
    w("")


def main():
    p = argparse.ArgumentParser(
        description="Genera la Capa 2 completa desde la Capa 1."
    )
    p.add_argument("base")
    p.add_argument("--periodo", default="2026_T1")
    p.add_argument("--version", type=int, default=1)
    p.add_argument("--archivos", default=None)
    p.add_argument("--aplicar", action="store_true")
    args = p.parse_args()

    dir_mapas = os.path.join(args.base, "mapas")
    if args.archivos:
        codigos = [c.strip() for c in args.archivos.split(",") if c.strip()]
    else:
        codigos = sorted(
            f.replace(".mapa.json", "")
            for f in os.listdir(dir_mapas)
            if f.endswith(".mapa.json")
        )

    ruta_control = os.path.join(args.base, "..", "sql", "03_schema_capa2_control.sql")
    with open(ruta_control, encoding="utf-8") as fh:
        control = fh.read()

    salida: list[str] = []
    w = salida.append
    anio = int(args.periodo[:4])
    m = re.search(r"T(\d)", args.periodo)
    numero = int(m.group(1)) if m else 1

    w("-- ===========================================================================")
    w(
        f'-- Capa 2 completa — generada el {datetime.now().isoformat(timespec="seconds").replace("T", " ")}'
    )
    w(f"-- Período {args.periodo}, versión de estructura {args.version}.")
    w(f'-- Archivos: {", ".join(codigos)}')
    w("--")
    w("-- NO editar a mano. Se regenera con:")
    w(f"--   python capa2.py <carpeta_capa1> --periodo {args.periodo} --aplicar")
    w("-- ===========================================================================")
    w("")
    w("-- ###########################################################################")
    w("-- PARTE 1 — Control. Fija, igual para cualquier archivo y cualquier proyecto.")
    w("-- ###########################################################################")
    w("")
    w(control)
    w("")
    w("-- Jurisdicción de prueba. En producción se cargan las 24 desde la")
    w("-- administración del sistema.")
    w("INSERT INTO runac_c2_jurisdiccion (codigo, nombre, modalidad, activa)")
    w("VALUES ('CHUBUT', 'Chubut', 'PRESENTACION_PERIODICA', 1)")
    w("ON DUPLICATE KEY UPDATE nombre = VALUES(nombre);")
    w("")
    w("-- El período tiene que existir antes de registrar qué versiones usa.")
    w(
        "INSERT INTO runac_c2_periodo (codigo, anio, numero, fecha_desde, fecha_hasta, estado)"
    )
    w(
        f"VALUES ({q(args.periodo)}, {anio}, {numero}, '{anio}-01-01', '{anio}-03-31', 'PREPARACION')"
    )
    w("ON DUPLICATE KEY UPDATE codigo = VALUES(codigo);")
    w("")

    registrar_periodo_archivo(codigos, args.periodo, args.version, salida)

    w("-- ###########################################################################")
    w("-- PARTE 2 — Tablas receptoras. Generadas leyendo la Capa 1, una por hoja")
    w("-- y versión de estructura.")
    w("-- ###########################################################################")
    w("")

    resumen = []
    for codigo in codigos:
        f = os.path.join(dir_mapas, f"{codigo}.mapa.json")
        if not os.path.exists(f):
            print(f"  (falta el mapa de {codigo}, se omite)")
            continue
        with open(f, encoding="utf-8") as fh:
            mapa = json.load(fh)
        resumen.extend(
            tablas_receptoras(mapa, codigo, args.periodo, args.version, salida)
        )

    destino = os.path.join(args.base, "sql", f"03_capa2_{args.periodo}.sql")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8") as fh:
        fh.write("\n".join(salida))

    print(f"sql: {destino}")
    print(f"  período {args.periodo}, versión {args.version}")
    for r in resumen:
        print(
            f'  {r["codigo"]}/{r["hoja"][:18]:20} {r["tabla"]:38} {r["columnas"]:3} columnas'
        )

    if args.aplicar:
        print("\naplicando contra la base de trabajo...")
        previo = ["SET FOREIGN_KEY_CHECKS=0;"]
        for r in resumen:
            previo.append(f'DROP TABLE IF EXISTS `{r["tabla"]}`;')
        previo.append("DROP TABLE IF EXISTS " + ", ".join(TABLAS_CONTROL) + ";")
        previo.append("SET FOREIGN_KEY_CHECKS=1;")
        sql = "\n".join(previo) + "\n" + "\n".join(salida)
        proc = subprocess.run(  # noqa: S603
            [
                "mysql",
                "-hmysql",
                "-uroot",
                "-prunac_local",
                "--default-character-set=utf8mb4",
                "runac",
            ],
            input=sql.encode("utf-8"),
            capture_output=True,
            check=False,
        )
        salida = proc.stderr.decode("utf-8", "replace")
        for linea in salida.splitlines():
            if "Using a password" not in linea:
                print("  " + linea)
        print(
            "aplicado." if proc.returncode == 0 else f"FALLÓ (código {proc.returncode})"
        )


if __name__ == "__main__":
    main()
