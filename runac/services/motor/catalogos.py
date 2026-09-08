"""Compara los catálogos de todos los archivos procesados.

    python catalogos.py <carpeta_capa1>

Responde tres preguntas:

  1. ¿Qué listas se repiten idénticas entre archivos? Esas son un solo catálogo
     compartido y no hay que duplicarlas.
  2. ¿Qué listas se llaman igual pero tienen contenido distinto? Ahí hay que
     decidir si es la misma lista con una diferencia o dos listas distintas.
  3. ¿Qué listas se parecen mucho sin ser iguales? Son candidatas a unificarse.

Produce un informe en informes/catalogos-comparados.md
"""

from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict

from comun import clave


def cargar_mapas(base: str) -> dict[str, dict]:
    dir_mapas = os.path.join(base, "mapas")
    mapas = {}
    for f in sorted(os.listdir(dir_mapas)):
        if not f.endswith(".mapa.json"):
            continue
        with open(os.path.join(dir_mapas, f), encoding="utf-8") as fh:
            m = json.load(fh)
        mapas[m["archivo"]["codigo"]] = m
    return mapas


def main():
    p = argparse.ArgumentParser(
        description="Compara los catálogos entre archivos de RUNAC."
    )
    p.add_argument("base")
    args = p.parse_args()

    mapas = cargar_mapas(args.base)
    if not mapas:
        print("No hay mapas para comparar.")
        return

    # huella -> {nombres, valores, archivos donde aparece}
    por_huella: dict[str, dict] = {}
    for codigo, m in mapas.items():
        for cat in m["catalogos"]:
            reg = por_huella.setdefault(
                cat["huella"],
                {
                    "huella": cat["huella"],
                    "valores": cat["valores"],
                    "cantidad": cat["cantidad"],
                    "nombres": set(),
                    "archivos": defaultdict(int),
                },
            )
            reg["nombres"].update(cat["nombres_vistos"])
            reg["archivos"][codigo] += len(cat["apariciones"])

    compartidos = [c for c in por_huella.values() if len(c["archivos"]) > 1]
    propios = [c for c in por_huella.values() if len(c["archivos"]) == 1]
    compartidos.sort(key=lambda c: (-len(c["archivos"]), -c["cantidad"]))

    # Mismo nombre, distinto contenido.
    por_nombre: dict[str, list[dict]] = defaultdict(list)
    for c in por_huella.values():
        for n in c["nombres"]:
            por_nombre[clave(n)].append(c)
    homonimos = {
        n: cs for n, cs in por_nombre.items() if len({c["huella"] for c in cs}) > 1
    }

    lineas: list[str] = []
    w = lineas.append

    w("# Catálogos comparados entre archivos")
    w("")
    w(f'Archivos analizados: {", ".join(f"**{c}**" for c in mapas)}.')
    w("")
    w("Dos listas se consideran **el mismo catálogo** cuando tienen exactamente los")
    w("mismos valores, ignorando el orden, las tildes, las mayúsculas y los textos de")
    w("relleno como `Seleccionar`. Eso es lo que llamamos su *huella*.")
    w("")
    w("| | Cantidad |")
    w("|---|---|")
    w(f"| Catálogos distintos en total | {len(por_huella)} |")
    w(f"| **Compartidos entre dos o más archivos** | **{len(compartidos)}** |")
    w(f"| Propios de un solo archivo | {len(propios)} |")
    w(f"| Nombres usados para más de un catálogo | {len(homonimos)} |")
    w("")
    w("---")
    w("")

    # --- 1. compartidos ---
    w("## 1. Catálogos compartidos")
    w("")
    if not compartidos:
        w("No hay catálogos que se repitan entre archivos.")
    else:
        w("Estos aparecen **idénticos** en más de un archivo. Se cargan una sola vez y")
        w("todos los campos que los usan apuntan al mismo catálogo.")
        w("")
        w("| Catálogo | Valores | Archivos | Usos |")
        w("|---|---|---|---|")
        for c in compartidos:
            nombres = " / ".join(sorted(c["nombres"])[:3])
            arch = ", ".join(f"{a} ({n})" for a, n in sorted(c["archivos"].items()))
            w(
                f'| {nombres} | {c["cantidad"]} | {arch} | {sum(c["archivos"].values())} |'
            )
        w("")
        w("El número entre paréntesis es cuántas columnas de ese archivo lo usan.")
    w("")

    # --- 2. homónimos ---
    w("## 2. Mismo nombre, distinto contenido")
    w("")
    if not homonimos:
        w("No hay nombres reutilizados para catálogos distintos.")
    else:
        w("**Acá hay que decidir.** Un mismo nombre identifica listas con contenidos")
        w(
            "diferentes. O son la misma lista que quedó desactualizada en algún archivo, o"
        )
        w("son dos listas legítimamente distintas que deberían llamarse distinto.")
        w("")
        for nombre, cs in sorted(homonimos.items()):
            titulo = sorted(cs[0]["nombres"])[0]
            w(f"### {titulo}")
            w("")
            w(f"{len(cs)} versiones distintas:")
            w("")
            for c in sorted(cs, key=lambda x: -x["cantidad"]):
                arch = ", ".join(sorted(c["archivos"]))
                w(f'- **{c["cantidad"]} valores** — en {arch} — huella `{c["huella"]}`')
            # Diferencias entre la más grande y las demás.
            base = max(cs, key=lambda x: x["cantidad"])
            sb = {clave(v) for v in base["valores"]}
            for c in cs:
                if c is base:
                    continue
                sc = {clave(v) for v in c["valores"]}
                faltan = [v for v in base["valores"] if clave(v) not in sc]
                sobran = [v for v in c["valores"] if clave(v) not in sb]
                if faltan:
                    w(
                        f'   - le faltan respecto de la más completa: {", ".join(f"`{v}`" for v in faltan)}'
                    )
                if sobran:
                    w(f'   - tiene de más: {", ".join(f"`{v}`" for v in sobran)}')
            w("")
    w("")

    # --- 3. parecidos entre archivos ---
    w("## 3. Catálogos parecidos, en archivos distintos")
    w("")
    parecidos = []
    lista = list(por_huella.values())
    for i, a in enumerate(lista):
        for b in lista[i + 1 :]:
            if set(a["archivos"]) == set(b["archivos"]) and len(a["archivos"]) == 1:
                continue  # los del mismo archivo ya se reportan en su propio informe
            sa = {clave(v) for v in a["valores"]}
            sb = {clave(v) for v in b["valores"]}
            union = len(sa | sb)
            solape = len(sa & sb) / union if union else 0
            if 0.7 <= solape < 1:
                parecidos.append((solape, a, b))
    parecidos.sort(key=lambda t: -t[0])

    if not parecidos:
        w("No se encontraron listas parecidas entre archivos distintos.")
    else:
        w(
            "Comparten la mayoría de sus valores pero no todos. Vale revisarlas: puede ser"
        )
        w("que se hayan actualizado en un archivo y no en el otro.")
        w("")
        for solape, a, b in parecidos[:25]:
            na = sorted(a["nombres"])[0] if a["nombres"] else a["huella"]
            nb = sorted(b["nombres"])[0] if b["nombres"] else b["huella"]
            w(
                f'- **{na}** ({", ".join(sorted(a["archivos"]))}, {a["cantidad"]} valores) '
                f'y **{nb}** ({", ".join(sorted(b["archivos"]))}, {b["cantidad"]} valores) '
                f"— coinciden en el {round(solape * 100)}%"
            )
            sa = {clave(v) for v in a["valores"]}
            sb = {clave(v) for v in b["valores"]}
            solo_a = [v for v in a["valores"] if clave(v) not in sb]
            solo_b = [v for v in b["valores"] if clave(v) not in sa]
            if solo_a:
                w(f'   - sólo en la primera: {", ".join(f"`{v}`" for v in solo_a[:8])}')
            if solo_b:
                w(f'   - sólo en la segunda: {", ".join(f"`{v}`" for v in solo_b[:8])}')
        if len(parecidos) > 25:
            w("")
            w(f"*(se muestran 25 de {len(parecidos)} casos)*")
    w("")

    # --- 4. inventario por archivo ---
    w("---")
    w("")
    w("## 4. Inventario por archivo")
    w("")
    w("| Archivo | Catálogos | Compartidos | Propios |")
    w("|---|---|---|---|")
    for codigo in mapas:
        total = sum(1 for c in por_huella.values() if codigo in c["archivos"])
        comp = sum(1 for c in compartidos if codigo in c["archivos"])
        w(f"| {codigo} | {total} | {comp} | {total - comp} |")
    w("")

    destino = os.path.join(args.base, "informes", "catalogos-comparados.md")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas))

    print(f"informe: {destino}")
    print(f"  catalogos distintos:  {len(por_huella)}")
    print(f"  compartidos:          {len(compartidos)}")
    print(f"  homonimos a resolver: {len(homonimos)}")
    print(f"  parecidos:            {len(parecidos)}")


if __name__ == "__main__":
    main()
