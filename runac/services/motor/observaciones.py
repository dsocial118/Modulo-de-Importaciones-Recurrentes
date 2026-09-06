"""Listado de observaciones sobre la planilla, para mandarle a quien la confecciona.

    python observaciones.py <carpeta_capa1> <CODIGO>

Sin jerga técnica y sin lo que sólo nos importa a nosotros: es un pedido de
corrección, no un informe interno.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict

# Qué se le informa a quien arma la planilla, y qué se resuelve puertas adentro.
PARA_LA_PLANILLA = {
    "listas_en_conflicto": {
        "titulo": "Columnas con más de una lista desplegable",
        "porque": "La misma columna tiene definidas listas distintas según la fila. El sistema no puede "
                  "saber cuál es la correcta.",
        "pedido": "Dejar una sola lista por columna, aplicada a todo el rango de filas.",
    },
    "titulo_duplicado": {
        "titulo": "Dos columnas con el mismo título",
        "porque": "Los títulos identifican a cada columna. Si se repiten, no se pueden distinguir.",
        "pedido": "Diferenciar los títulos.",
    },
    "lista_huerfana": {
        "titulo": "Listas escritas que ninguna columna usa",
        "porque": "La lista de valores está en la planilla pero no está asignada a ninguna columna, así "
                  "que quien completa el archivo la escribe a mano.",
        "pedido": "Asignar la lista a la columna que corresponde, o quitarla si ya no se usa.",
    },
    "valor_con_espacios": {
        "titulo": "Valores con espacios de más",
        "porque": "El valor tiene espacios al principio o al final. A la vista no se nota, pero para el "
                  "sistema es un valor distinto.",
        "pedido": "Quitar los espacios sobrantes.",
    },
    "variantes_entre_catalogos": {
        "titulo": "El mismo valor escrito de dos maneras",
        "porque": "En columnas distintas el mismo concepto aparece escrito diferente.",
        "pedido": "Unificar la escritura.",
    },
    "catalogos_parecidos": {
        "titulo": "Listas casi iguales entre sí",
        "porque": "Dos listas comparten la mayoría de sus valores pero no todos. Puede ser intencional o "
                  "quedar de una versión anterior.",
        "pedido": "Confirmar si son dos listas distintas o si deberían unificarse.",
    },
    "formato_contradice_al_nombre": {
        "titulo": "Columnas con el formato de celda equivocado",
        "porque": "La celda tiene aplicado un formato que no corresponde con lo que el campo pide.",
        "pedido": "Corregir el formato de la columna.",
    },
    "formato_aplicado_en_bloque": {
        "titulo": "Formato aplicado a la hoja entera",
        "porque": "Un mismo formato está puesto sobre casi todas las columnas, incluidas las que no lo "
                  "necesitan. Suele pasar al seleccionar toda la hoja y aplicar formato.",
        "pedido": "Aplicar el formato sólo a las columnas que corresponde.",
    },
    "ayuda_sin_campo": {
        "titulo": "Instrucciones que no coinciden con ninguna columna",
        "porque": "La hoja de instrucciones explica un campo cuyo título no existe en la planilla. Suele "
                  "pasar cuando se renombra una columna.",
        "pedido": "Actualizar el nombre en la hoja de instrucciones.",
    },
    "ayuda_ambigua": {
        "titulo": "Instrucciones que podrían corresponder a más de una columna",
        "porque": "Hay dos columnas con el mismo título y la instrucción no aclara a cuál se refiere.",
        "pedido": "Diferenciar los títulos, o aclarar en la instrucción a qué columna corresponde.",
    },
    "obligatoriedad_ambigua": {
        "titulo": "Columnas donde no queda claro si el dato es obligatorio",
        "porque": "La lista desplegable de esa columna no declara si admite dejar la celda vacía, mientras "
                  "que las demás sí lo declaran.",
        "pedido": "Definir si el campo admite quedar vacío.",
    },
}


def main():
    p = argparse.ArgumentParser(description="Genera el listado de observaciones sobre una planilla.")
    p.add_argument("base")
    p.add_argument("codigo")
    args = p.parse_args()

    with open(os.path.join(args.base, "mapas", f"{args.codigo}.mapa.json"), encoding="utf-8") as fh:
        mapa = json.load(fh)

    por_tipo: dict[str, list] = defaultdict(list)
    for a in mapa["anomalias"]:
        if a["tipo"] in PARA_LA_PLANILLA:
            por_tipo[a["tipo"]].append(a)
    total = sum(len(v) for v in por_tipo.values())

    L: list[str] = []
    w = L.append
    w(f"# Observaciones sobre la planilla {args.codigo}")
    w("")
    w(f'**Archivo revisado:** `{mapa["archivo"]["nombre_fisico"]}`  ')
    w(f'**Fecha de revisión:** {mapa["generado"][:10]}')
    w("")
    w("Este listado reúne los puntos de la planilla que conviene corregir antes de")
    w("distribuirla a las jurisdicciones. Son observaciones sobre **el diseño del")
    w("archivo**, no sobre los datos que contiene.")
    w("")

    if total == 0:
        w("**No se encontraron observaciones.** La planilla está en condiciones.")
    else:
        w(f"Se detectaron **{total} observaciones**, agrupadas en {len(por_tipo)} tipos.")
        w("")
        w("| # | Observación | Casos |")
        w("|---|---|---|")
        for i, (t, arr) in enumerate(por_tipo.items(), start=1):
            w(f'| {i} | {PARA_LA_PLANILLA[t]["titulo"]} | {len(arr)} |')
        w("")
        w("---")
        w("")

        for i, (t, arr) in enumerate(por_tipo.items(), start=1):
            meta = PARA_LA_PLANILLA[t]
            w(f'## {i}. {meta["titulo"]}')
            w("")
            w(f'**Qué pasa:** {meta["porque"]}')
            w("")
            w(f'**Qué habría que hacer:** {meta["pedido"]}')
            w("")
            w(f'**Dónde** ({len(arr)} {"caso" if len(arr) == 1 else "casos"}):')
            w("")
            if t == "listas_en_conflicto":
                for a in arr:
                    w(f'- **Columna {a["columna"]} — {a["titulo"]}**')
                    for o in a["opciones"]:
                        v = ", ".join(o["valores"]) if o["valores"] else "lista de otra hoja"
                        w(f'   - filas {o["filas"]}: {v}')
            elif t == "catalogos_parecidos":
                for a in arr:
                    w(f'- {a["detalle"]}')
                    if a.get("solo_en_el_primero"):
                        w(f'   - sólo en la primera: {", ".join(a["solo_en_el_primero"][:10])}')
                    if a.get("solo_en_el_segundo"):
                        w(f'   - sólo en la segunda: {", ".join(a["solo_en_el_segundo"][:10])}')
            elif t == "valor_con_espacios":
                por_origen: dict[str, list] = defaultdict(list)
                for a in arr:
                    por_origen[a.get("origen", "—")].append(a["detalle"])
                for o, vals in por_origen.items():
                    w(f'- {o}: {", ".join(vals)}')
            else:
                for a in arr:
                    donde = f'**Columna {a["columna"]}**' if a.get("columna") else ""
                    if a.get("titulo"):
                        donde = f'{donde} — {a["titulo"]}' if donde else f'**{a["titulo"]}**'
                    w(f'- {donde + ": " if donde else ""}{a.get("detalle", "")}')
            w("")

    # La cobertura de la ayuda se informa aparte: no es un error, es una falta.
    cobertura = next((a for a in mapa["anomalias"] if a["tipo"] == "cobertura_de_ayuda"), None)
    if cobertura:
        w("---")
        w("")
        w("## Campos sin explicación")
        w("")
        w(cobertura["detalle"])
        w("")
        w("La explicación de cada campo es la que después aparece en el sistema cuando el")
        w("operador provincial lo completa. Un campo sin explicación se completa a criterio")
        w("de cada provincia.")
        w("")
        sin_ayuda = [(h["nombre"], c) for h in mapa["hojas"] for c in h["columnas"] if not c.get("ayuda")]
        if sin_ayuda:
            w("<details><summary>Ver los campos sin explicación</summary>")
            w("")
            w("| Hoja | Col | Campo |")
            w("|---|---|---|")
            for hoja, c in sin_ayuda:
                w(f'| {hoja} | {c["letra"]} | {c["titulo"]} |')
            w("")
            w("</details>")
            w("")

    w("---")
    w("")
    w("*Listado generado automáticamente a partir del archivo. No se modificó la planilla original.*")

    destino = os.path.join(args.base, "informes", f"{args.codigo}.observaciones-planilla.md")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))
    print(f"observaciones: {destino}  ({total} observaciones)")


if __name__ == "__main__":
    main()
