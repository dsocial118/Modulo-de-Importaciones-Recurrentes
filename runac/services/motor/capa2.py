"""Genera TODA la Capa 2 leyendo la Capa 1.

    python capa2.py <carpeta_capa1> --periodo 2026_T1 [--archivos MPI,MPE] [--aplicar]

Produce un único .sql con:

  1. las tablas fijas de control (período, estructura, presentación,
     importación, hallazgo, observación, edición), iguales para cualquier
     archivo y para cualquier proyecto de importación;

  2. las tablas receptoras de cada hoja de cada archivo, generadas leyendo la
     Capa 1: dos por hoja, una cruda y una tipada.

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

from comun import sql_texto as q

MAX_IDENT = 64  # límite de MySQL para nombres de tabla


def abrev(texto: str, largo: int) -> str:
    return re.sub(r"[^a-z0-9_]", "", texto.lower())[:largo]


def tipo_sql(campo: dict) -> str:
    t = campo["tipo_dato"]
    if t == "FECHA":
        return "date"
    if t == "ENTERO":
        return "bigint"
    if t == "DECIMAL":
        return "decimal(18,4)"
    # El comentario de runac_c1_campo.longitud_maxima lo dice: sin longitud,
    # la columna receptora se crea como TEXT.
    return f'varchar({campo["longitud_maxima"]})' if campo.get("longitud_maxima") else "text"


def nombres_de_tabla(codigo: str, hoja: str, varias_hojas: bool) -> tuple[str, str]:
    if varias_hojas:
        sufijo = f"{abrev(codigo, 12)}_{abrev(hoja, 14)}"
    else:
        sufijo = abrev(codigo, 22)
    return f"runac_c2_cru_{sufijo}"[:MAX_IDENT], f"runac_c2_dat_{sufijo}"[:MAX_IDENT]


def tablas_receptoras(mapa: dict, codigo: str, periodo: str, version: int, S: list) -> list[dict]:
    w = S.append
    generadas = []
    varias = len(mapa["hojas"]) > 1

    for h in mapa["hojas"]:
        t_cru, t_dat = nombres_de_tabla(codigo, h["nombre"], varias)
        firma = "|".join(f'{c["orden"]}:{c["nombre_tecnico"]}:{c["tipo_dato"]}:{c.get("longitud_maxima") or ""}'
                         for c in h["columnas"])
        huella = hashlib.sha1(firma.encode("utf-8")).hexdigest()

        w("-- ------------------------------------------------------------------")
        w(f'-- {codigo} / hoja "{h["nombre"]}" — {len(h["columnas"])} columnas')
        w("-- ------------------------------------------------------------------")
        w(f"DROP TABLE IF EXISTS `{t_cru}`;")
        w(f"CREATE TABLE `{t_cru}` (")
        w("  `id` bigint PRIMARY KEY AUTO_INCREMENT COMMENT 'Identificador interno.',")
        w("  `importacion_id` bigint NOT NULL COMMENT 'Importación a la que pertenece la fila.',")
        w("  `numero_fila` int NOT NULL COMMENT 'Número de fila en el Excel, tal como lo ve quien completa la planilla.',")
        w("  `estado` ENUM('LEIDA','VALIDA','CON_ERROR','CON_ADVERTENCIA','EDITADA') NOT NULL DEFAULT 'LEIDA' "
          "COMMENT 'Resultado de la validación de la fila.',")
        w("  `hash_contenido` char(40) COMMENT 'Huella del contenido, para detectar duplicados exactos y cambios entre versiones.',")
        for c in h["columnas"]:
            comentario = f'{c["letra"]} — {c["titulo"]}'
            w(f'  `{c["nombre_tecnico"]}` text COMMENT {q(comentario[:255])},')
        w(f"  UNIQUE KEY `{abrev(t_cru, 50)}_fila` (`importacion_id`, `numero_fila`)")
        comentario_tabla = (f'Staging literal de {codigo}/{h["nombre"]}. Todo en texto: acepta cualquier '
                            "contenido para poder informar los errores sin perder el original.")
        w(f") COMMENT = {q(comentario_tabla[:1000])};")
        w("")

        w(f"DROP TABLE IF EXISTS `{t_dat}`;")
        w(f"CREATE TABLE `{t_dat}` (")
        w("  `id` bigint PRIMARY KEY AUTO_INCREMENT COMMENT 'Identificador interno.',")
        w("  `importacion_id` bigint NOT NULL COMMENT 'Importación a la que pertenece la fila.',")
        w("  `numero_fila` int NOT NULL COMMENT 'Número de fila en el Excel. Permite volver a la fila cruda.',")
        for c in h["columnas"]:
            com = f'{c["letra"]} — {c["titulo"]}' + (" (valor de catálogo)" if c.get("catalogo_huella") else "")
            nulo = "NOT NULL" if c.get("obligatorio") else "NULL"
            w(f'  `{c["nombre_tecnico"]}` {tipo_sql(c)} {nulo} COMMENT {q(com[:255])},')
        w(f"  UNIQUE KEY `{abrev(t_dat, 50)}_fila` (`importacion_id`, `numero_fila`)")
        w(f') COMMENT = {q(f"Datos validados de {codigo}. Sólo entran las filas sin errores bloqueantes."[:1000])};')
        w("")
        w(f"ALTER TABLE `{t_cru}` ADD FOREIGN KEY (`importacion_id`) REFERENCES `runac_c2_importacion` (`id`);")
        w(f"ALTER TABLE `{t_dat}` ADD FOREIGN KEY (`importacion_id`) REFERENCES `runac_c2_importacion` (`id`);")
        w("")
        w("INSERT INTO runac_c2_estructura (periodo_id, archivo_id, hoja_id, version, tabla_cruda, tabla_tipada, huella_estructura)")
        w(f"  SELECT p.id, a.id, hj.id, {version}, {q(t_cru)}, {q(t_dat)}, {q(huella[:40])}")
        w("    FROM runac_c2_periodo p, runac_c1_archivo a, runac_c1_hoja hj")
        w(f"   WHERE p.codigo = {q(periodo)} AND a.codigo = {q(codigo)}")
        w(f"     AND hj.archivo_id = a.id AND hj.nombre_esperado = {q(h['nombre'])}")
        w("  ON DUPLICATE KEY UPDATE tabla_cruda=VALUES(tabla_cruda), tabla_tipada=VALUES(tabla_tipada), "
          "huella_estructura=VALUES(huella_estructura);")
        w("")
        generadas.append({"codigo": codigo, "hoja": h["nombre"], "t_cru": t_cru, "t_dat": t_dat,
                          "columnas": len(h["columnas"]), "huella": huella})
    return generadas


def main():
    p = argparse.ArgumentParser(description="Genera la Capa 2 completa desde la Capa 1.")
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
        codigos = sorted(f.replace(".mapa.json", "") for f in os.listdir(dir_mapas) if f.endswith(".mapa.json"))

    ruta_control = os.path.join(args.base, "..", "sql", "03_schema_capa2_control.sql")
    with open(ruta_control, encoding="utf-8") as fh:
        control = fh.read()

    S: list[str] = []
    w = S.append
    anio = int(args.periodo[:4])
    m = re.search(r"T(\d)", args.periodo)
    numero = int(m.group(1)) if m else 1

    w("-- ===========================================================================")
    w(f'-- Capa 2 completa — generada el {datetime.now().isoformat(timespec="seconds").replace("T", " ")}')
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
    w("-- El período tiene que existir antes de registrar las estructuras.")
    w("INSERT INTO runac_c2_periodo (codigo, anio, numero, fecha_desde, fecha_hasta, estado)")
    w(f"VALUES ({q(args.periodo)}, {anio}, {numero}, '{anio}-01-01', '{anio}-03-31', 'PREPARACION')")
    w("ON DUPLICATE KEY UPDATE codigo = VALUES(codigo);")
    w("")
    w("-- ###########################################################################")
    w("-- PARTE 2 — Tablas receptoras. Generadas leyendo la Capa 1.")
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
        resumen.extend(tablas_receptoras(mapa, codigo, args.periodo, args.version, S))

    destino = os.path.join(args.base, "sql", f"03_capa2_{args.periodo}.sql")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8") as fh:
        fh.write("\n".join(S))

    print(f"sql: {destino}")
    print(f"  período {args.periodo}, versión {args.version}")
    for r in resumen:
        print(f'  {r["codigo"]}/{r["hoja"][:18]:20} {r["t_dat"]:34} {r["columnas"]:3} columnas')

    if args.aplicar:
        print("\naplicando contra la base de trabajo...")
        previo = ["SET FOREIGN_KEY_CHECKS=0;"]
        for r in resumen:
            previo.append(f'DROP TABLE IF EXISTS `{r["t_cru"]}`;')
            previo.append(f'DROP TABLE IF EXISTS `{r["t_dat"]}`;')
        previo.append("DROP TABLE IF EXISTS runac_c2_edicion, runac_c2_observacion, runac_c2_hallazgo, "
                      "runac_c2_importacion, runac_c2_presentacion, runac_c2_estructura, runac_c2_periodo;")
        previo.append("SET FOREIGN_KEY_CHECKS=1;")
        sql = "\n".join(previo) + "\n" + "\n".join(S)
        proc = subprocess.run(
            ["mysql", "-hmysql", "-uroot", "-prunac_local", "--default-character-set=utf8mb4", "runac"],
            input=sql.encode("utf-8"), capture_output=True)
        salida = proc.stderr.decode("utf-8", "replace")
        for linea in salida.splitlines():
            if "Using a password" not in linea:
                print("  " + linea)
        print("aplicado." if proc.returncode == 0 else f"FALLÓ (código {proc.returncode})")


if __name__ == "__main__":
    main()
