"""Convierte el mapa crudo en un informe legible en castellano.

    python informe.py <carpeta_capa1> <CODIGO>

Las incongruencias no se corrigen: se documentan.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict

TITULOS = {
    "listas_en_conflicto": "Columnas con más de una lista de valores",
    "titulo_duplicado": "Títulos de columna repetidos",
    "lista_huerfana": "Listas escritas que ninguna columna usa",
    "valor_con_espacios": "Valores con espacios de más",
    "variantes_entre_catalogos": "El mismo valor escrito de dos formas",
    "catalogos_parecidos": "Listas casi iguales entre sí",
    "ayuda_sin_campo": "Instrucciones que no corresponden a ninguna columna",
    "ayuda_ambigua": "Instrucciones que podrían ser de más de una columna",
    "cobertura_de_ayuda": "Cobertura de las instrucciones",
    "referencia_no_resuelta": "Referencias a listas que no se pudieron resolver",
    "nombre_tecnico_desambiguado": "Nombres técnicos que hubo que desambiguar",
    "formato_contradice_al_nombre": "El formato de la celda no coincide con el nombre del campo",
    "formato_aplicado_en_bloque": "Formato aplicado a la hoja entera",
    "obligatoriedad_ambigua": "Obligatoriedad que el archivo no declara con claridad",
    "validaciones_rescatadas": "Listas que la librería de lectura descarta",
}

EXPLICACION = {
    "listas_en_conflicto":
        "Excel guarda las listas desplegables por rango de filas. Cuando una columna tiene más de una "
        "definición, y no coinciden entre sí, hay que decidir cuál vale.",
    "titulo_duplicado":
        "Dos columnas distintas con el mismo título. El nombre técnico no puede repetirse dentro de una "
        "hoja, así que hay que desambiguarlos.",
    "lista_huerfana":
        "La lista está escrita en el archivo pero ninguna columna la usa. Puede ser un olvido (la columna "
        "existe pero quedó sin desplegable) o una lista en desuso.",
    "valor_con_espacios":
        "El valor tiene espacios al principio o al final. Para una persona es invisible; para el "
        "importador es un valor distinto.",
    "variantes_entre_catalogos":
        "El mismo texto escrito de dos maneras en listas diferentes del archivo.",
    "catalogos_parecidos":
        "Dos listas que comparten la mayoría de sus valores pero no todos. Podrían ser la misma lista en "
        "dos versiones, o dos listas legítimamente distintas.",
    "ayuda_sin_campo":
        "La hoja de instrucciones explica algo que no coincide con el título de ninguna columna. Suele ser "
        "el nombre de un grupo de campos, o un título que cambió.",
    "ayuda_ambigua":
        "El mismo título aparece en varias columnas y la sección de la hoja de instrucciones no alcanza "
        "para saber a cuál corresponde.",
    "cobertura_de_ayuda": "Cuántos campos tienen texto de ayuda escrito.",
    "referencia_no_resuelta": "La lista apunta a un rango de otra hoja que no se pudo leer.",
    "nombre_tecnico_desambiguado":
        "Dos columnas daban el mismo nombre técnico. Se les agregó el grupo de campos para diferenciarlas.",
    "formato_contradice_al_nombre":
        "La celda tiene aplicado un formato que no se corresponde con lo que el nombre del campo sugiere. "
        "Suele indicar que la planilla quedó mal formateada. Se propone el tipo según el nombre.",
    "formato_aplicado_en_bloque":
        "El mismo formato está aplicado a la mayoría de las columnas de la hoja. No puede ser una decisión "
        "sobre cada campo: alguien seleccionó la hoja entera. Se ignora como evidencia del tipo de dato.",
    "obligatoriedad_ambigua":
        "La validación de esa columna no declara si admite celdas vacías, mientras el resto del archivo sí "
        "lo declara. Se toma como descuido, no como marca de obligatoriedad.",
    "validaciones_rescatadas":
        "Excel guarda de otra manera las listas que viven en otra hoja del archivo, y la librería estándar "
        "de lectura las descarta. Se recuperaron leyendo el archivo directamente.",
}


def main():
    p = argparse.ArgumentParser(description="Genera el informe de estructura de un archivo.")
    p.add_argument("base")
    p.add_argument("codigo")
    args = p.parse_args()

    with open(os.path.join(args.base, "mapas", f"{args.codigo}.mapa.json"), encoding="utf-8") as fh:
        mapa = json.load(fh)

    L: list[str] = []
    w = L.append
    a = mapa["archivo"]

    w(f'# Informe de estructura — {a["codigo"]}')
    w("")
    w(f'**Archivo:** `{a["nombre_fisico"]}`  ')
    w(f'**Huella del archivo:** `{a["sha1"][:16]}` · {a["bytes"] / 1024:.0f} KB  ')
    w(f'**Extraído:** {mapa["generado"][:19].replace("T", " ")}')
    w("")
    w("> Este informe describe lo que el archivo dice, sin corregir nada. Las")
    w("> incongruencias quedan registradas para decidir qué hacer con ellas.")
    w("")
    w("---")
    w("")

    w("## Las hojas")
    w("")
    w("| Hoja | Tipo | Contenido |")
    w("|---|---|---|")
    for h in mapa["hojas"]:
        w(f'| {h["nombre"]} | datos | {len(h["columnas"])} columnas, {len(h["dimensiones"])} grupos |')
    for n in a["hojas_de_listas"]:
        c = sum(1 for l in mapa["listas"] if l["hoja"] == n and l["titulo"])
        w(f"| {n} | listas | {c} listas de valores |")
    for n in a.get("hojas_de_ayuda", []):
        ay = next((x for x in mapa.get("ayudas", []) if x["hoja"] == n), None)
        w(f'| {n} | instrucciones | {len(ay["entradas"]) if ay else 0} entradas |')
    w("")

    for h in mapa["hojas"]:
        w(f'## Estructura de "{h["nombre"]}"')
        w("")
        if h.get("titulo_general"):
            w(f'Título: **{h["titulo_general"]}** (fila {h["fila_titulo"]}).')
        if h.get("subtitulo_general"):
            w(f'Subtítulo: *{h["subtitulo_general"]}*.')
        w(f'Grupos de campos en la fila {h["fila_dimensiones"] or "—"}, títulos de columna en la fila '
          f'{h["fila_encabezados"]}, datos desde la {h["fila_encabezados"] + 1}.')
        w("")
        if h.get("notas"):
            w("**Notas que trae la planilla:**")
            w("")
            for nota in h["notas"]:
                w(f'- *{nota["texto"]}* (fila {nota["fila"]}, columna {nota["columna"]})')
            w("")
        if h["filas_con_datos"] == 0 and h["filas_solo_placeholder"] > 0:
            w(f'**Es una plantilla vacía:** {h["filas_solo_placeholder"]} filas preparadas, ninguna con datos reales.')
        else:
            w(f'Filas con datos: {h["filas_con_datos"]}. Filas sólo con texto de relleno: {h["filas_solo_placeholder"]}.')
        w("")
        if h["dimensiones"]:
            w("| Grupo | Columnas | Campos |")
            w("|---|---|---|")
            for d in h["dimensiones"]:
                w(f'| {d["nombre"]} | {d["col_desde"]} a {d["col_hasta"]} | {d["cantidad_columnas"]} |')
            for c in [x for x in h["columnas"] if not x["dimension"]]:
                w(f'| *(sin grupo)* | {c["letra"]} | 1 — {c["titulo"]} |')
            w(f'| | | **{len(h["columnas"])}** |')
            w("")
        w("<details><summary>Ver las columnas una por una</summary>")
        w("")
        w("| Col | Nombre técnico | Título | Grupo | Tipo | Largo | Oblig. | Confianza |")
        w("|---|---|---|---|---|---|---|---|")
        for c in h["columnas"]:
            cf = c["inferencia"]["tipo"]["confianza"] if c.get("inferencia") else "—"
            w(f'| {c["letra"]} | `{c["nombre_tecnico"]}` | {c["titulo"]} | {c["dimension"] or "—"} | '
              f'{c.get("tipo_dato", "—")} | {c.get("longitud_maxima") or "—"} | '
              f'{"sí" if c.get("obligatorio") else "—"} | {cf} |')
        w("")
        w("</details>")
        w("")

    if mapa.get("inferencia"):
        inf = mapa["inferencia"]
        w("## Tipos y obligatoriedad propuestos")
        w("")
        w("El Excel casi nunca dice de qué tipo es cada campo. Lo que sigue son **propuestas**,")
        w("cada una con el motivo por el que se propuso y cuánta confianza merece.")
        w("")
        w("| Confianza | Qué significa |")
        w("|---|---|")
        w("| **alta** | Sale de algo que el archivo dice: la lista de valores, el formato de la celda, o los datos cargados. |")
        w("| **media** | El archivo dice una cosa y el nombre del campo otra. Se optó por el nombre. |")
        w("| **baja** | El archivo no dice nada. Se dedujo del nombre del campo, o es el valor por defecto. |")
        w("")
        w(f'Tipos: {" · ".join(f"**{k}** {v}" for k, v in inf["por_tipo"].items())}.')
        w(f'Confianza: {" · ".join(f"**{k}** {v}" for k, v in inf["por_confianza"].items())}.')
        w(f'Campos propuestos como obligatorios: **{inf["obligatorios"]}**. '
          f'Reglas sugeridas: **{inf.get("reglas_sugeridas", 0)}**.')
        w("")
        for h in mapa["hojas"]:
            no_texto = [c for c in h["columnas"] if c.get("tipo_dato") and c["tipo_dato"] != "TEXTO"]
            if no_texto:
                w(f'**Campos que no son texto** (hoja {h["nombre"]}):')
                w("")
                w("| Col | Campo | Tipo | Por qué |")
                w("|---|---|---|---|")
                for c in no_texto:
                    w(f'| {c["letra"]} | {c["titulo"]} | {c["tipo_dato"]} | {c["inferencia"]["tipo"]["origen"]} |')
                w("")
            reglas = [(c, r) for c in h["columnas"] for r in c.get("reglas_sugeridas", [])]
            if reglas:
                w(f'**Reglas sugeridas** (hoja {h["nombre"]}):')
                w("")
                w("| Col | Campo | Regla | Severidad | Confianza | Por qué |")
                w("|---|---|---|---|---|---|")
                for c, r in reglas:
                    w(f'| {c["letra"]} | {c["titulo"]} | `{r["tipo_regla"]}` | {r["severidad"]} | '
                      f'{r["confianza"]} | {r["motivo"]} |')
                w("")

    w("## Listas de valores")
    w("")
    total_apar = sum(len(c["apariciones"]) for c in mapa["catalogos"])
    w(f'Se encontraron **{len(mapa["catalogos"])} listas distintas**, contando {total_apar} apariciones.')
    w("Dos listas con los mismos valores se consideran la misma, aunque estén escritas en lugares diferentes.")
    w("")
    w("| Nombre | Valores | Aparece | Huella |")
    w("|---|---|---|---|")
    for c in mapa["catalogos"]:
        n = " / ".join(c["nombres_vistos"][:3]) or "(sin nombre)"
        veces = len(c["apariciones"])
        w(f'| {n[:70]} | {c["cantidad"]} | {veces} {"vez" if veces == 1 else "veces"} | `{c["huella"]}` |')
    w("")
    w("La **huella** es lo que permite reconocer una lista cuando reaparece en otro archivo.")
    w("")

    por_tipo = defaultdict(list)
    for an in mapa["anomalias"]:
        por_tipo[an["tipo"]].append(an)

    w("---")
    w("")
    w("## Incongruencias detectadas")
    w("")
    w(f'Total: **{len(mapa["anomalias"])}**. Ninguna se corrigió.')
    w("")
    w("| Tipo | Cantidad |")
    w("|---|---|")
    for t, arr in por_tipo.items():
        w(f"| {TITULOS.get(t, t)} | {len(arr)} |")
    w("")

    for t, arr in por_tipo.items():
        w(f"### {TITULOS.get(t, t)}")
        w("")
        if t in EXPLICACION:
            w(EXPLICACION[t])
            w("")
        if t == "listas_en_conflicto":
            for an in arr:
                w(f'**Columna {an["columna"]} — {an["titulo"]}**')
                w("")
                for o in an["opciones"]:
                    v = ", ".join(f"`{x}`" for x in o["valores"]) if o["valores"] \
                        else f'→ {o["referencia"]["hoja"]}!{o["referencia"]["rango"]}'
                    w(f'- Filas {o["filas"]}: {v}')
                w("")
        elif t == "catalogos_parecidos":
            for an in arr:
                w(f'- {an["detalle"]}')
                if an.get("solo_en_el_primero"):
                    w(f'   - sólo en la primera: {", ".join(f"`{x}`" for x in an["solo_en_el_primero"][:10])}')
                if an.get("solo_en_el_segundo"):
                    w(f'   - sólo en la segunda: {", ".join(f"`{x}`" for x in an["solo_en_el_segundo"][:10])}')
            w("")
        else:
            for an in arr:
                donde = "!".join(x for x in (an.get("hoja"), an.get("columna")) if x)
                enc = f' — {an["titulo"]}' if an.get("titulo") else ""
                pref = f"**{donde}**{enc}: " if donde else (f'**{an["titulo"]}**: ' if an.get("titulo") else "")
                w(f'- {pref}{an.get("detalle") or an.get("origen") or ""}')
            w("")

    destino = os.path.join(args.base, "informes", f"{args.codigo}.anomalias.md")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))
    print(f"informe: {destino}")
    print(f'  {len(mapa["anomalias"])} incongruencias documentadas')


if __name__ == "__main__":
    main()
