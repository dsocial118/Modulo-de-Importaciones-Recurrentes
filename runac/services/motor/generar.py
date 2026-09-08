"""Convierte el mapa (más las decisiones tomadas) en los INSERT de la Capa 1.

    python generar.py <carpeta_capa1> <CODIGO> [--orden N]

El .sql es el entregable: revisable, versionable y repetible. La base es sólo el
banco de pruebas.

Los códigos se deciden UNA VEZ y quedan guardados en decisiones/. Si el texto de
un valor cambia en el Excel, el código NO cambia: cambia `valor_esperado`.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import date, datetime

from comun import codificar, sql_texto as q
from reglas import TIPOS_REGLA


def cargar_decisiones(base: str, codigo: str):
    f_arch = os.path.join(base, "decisiones", f"{codigo}.decisiones.json")
    f_cat = os.path.join(base, "decisiones", "catalogos.json")
    arch = {"codigo": codigo, "campos": {}, "notas": []}
    cat = {"por_huella": {}}
    if os.path.exists(f_arch):
        with open(f_arch, encoding="utf-8") as fh:
            arch = json.load(fh)
    if os.path.exists(f_cat):
        with open(f_cat, encoding="utf-8") as fh:
            cat = json.load(fh)
    return {"arch": arch, "cat": cat, "f_arch": f_arch, "f_cat": f_cat}


def guardar_decisiones(dec):
    os.makedirs(os.path.dirname(dec["f_arch"]), exist_ok=True)
    for ruta, datos in ((dec["f_arch"], dec["arch"]), (dec["f_cat"], dec["cat"])):
        with open(ruta, "w", encoding="utf-8") as fh:
            json.dump(datos, fh, ensure_ascii=False, indent=2)


def codigo_catalogo(dec, cat: dict) -> dict:
    """Código estable de un catálogo. Se crea la primera vez y no cambia más."""
    ya = dec["cat"]["por_huella"].get(cat["huella"])
    if ya:
        for n in cat["nombres_vistos"]:
            if n not in ya["nombres_vistos"]:
                ya["nombres_vistos"].append(n)
        # Valores nuevos que aparecieron en una versión posterior del archivo.
        conocidos = {o["valor_esperado"] for o in ya["opciones"]}
        for v in cat["valores"]:
            if v not in conocidos:
                ya["opciones"].append(
                    {
                        "codigo": codificar(v),
                        "valor_esperado": v,
                        "orden": len(ya["opciones"]) + 1,
                        "nuevo_en": date.today().isoformat(),
                    }
                )
        return ya

    base_cod = codificar(
        cat["nombres_vistos"][0] if cat["nombres_vistos"] else "catalogo"
    )
    usados = {c["codigo"] for c in dec["cat"]["por_huella"].values()}
    cod, n = base_cod, 2
    while cod in usados:
        cod = f"{base_cod}_{n}"
        n += 1

    opciones = []
    vistos = set()
    for i, v in enumerate(cat["valores"], start=1):
        c = codificar(v)
        k = 2
        while c in vistos:
            c = f"{codificar(v)}_{k}"
            k += 1
        vistos.add(c)
        opciones.append({"codigo": c, "valor_esperado": v, "orden": i})

    nuevo = {
        "codigo": cod,
        "huella": cat["huella"],
        "nombre": cat["nombres_vistos"][0] if cat["nombres_vistos"] else cod,
        "nombres_vistos": list(cat["nombres_vistos"]),
        "opciones": opciones,
        "decidido_el": date.today().isoformat(),
    }
    dec["cat"]["por_huella"][cat["huella"]] = nuevo
    return nuevo


def main():
    p = argparse.ArgumentParser(description="Genera los INSERT de la Capa 1.")
    p.add_argument("base")
    p.add_argument("codigo")
    p.add_argument("--orden", type=int, default=1)
    p.add_argument(
        "--version",
        type=int,
        default=1,
        help="Número de versión de la estructura del archivo.",
    )
    p.add_argument(
        "--estado",
        default="VIGENTE",
        choices=["BORRADOR", "VIGENTE", "HISTORICA"],
        help="Estado de la versión generada.",
    )
    args = p.parse_args()

    with open(
        os.path.join(args.base, "mapas", f"{args.codigo}.mapa.json"), encoding="utf-8"
    ) as fh:
        mapa = json.load(fh)
    dec = cargar_decisiones(args.base, args.codigo)

    salida: list[str] = []
    w = salida.append
    codigo = args.codigo

    w(f"-- Capa 1 de RUNAC — {codigo}")
    w(
        f'-- Generado el {datetime.now().isoformat(timespec="seconds").replace("T", " ")} a partir de:'
    )
    w(f'--   {mapa["archivo"]["nombre_fisico"]}  (sha1 {mapa["archivo"]["sha1"][:16]})')
    w("--")
    w("-- Este archivo se regenera entero. Para recargar: correrlo de nuevo.")
    w("")
    w("SET NAMES utf8mb4;")
    w("START TRANSACTION;")
    w("")

    # --- tipos de regla ---
    # Son referenciales: los mismos para todos los archivos. Se cargan con cada
    # archivo porque el .sql tiene que poder correrse solo.
    w("-- ============================================================")
    w("-- Tipos de regla de validación (apartado técnico de RUNAC)")
    w("-- ============================================================")
    for t in TIPOS_REGLA:
        w(
            f'INSERT INTO runac_c1_tipo_regla (nombre, descripcion) VALUES ({q(t["nombre"])}, {q(t["descripcion"])})'
        )
        w("  ON DUPLICATE KEY UPDATE descripcion = VALUES(descripcion);")
        for i, (nom, tipo_par, oblig, desc) in enumerate(t["parametros"], start=1):
            w(
                "INSERT INTO runac_c1_tipo_regla_parametro (tipo_regla_id, nombre, tipo_parametro, obligatorio, orden, descripcion)"
            )
            w(
                f"  SELECT id, {q(nom)}, {q(tipo_par)}, {1 if oblig else 0}, {i}, {q(desc)}"
            )
            w(f'    FROM runac_c1_tipo_regla WHERE nombre = {q(t["nombre"])}')
            w(
                "  ON DUPLICATE KEY UPDATE descripcion = VALUES(descripcion), tipo_parametro = VALUES(tipo_parametro);"
            )
    w("")

    # --- catálogos ---
    w("-- ============================================================")
    w("-- Catálogos. Se reconocen por su huella: si el mismo catálogo")
    w("-- ya vino en otro archivo, no se duplica.")
    w("-- ============================================================")
    cat_por_huella = {}
    for cat in mapa["catalogos"]:
        d = codigo_catalogo(dec, cat)
        cat_por_huella[cat["huella"]] = d
        desc = (
            f'Huella {cat["huella"]}. Aparece como: {" / ".join(d["nombres_vistos"])}.'
        )
        w(f'-- {d["codigo"]}: {len(d["opciones"])} opciones')
        w(
            "INSERT INTO runac_c1_catalogo (codigo, nombre, descripcion) VALUES "
            f'({q(d["codigo"])}, {q(d["nombre"][:255])}, {q(desc)})'
        )
        w(
            "  ON DUPLICATE KEY UPDATE nombre = VALUES(nombre), descripcion = VALUES(descripcion);"
        )
        for o in d["opciones"]:
            w(
                "INSERT INTO runac_c1_catalogo_opcion (catalogo_id, codigo, valor_esperado, orden, activo)"
            )
            w(
                f'  SELECT id, {q(o["codigo"])}, {q(o["valor_esperado"][:255])}, {o["orden"]}, 1 '
                f'FROM runac_c1_catalogo WHERE codigo = {q(d["codigo"])}'
            )
            w(
                "  ON DUPLICATE KEY UPDATE valor_esperado = VALUES(valor_esperado), orden = VALUES(orden), activo = 1;"
            )
    w("")

    # --- archivo ---
    hoja_principal = mapa["hojas"][0] if mapa["hojas"] else {}
    titulo = hoja_principal.get("titulo_general")
    subtitulo = hoja_principal.get("subtitulo_general")
    desc_archivo = f"Archivo {codigo} de RUNAC. " + ", ".join(
        f'hoja "{h["nombre"]}" con {len(h["columnas"])} campos' for h in mapa["hojas"]
    )

    w("-- ============================================================")
    w(f"-- Archivo {codigo}")
    w("-- ============================================================")
    w("-- El archivo es la IDENTIDAD y no cambia nunca. Todo lo que puede variar")
    w("-- entre períodos vive en la versión de estructura.")
    w("INSERT INTO runac_c1_archivo (codigo, descripcion, activo)")
    w(f"VALUES ({q(codigo)}, {q(desc_archivo)}, 1)")
    w("ON DUPLICATE KEY UPDATE descripcion = VALUES(descripcion), activo = 1;")
    w(f"SET @archivo := (SELECT id FROM runac_c1_archivo WHERE codigo = {q(codigo)});")
    w("")
    w(
        f"-- Versión {args.version} de la estructura. El .sql se regenera entero, así que"
    )
    w("-- se rehace el contenido de esa versión de abajo hacia arriba, para no violar")
    w("-- las claves foráneas. Una versión ya usada por un período NO debería")
    w("-- regenerarse: correspondería crear la siguiente.")
    w("SET @version := (SELECT id FROM runac_c1_archivo_version")
    w(f"                  WHERE archivo_id = @archivo AND numero = {args.version});")
    w("DELETE cr FROM runac_c1_campo_regla cr")
    w("  JOIN runac_c1_campo c ON c.id = cr.campo_id")
    w(
        "  JOIN runac_c1_hoja h ON h.id = c.hoja_id WHERE h.archivo_version_id = @version;"
    )
    w(
        "DELETE c FROM runac_c1_campo c JOIN runac_c1_hoja h ON h.id = c.hoja_id WHERE h.archivo_version_id = @version;"
    )
    w(
        "DELETE d FROM runac_c1_dimension d JOIN runac_c1_hoja h ON h.id = d.hoja_id WHERE h.archivo_version_id = @version;"
    )
    w("DELETE FROM runac_c1_hoja WHERE archivo_version_id = @version;")
    w("")
    w("INSERT INTO runac_c1_archivo_version")
    w(
        "  (archivo_id, numero, estado, nombre_esperado, titulo, subtitulo, orden_importacion, obligatorio, nota)"
    )
    w(
        f'VALUES (@archivo, {args.version}, {q(args.estado)}, {q(mapa["archivo"]["nombre_fisico"])}, '
        f"{q(titulo)}, {q(subtitulo)}, {args.orden}, 1, "
        f'{q("Generada automáticamente a partir del Excel relevado.")})'
    )
    w(
        "ON DUPLICATE KEY UPDATE estado = VALUES(estado), nombre_esperado = VALUES(nombre_esperado), "
        "titulo = VALUES(titulo), subtitulo = VALUES(subtitulo), orden_importacion = VALUES(orden_importacion);"
    )
    w("SET @version := (SELECT id FROM runac_c1_archivo_version")
    w(f"                  WHERE archivo_id = @archivo AND numero = {args.version});")
    w("")

    n_reglas = n_campos = 0
    for i_hoja, h in enumerate(mapa["hojas"], start=1):
        w(f'-- --- hoja "{h["nombre"]}" ---')
        w(
            "INSERT INTO runac_c1_hoja (archivo_version_id, nombre_esperado, descripcion, orden_procesamiento, "
            "fila_encabezados, obligatoria)"
        )
        w(
            f'VALUES (@version, {q(h["nombre"])}, {q(h.get("titulo_general"))}, {i_hoja}, '
            f'{h["fila_encabezados"]}, 1);'
        )
        w("SET @hoja := LAST_INSERT_ID();")
        w("")

        for d in h["dimensiones"]:
            desc_dim = (
                f'Columnas {d["col_desde"]} a {d["col_hasta"]} del Excel '
                f'({d["cantidad_columnas"]} campos).'
            )
            w(
                "INSERT INTO runac_c1_dimension (hoja_id, nombre_esperado, descripcion, orden)"
            )
            w(f'VALUES (@hoja, {q(d["nombre"])}, {q(desc_dim)}, {d["orden"]});')
        w("")

        for col in h["columnas"]:
            n_campos += 1
            dim_sub = (
                f'(SELECT id FROM runac_c1_dimension WHERE hoja_id = @hoja AND nombre_esperado = {q(col["dimension"])})'
                if col.get("dimension")
                else "NULL"
            )
            cat = (
                cat_por_huella.get(col.get("catalogo_huella"))
                if col.get("catalogo_huella")
                else None
            )
            cat_sub = (
                f'(SELECT id FROM runac_c1_catalogo WHERE codigo = {q(cat["codigo"])})'
                if cat
                else "NULL"
            )
            inf = col["inferencia"]

            w(f'-- {col["letra"]}: {col["titulo"]}')
            w(
                f'--    tipo {col["tipo_dato"]} por {inf["tipo"]["origen"]} (confianza {inf["tipo"]["confianza"]})'
            )
            if col.get("ayuda_origen"):
                w(f'--    ayuda tomada de {col["ayuda_origen"]}')
            w(
                "INSERT INTO runac_c1_campo (hoja_id, dimension_id, catalogo_id, nombre, titulo_esperado, orden, "
                "tipo_dato, longitud_maxima, obligatorio, ayuda)"
            )
            w(
                f'VALUES (@hoja, {dim_sub}, {cat_sub}, {q(col["nombre_tecnico"])}, {q(col["titulo"][:255])}, '
                f'{col["orden"]}, {q(col["tipo_dato"])}, {col["longitud_maxima"] if col["longitud_maxima"] else "NULL"}, '
                f'{1 if col["obligatorio"] else 0}, {q(col.get("ayuda"))});'
            )

            for r in col.get("reglas_sugeridas", []):
                n_reglas += 1
                nombre_regla = (
                    f'{codigo}_{col["nombre_tecnico"]}_{r["tipo_regla"]}'.lower()[:255]
                )
                desc_regla = f'{r["motivo"]} (confianza {r["confianza"]})'
                w(
                    "INSERT INTO runac_c1_regla (tipo_regla_id, nombre, descripcion, parametros)"
                )
                w(
                    f"  SELECT id, {q(nombre_regla)}, {q(desc_regla)}, "
                    f'{q(json.dumps(r["parametros"], ensure_ascii=False))}'
                )
                w(f'    FROM runac_c1_tipo_regla WHERE nombre = {q(r["tipo_regla"])}')
                w(
                    "  ON DUPLICATE KEY UPDATE descripcion = VALUES(descripcion), parametros = VALUES(parametros);"
                )
                # El mensaje al usuario queda vacío a propósito: se redacta en la
                # matriz de reglas de validación, en lenguaje claro. No se infiere.
                w(
                    "INSERT INTO runac_c1_campo_regla (campo_id, regla_id, severidad, mensaje)"
                )
                w(f'  SELECT c.id, r.id, {q(r["severidad"])}, NULL')
                w("    FROM runac_c1_campo c, runac_c1_regla r")
                w(
                    f'   WHERE c.hoja_id = @hoja AND c.nombre = {q(col["nombre_tecnico"])} '
                    f"AND r.nombre = {q(nombre_regla)}"
                )
                w("  ON DUPLICATE KEY UPDATE severidad = VALUES(severidad);")
            w("")

    w("COMMIT;")
    w("")
    w(
        f'-- Resumen: {len(mapa["hojas"])} hoja(s), {n_campos} campos, '
        f'{len(mapa["catalogos"])} catálogos, {n_reglas} reglas.'
    )

    destino = os.path.join(args.base, "sql", f"{args.orden + 1:02d}_{codigo}.sql")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8") as fh:
        fh.write("\n".join(salida))

    dec["arch"]["ultima_generacion"] = datetime.now().isoformat(timespec="seconds")
    dec["arch"]["origen"] = {
        "nombre_fisico": mapa["archivo"]["nombre_fisico"],
        "sha1": mapa["archivo"]["sha1"],
    }
    for h in mapa["hojas"]:
        for col in h["columnas"]:
            prev = dec["arch"]["campos"].get(
                col["nombre_tecnico"], {"titulos_vistos": []}
            )
            if col["titulo"] not in prev["titulos_vistos"]:
                prev["titulos_vistos"].append(col["titulo"])
            prev.update(
                {
                    "hoja": h["nombre"],
                    "letra": col["letra"],
                    "orden": col["orden"],
                    "tipo_dato": col["tipo_dato"],
                    "obligatorio": col["obligatorio"],
                    "catalogo": (
                        cat_por_huella[col["catalogo_huella"]]["codigo"]
                        if col.get("catalogo_huella")
                        else None
                    ),
                }
            )
            dec["arch"]["campos"][col["nombre_tecnico"]] = prev
    guardar_decisiones(dec)

    print(f"sql: {destino}")
    print(
        f'  {len(mapa["hojas"])} hoja(s), {n_campos} campos, {len(mapa["catalogos"])} catalogos, {n_reglas} reglas'
    )
    print(f'  catalogos conocidos en total: {len(dec["cat"]["por_huella"])}')


if __name__ == "__main__":
    main()
