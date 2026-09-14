"""Lee un Excel y produce el "mapa crudo": lo que el archivo dice.

    python extraer.py "<archivo.xlsx>" "<carpeta_salida>" --codigo MPI

Determinista: el mismo archivo produce siempre el mismo resultado. No corrige
nada; las incongruencias quedan registradas para decidir qué hacer con ellas.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict

import lector_excel as LX
import validaciones_x14
from comun import (
    clave,
    es_placeholder,
    huella,
    nombre_tecnico,
    norm,
    sha1_archivo,
    titulo_sin_instrucciones,
)
from inferir import inferir_campo
from reglas import sugerir_reglas, sugerir_reglas_de_hoja


# --- detección de la estructura de una hoja --------------------------------

# Qué tan variados tienen que ser los valores de una fila para que pueda ser la
# de títulos. Medido sobre las seis planillas recibidas: las filas de títulos dan
# entre 0,97 y 1,00 y las de anotaciones entre 0,02 y 0,35. No hay zona gris.
VARIEDAD_DE_TITULOS = 0.8


def variedad(hoja: LX.Hoja, fila: int) -> float:
    """Proporción de valores distintos en una fila.

    Es lo que distingue una fila de títulos de una de anotaciones. Los títulos
    nombran columnas, así que casi no se repiten; las anotaciones dicen lo mismo
    muchas veces —«Seleccionar» cinco veces, «AGREGADO» cuatro—, igual que las
    filas de datos.
    """
    valores = [
        str(LX.texto(hoja, fila, c) or "").strip().lower()
        for c in range(1, hoja.max_columna + 1)
    ]
    valores = [v for v in valores if v]
    return len(set(valores)) / len(valores) if valores else 0.0


def detectar_estructura(hoja: LX.Hoja) -> dict:
    """Ubica el título general, la fila de dimensiones y la de encabezados.

    Se apoya en cómo Excel guarda las celdas combinadas: una que cubre casi todo
    el ancho es el título; las que agrupan varias columnas son las dimensiones.

    La fila de títulos era simplemente la que más celdas llenas tenía, y eso
    alcanzaba mientras las planillas no traían anotaciones de trabajo. El MPE de
    septiembre trae una fila de aclaraciones debajo del encabezado —«Campo
    abierto», «AGREGADO», «Seleccionar»— con UNA celda llena más que la de
    títulos, y con eso se llevaba la elección: la Capa 1 salía con veinte
    columnas llamadas «Seleccionar». Por eso ahora primero se descarta lo que no
    puede ser una fila de títulos, y recién después se cuenta.
    """
    llenas_por_fila = {}
    for fila in range(1, min(hoja.max_fila, 12) + 1):
        llenas_por_fila[fila] = sum(
            1 for col in range(1, hoja.max_columna + 1) if (fila, col) in hoja.celdas
        )
    candidatas = {
        f: n
        for f, n in llenas_por_fila.items()
        if n and variedad(hoja, f) >= VARIEDAD_DE_TITULOS
    }
    # Si ninguna fila califica, se decide como antes: es preferible elegir mal a
    # no elegir, porque el mapa de la hoja se revisa igual antes de generar.
    entre = candidatas or llenas_por_fila
    fila_encabezados = max(entre, key=lambda f: entre[f]) if entre else 1

    horizontales = defaultdict(list)
    for f1, c1, f2, c2 in hoja.combinadas:
        if c2 > c1:
            horizontales[f1].append((f1, c1, f2, c2))

    # Encabezado de la planilla. La señal que lo distingue es dónde empieza:
    #
    #   fila 1:  F1 = "ATENCIÓN: respetar las clasificaciones..."   una nota
    #   fila 2:  A2 = "Listado de dispositivos penales..."          el título
    #
    # El título arranca en la columna A y ocupa una fila para sí solo. Un bloque
    # combinado que empieza más a la derecha es una aclaración al usuario, no un
    # título, y se guarda aparte porque también es información útil.
    encabezados = []
    notas = []
    for f in sorted(horizontales):
        if f >= fila_encabezados:
            continue
        bloques = horizontales[f]
        desde_a = [r for r in bloques if r[1] == 1]
        if len(bloques) == 1 and desde_a:
            texto_enc = titulo_sin_instrucciones(
                LX.texto(hoja, desde_a[0][0], desde_a[0][1])
            )
            if texto_enc:
                encabezados.append((f, texto_enc))
        else:
            for r in bloques:
                if r[1] == 1:
                    continue
                texto_nota = LX.texto(hoja, r[0], r[1])
                if texto_nota:
                    notas.append(
                        {"fila": r[0], "columna": LX.letra(r[1]), "texto": texto_nota}
                    )

    fila_titulo = encabezados[0][0] if encabezados else None
    titulo_general = encabezados[0][1] if encabezados else None
    subtitulo_general = encabezados[1][1] if len(encabezados) > 1 else None
    filas_encabezado = {f for f, _ in encabezados}

    fila_dimensiones = None
    for f, rangos in horizontales.items():
        if f in filas_encabezado:
            continue
        if f < fila_encabezados and len(rangos) >= 2:
            if fila_dimensiones is None or f > fila_dimensiones:
                fila_dimensiones = f

    return {
        "fila_encabezados": fila_encabezados,
        "fila_dimensiones": fila_dimensiones,
        "fila_titulo": fila_titulo,
        "titulo_general": titulo_general,
        "subtitulo_general": subtitulo_general,
        "notas": notas,
    }


def clasificar_hoja(hoja: LX.Hoja, hojas_apuntadas: set[str]) -> str:
    """Cada hoja es de datos, de listas o de instrucciones.

    La señal más confiable no es heurística: si alguna validación de otra hoja
    apunta a ésta, entonces es una hoja de listas. Lo dice el propio archivo.
    """
    if hoja.nombre in hojas_apuntadas:
        return "listas"
    if hoja.combinadas:
        return "datos"
    if hoja.max_columna < 2:
        return "listas"

    if hoja.max_columna <= 3:
        largos = filas = 0
        for f in range(2, hoja.max_fila + 1):
            b = hoja.celdas.get((f, 2))
            if b is None:
                continue
            filas += 1
            if len(str(b)) > 40:
                largos += 1
        if filas and largos / filas > 0.5:
            return "ayuda"

    con_titulo = sum(1 for c in range(1, hoja.max_columna + 1) if (1, c) in hoja.celdas)
    if con_titulo / hoja.max_columna < 0.9 and hoja.max_fila > 10:
        return "listas"
    return "datos"


def extraer_listas(hoja: LX.Hoja) -> list[dict]:
    salida = []
    for col in range(1, hoja.max_columna + 1):
        titulo = LX.texto(hoja, 1, col)
        valores = [
            str(hoja.celdas[(f, col)])
            for f in range(2, hoja.max_fila + 1)
            if (f, col) in hoja.celdas
        ]
        if not titulo and not valores:
            continue
        salida.append(
            {
                "hoja": hoja.nombre,
                "columna": LX.letra(col),
                "titulo": titulo or None,
                "rango": f"{LX.letra(col)}2:{LX.letra(col)}{hoja.max_fila}",
                "cantidad": len(valores),
                "valores": valores,
            }
        )
    return salida


def extraer_ayuda(hoja: LX.Hoja) -> dict:
    """Las filas con nombre pero sin texto son encabezados de sección.

    Las secciones se corresponden con las dimensiones de la hoja de datos, y
    sirven para desambiguar cuando dos campos distintos se llaman igual.
    """
    entradas = []
    seccion = None
    for f in range(2, hoja.max_fila + 1):
        campo = LX.texto(hoja, f, 1)
        texto_ayuda = LX.texto(hoja, f, 2)
        if not campo:
            continue
        if not texto_ayuda:
            seccion = campo
            entradas.append(
                {
                    "fila": f,
                    "campo": campo,
                    "ayuda": None,
                    "es_seccion": True,
                    "seccion": None,
                }
            )
        else:
            entradas.append(
                {
                    "fila": f,
                    "campo": campo,
                    "ayuda": texto_ayuda,
                    "es_seccion": False,
                    "seccion": seccion,
                }
            )
    return {"hoja": hoja.nombre, "entradas": entradas}


def extraer_hoja_datos(hoja: LX.Hoja, extras: list[dict], anomalias: list) -> dict:
    est = detectar_estructura(hoja)
    fila_enc = est["fila_encabezados"]
    fila_dim = est["fila_dimensiones"]

    # --- dimensiones ---
    dimensiones = []
    dim_de_col = {}
    if fila_dim is not None:
        rangos = sorted(
            [r for r in hoja.combinadas if r[0] == fila_dim and r[3] > r[1]],
            key=lambda r: r[1],
        )
        for orden, (f1, c1, _f2, c2) in enumerate(rangos, start=1):
            nombre = LX.texto(hoja, f1, c1)
            if not nombre:
                continue
            dimensiones.append(
                {
                    "nombre": nombre,
                    "orden": orden,
                    "col_desde": LX.letra(c1),
                    "col_hasta": LX.letra(c2),
                    "cantidad_columnas": c2 - c1 + 1,
                }
            )
            for c in range(c1, c2 + 1):
                dim_de_col[c] = nombre

    # --- validaciones por columna (las de openpyxl más las rescatadas) ---
    val_por_col = defaultdict(list)
    for v in list(hoja.validaciones) + list(extras):
        for c in range(v["col_desde"], v["col_hasta"] + 1):
            val_por_col[c].append(v)

    # --- columnas ---
    columnas = []
    vistos = {}
    for c in range(1, hoja.max_columna + 1):
        titulo = LX.texto(hoja, fila_enc, c)
        desde = "encabezado"
        if not titulo and fila_dim is not None:
            t2 = LX.texto(hoja, fila_dim, c)
            if t2 and c not in dim_de_col:
                titulo, desde = t2, "dimension_vertical"
        if not titulo:
            continue

        vals = val_por_col.get(c, [])
        firmas = {
            json.dumps(
                v["literal"] or v["referencia"], sort_keys=True, ensure_ascii=False
            )
            for v in vals
        }
        if len(firmas) > 1:
            anomalias.append(
                {
                    "tipo": "listas_en_conflicto",
                    "hoja": hoja.nombre,
                    "columna": LX.letra(c),
                    "titulo": titulo,
                    "detalle": f"La columna tiene {len(firmas)} listas distintas según el rango de filas.",
                    "opciones": [
                        {
                            "filas": f'{v["fila_desde"]}-{v["fila_hasta"]}',
                            "valores": (
                                [norm(x) for x in v["literal"]]
                                if v["literal"]
                                else None
                            ),
                            "referencia": v["referencia"],
                        }
                        for v in vals
                    ],
                }
            )

        k = clave(titulo)
        if k in vistos:
            anomalias.append(
                {
                    "tipo": "titulo_duplicado",
                    "hoja": hoja.nombre,
                    "columna": LX.letra(c),
                    "titulo": titulo,
                    "detalle": f"El mismo título ya aparece en la columna {vistos[k]}.",
                }
            )
        else:
            vistos[k] = LX.letra(c)

        muestras = []
        for f in range(fila_enc + 1, hoja.max_fila + 1):
            v = hoja.celdas.get((f, c))
            if v is None or es_placeholder(v):
                continue
            muestras.append(str(v))
            if len(muestras) >= 40:
                break

        # allowBlank sólo cuenta como evidencia si el autor lo declaró. Si el
        # atributo falta, es el valor por omisión y no dice nada.
        no_vacio_explicito = any(
            v.get("admite_vacio") is False and v.get("admite_vacio_declarado", True)
            for v in vals
        )
        no_vacio_ambiguo = any(
            v.get("admite_vacio") is False and not v.get("admite_vacio_declarado", True)
            for v in vals
        )
        if no_vacio_ambiguo:
            anomalias.append(
                {
                    "tipo": "obligatoriedad_ambigua",
                    "hoja": hoja.nombre,
                    "columna": LX.letra(c),
                    "titulo": titulo,
                    "detalle": "La validación de esta columna no declara si admite celdas vacías, "
                    "mientras que el resto del archivo sí lo declara. Parece un descuido, "
                    "no una marca de obligatoriedad.",
                }
            )

        columnas.append(
            {
                "letra": LX.letra(c),
                "orden": c,
                "titulo": titulo,
                "titulo_desde": desde,
                "nombre_tecnico": nombre_tecnico(titulo),
                "dimension": dim_de_col.get(c),
                "formato": LX.formato_de(hoja, c),
                "clase_formato": LX.clase_formato_de(hoja, c),
                "no_admite_vacio_explicito": no_vacio_explicito,
                "muestras": muestras,
                "listas": vals,
                "ayuda": None,
            }
        )

    # Nombres técnicos repetidos: se desambiguan con la dimensión.
    por_nombre = defaultdict(list)
    for col in columnas:
        por_nombre[col["nombre_tecnico"]].append(col)
    for n, arr in list(por_nombre.items()):
        if len(arr) < 2:
            continue
        for col in arr:
            sufijo = (
                nombre_tecnico(col["dimension"])
                if col["dimension"]
                else f'col_{col["letra"].lower()}'
            )
            col["nombre_tecnico"] = nombre_tecnico(f"{n}_{sufijo}")
            col["nombre_desambiguado"] = True
        anomalias.append(
            {
                "tipo": "nombre_tecnico_desambiguado",
                "hoja": hoja.nombre,
                "titulo": n,
                "detalle": f"{len(arr)} columnas daban el mismo nombre técnico. Quedaron: "
                + ", ".join(f'{c["letra"]}={c["nombre_tecnico"]}' for c in arr)
                + ".",
            }
        )

    # Un formato aplicado a la mayoría de las columnas no es una decisión sobre
    # cada campo: es alguien que seleccionó la hoja entera y le puso formato.
    conteo_formato: dict[str, int] = defaultdict(int)
    for col in columnas:
        if col["formato"] and col["formato"] != "General":
            conteo_formato[col["formato"]] += 1
    if columnas:
        for fmt, n in conteo_formato.items():
            if n / len(columnas) >= 0.5 and n >= 5:
                for col in columnas:
                    if col["formato"] == fmt:
                        col["formato_masivo"] = True
                anomalias.append(
                    {
                        "tipo": "formato_aplicado_en_bloque",
                        "hoja": hoja.nombre,
                        "detalle": f'El formato "{fmt}" está aplicado a {n} de las {len(columnas)} columnas. '
                        f"No puede ser una decisión sobre cada campo: se ignora como evidencia del tipo de dato.",
                    }
                )

    con_dato = solo_placeholder = 0
    for f in range(fila_enc + 1, hoja.max_fila + 1):
        reales = ph = 0
        for c in range(1, hoja.max_columna + 1):
            v = hoja.celdas.get((f, c))
            if v is None:
                continue
            if es_placeholder(v):
                ph += 1
            else:
                reales += 1
        if reales:
            con_dato += 1
        elif ph:
            solo_placeholder += 1

    return {
        "nombre": hoja.nombre,
        "indice": hoja.indice,
        "estado": hoja.estado,
        "ultima_fila": hoja.max_fila,
        "ultima_columna": LX.letra(hoja.max_columna),
        "titulo_general": est["titulo_general"],
        "subtitulo_general": est.get("subtitulo_general"),
        "notas": est.get("notas", []),
        "fila_titulo": est["fila_titulo"],
        "fila_dimensiones": fila_dim,
        "fila_encabezados": fila_enc,
        "filas_con_datos": con_dato,
        "filas_solo_placeholder": solo_placeholder,
        "dimensiones": dimensiones,
        "columnas": columnas,
    }


# --- programa ---------------------------------------------------------------


def main():
    p = argparse.ArgumentParser(
        description="Extrae la estructura de un Excel de RUNAC."
    )
    p.add_argument("archivo")
    p.add_argument("salida")
    p.add_argument("--codigo", default=None)
    args = p.parse_args()

    nombre_fisico = os.path.basename(args.archivo)
    codigo = args.codigo or nombre_fisico.rsplit(".", 1)[0].split()[0].upper()

    hojas_excel = LX.leer(args.archivo)
    rescatadas = validaciones_x14.leer(args.archivo)
    anomalias: list[dict] = []

    # Primero se ve qué hojas son apuntadas por alguna validación: esas son,
    # sin lugar a dudas, hojas de listas.
    hojas_apuntadas: set[str] = set()
    for hoja in hojas_excel:
        for v in list(hoja.validaciones) + list(rescatadas.get(hoja.nombre, [])):
            if v.get("referencia"):
                hojas_apuntadas.add(v["referencia"]["hoja"])

    hojas_datos, hojas_listas, hojas_ayuda = [], [], []
    listas, ayudas = [], []

    for hoja in hojas_excel:
        tipo = clasificar_hoja(hoja, hojas_apuntadas)
        if tipo == "listas":
            hojas_listas.append(hoja.nombre)
            listas.extend(extraer_listas(hoja))
        elif tipo == "ayuda":
            hojas_ayuda.append(hoja.nombre)
            ayudas.append(extraer_ayuda(hoja))
        else:
            extras = rescatadas.get(hoja.nombre, [])
            if extras:
                anomalias.append(
                    {
                        "tipo": "validaciones_rescatadas",
                        "hoja": hoja.nombre,
                        "detalle": f"Se recuperaron {len(extras)} listas desplegables que openpyxl descarta "
                        f"(las que apuntan a otra hoja del archivo).",
                    }
                )
            hojas_datos.append(extraer_hoja_datos(hoja, extras, anomalias))

    # --- resolver las listas que apuntan a otra hoja ---
    por_hoja_col = {f'{l["hoja"]}!{l["columna"]}': l for l in listas}
    for h in hojas_datos:
        for col in h["columnas"]:
            for li in col["listas"]:
                ref = li.get("referencia")
                if not ref:
                    continue
                from validaciones_x14 import _partes_rango

                r = _partes_rango(ref["rango"])
                lista = (
                    por_hoja_col.get(f'{ref["hoja"]}!{LX.letra(r[1])}') if r else None
                )
                if lista and r:
                    li["valores_resueltos"] = lista["valores"][r[0] - 2 : r[2] - 1]
                else:
                    anomalias.append(
                        {
                            "tipo": "referencia_no_resuelta",
                            "hoja": h["nombre"],
                            "columna": col["letra"],
                            "titulo": col["titulo"],
                            "detalle": f'No se pudo resolver {li["formula"]}',
                        }
                    )

    # --- cruzar la ayuda con los campos ---
    candidatos = defaultdict(list)
    total_campos = 0
    for h in hojas_datos:
        for col in h["columnas"]:
            total_campos += 1
            candidatos[clave(col["titulo"])].append((h["nombre"], col))

    for a in ayudas:
        for e in a["entradas"]:
            if e["es_seccion"]:
                e["campo_destino"] = None
                continue
            opciones = candidatos.get(clave(e["campo"]), [])
            elegida = None
            if len(opciones) == 1:
                elegida = opciones[0]
            elif len(opciones) > 1:
                if e["seccion"]:
                    elegida = next(
                        (
                            o
                            for o in opciones
                            if o[1]["dimension"]
                            and clave(o[1]["dimension"]) == clave(e["seccion"])
                        ),
                        None,
                    )
                if not elegida:
                    anomalias.append(
                        {
                            "tipo": "ayuda_ambigua",
                            "hoja": a["hoja"],
                            "titulo": e["campo"],
                            "detalle": f'"{e["campo"]}" coincide con {len(opciones)} columnas '
                            f'({", ".join(o[1]["letra"] for o in opciones)}) y la sección '
                            f'"{e["seccion"] or "—"}" no permite decidir.',
                        }
                    )
            if elegida:
                e["campo_destino"] = {
                    "hoja": elegida[0],
                    "columna": elegida[1]["letra"],
                }
                elegida[1]["ayuda"] = e["ayuda"]
                elegida[1]["ayuda_origen"] = f'{a["hoja"]}, fila {e["fila"]}'
            else:
                e["campo_destino"] = None
                if not opciones:
                    anomalias.append(
                        {
                            "tipo": "ayuda_sin_campo",
                            "hoja": a["hoja"],
                            "titulo": e["campo"],
                            "detalle": f'La hoja de instrucciones explica "{e["campo"]}", que no coincide con ninguna columna.',
                        }
                    )
        explicados = sum(
            1 for e in a["entradas"] if e.get("campo_destino") and e["ayuda"]
        )
        anomalias.append(
            {
                "tipo": "cobertura_de_ayuda",
                "hoja": a["hoja"],
                "detalle": f"La hoja de instrucciones explica {explicados} de los {total_campos} campos. "
                f"Quedan {total_campos - explicados} sin texto de ayuda.",
            }
        )

    # --- listas huérfanas ---
    usadas = set()
    for h in hojas_datos:
        for col in h["columnas"]:
            for li in col["listas"]:
                ref = li.get("referencia")
                if ref:
                    from validaciones_x14 import _partes_rango

                    r = _partes_rango(ref["rango"])
                    if r:
                        usadas.add(f'{ref["hoja"]}!{LX.letra(r[1])}')
    for l in listas:
        if f'{l["hoja"]}!{l["columna"]}' not in usadas and l["titulo"]:
            anomalias.append(
                {
                    "tipo": "lista_huerfana",
                    "hoja": l["hoja"],
                    "columna": l["columna"],
                    "titulo": l["titulo"],
                    "detalle": f'Lista de {l["cantidad"]} valores que ninguna columna usa.',
                }
            )

    # --- catálogos, agrupados por huella ---
    por_huella: dict[str, dict] = {}

    def agregar_catalogo(nombre_sug, valores_crudos, origen, usado_por):
        valores = [norm(v) for v in valores_crudos if norm(v)]
        reales = [v for v in valores if not es_placeholder(v)]
        placeholders = [v for v in valores if es_placeholder(v)]
        if not reales:
            return
        hh = huella(reales)
        cat = por_huella.setdefault(
            hh,
            {
                "huella": hh,
                "nombres_vistos": [],
                "cantidad": len(reales),
                "valores": reales,
                # Los valores tal como venían, antes de recortar espacios. Sirven
                # para detectar los que traen espacios de más.
                "valores_crudos": [str(v) for v in valores_crudos],
                "placeholders_descartados": [],
                "apariciones": [],
            },
        )
        if nombre_sug and nombre_sug not in cat["nombres_vistos"]:
            cat["nombres_vistos"].append(nombre_sug)
        for ph in placeholders:
            if ph not in cat["placeholders_descartados"]:
                cat["placeholders_descartados"].append(ph)
        cat["apariciones"].append(
            {"archivo": codigo, "origen": origen, "usado_por": usado_por}
        )

    for l in listas:
        if l["titulo"]:
            agregar_catalogo(
                l["titulo"], l["valores"], f'{l["hoja"]}!{l["rango"]}', None
            )
    for h in hojas_datos:
        for col in h["columnas"]:
            for li in col["listas"]:
                usado = f'{h["nombre"]}!{col["letra"]} ({col["titulo"]})'
                if li.get("literal"):
                    agregar_catalogo(
                        col["titulo"],
                        li["literal"],
                        f'{h["nombre"]}!{col["letra"]} filas {li["fila_desde"]}-{li["fila_hasta"]}',
                        usado,
                    )
                elif li.get("valores_resueltos"):
                    agregar_catalogo(
                        col["titulo"], li["valores_resueltos"], li["formula"], usado
                    )

    catalogos = sorted(por_huella.values(), key=lambda c: -len(c["apariciones"]))

    # --- anomalías de contenido ---
    for cat in catalogos:
        # Se compara contra el valor CRUDO: el normalizado ya no tiene espacios.
        for v in cat.get("valores_crudos", []):
            if v and v != norm(v):
                anomalias.append(
                    {
                        "tipo": "valor_con_espacios",
                        "origen": (
                            cat["nombres_vistos"][0]
                            if cat["nombres_vistos"]
                            else cat["huella"]
                        ),
                        "detalle": json.dumps(v, ensure_ascii=False),
                    }
                )

    formas = defaultdict(set)
    for cat in catalogos:
        for v in cat["valores"]:
            formas[clave(v)].add(v)
    for _k, formas_v in formas.items():
        if len(formas_v) > 1:
            anomalias.append(
                {
                    "tipo": "variantes_entre_catalogos",
                    "detalle": " / ".join(
                        json.dumps(v, ensure_ascii=False) for v in sorted(formas_v)
                    ),
                }
            )

    for i, a in enumerate(catalogos):
        for b in catalogos[i + 1 :]:
            sa = {clave(v) for v in a["valores"]}
            sb = {clave(v) for v in b["valores"]}
            comunes = len(sa & sb)
            union = len(sa | sb)
            solape = comunes / union if union else 0
            if 0.6 <= solape < 1:
                anomalias.append(
                    {
                        "tipo": "catalogos_parecidos",
                        "detalle": f'"{a["nombres_vistos"][0]}" ({a["cantidad"]}) y "{b["nombres_vistos"][0]}" '
                        f'({b["cantidad"]}) comparten el {round(solape * 100)}% de sus valores.',
                        "solo_en_el_primero": [
                            v for v in a["valores"] if clave(v) not in sb
                        ],
                        "solo_en_el_segundo": [
                            v for v in b["valores"] if clave(v) not in sa
                        ],
                        "huellas": [a["huella"], b["huella"]],
                    }
                )

    # --- inferencia de tipo, longitud y obligatoriedad ---
    cat_por_huella = {c["huella"]: c for c in catalogos}
    for h in hojas_datos:
        for col in h["columnas"]:
            cat = None
            for li in col["listas"]:
                vals = li.get("literal") or li.get("valores_resueltos")
                if not vals:
                    continue
                reales = [norm(v) for v in vals if norm(v) and not es_placeholder(v)]
                if reales:
                    cat = cat_por_huella.get(huella(reales))
                    if cat:
                        break
            col["catalogo_huella"] = cat["huella"] if cat else None
            inf = inferir_campo(
                col,
                bool(cat),
                cat["cantidad"] if cat else 0,
                max((len(v) for v in cat["valores"]), default=0) if cat else 0,
            )
            col.update(inf)
            if inf["conflicto_de_tipo"]:
                anomalias.append(
                    {
                        "tipo": "formato_contradice_al_nombre",
                        "hoja": h["nombre"],
                        "columna": col["letra"],
                        "titulo": col["titulo"],
                        "detalle": inf["conflicto_de_tipo"]["detalle"],
                    }
                )

    # --- reglas sugeridas ---
    for h in hojas_datos:
        for col in h["columnas"]:
            col["reglas_sugeridas"] = sugerir_reglas(col, h["columnas"])
        for r in sugerir_reglas_de_hoja(h):
            destino = next(
                (c for c in h["columnas"] if c["nombre_tecnico"] == r["aplicar_a"]),
                None,
            )
            if destino:
                destino["reglas_sugeridas"].append(r)

    resumen = {
        "por_tipo": defaultdict(int),
        "por_confianza": defaultdict(int),
        "obligatorios": 0,
        "reglas_sugeridas": 0,
        "por_tipo_regla": defaultdict(int),
    }
    for h in hojas_datos:
        for col in h["columnas"]:
            resumen["por_tipo"][col["tipo_dato"]] += 1
            resumen["por_confianza"][col["inferencia"]["tipo"]["confianza"]] += 1
            if col["obligatorio"]:
                resumen["obligatorios"] += 1
            for r in col["reglas_sugeridas"]:
                resumen["reglas_sugeridas"] += 1
                resumen["por_tipo_regla"][r["tipo_regla"]] += 1
    resumen = {
        k: (dict(v) if isinstance(v, defaultdict) else v) for k, v in resumen.items()
    }

    # Las muestras no van al mapa: pueden traer datos personales.
    for h in hojas_datos:
        for col in h["columnas"]:
            col["cantidad_muestras"] = len(col.pop("muestras", []))

    from datetime import datetime, timezone

    mapa = {
        "generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "archivo": {
            "codigo": codigo,
            "nombre_fisico": nombre_fisico,
            "ruta_origen": args.archivo,
            "bytes": os.path.getsize(args.archivo),
            "sha1": sha1_archivo(args.archivo),
            "hojas_totales": len(hojas_excel),
            "hojas_de_datos": [h["nombre"] for h in hojas_datos],
            "hojas_de_listas": hojas_listas,
            "hojas_de_ayuda": hojas_ayuda,
        },
        "hojas": hojas_datos,
        "listas": listas,
        "ayudas": ayudas,
        "catalogos": catalogos,
        "inferencia": resumen,
        "anomalias": anomalias,
    }

    destino = os.path.join(args.salida, "mapas", f"{codigo}.mapa.json")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(mapa, f, ensure_ascii=False, indent=2)

    print(f"mapa: {destino}")
    print(f"  codigo:           {codigo}")
    print(
        f'  hojas de datos:   {", ".join(h["nombre"] for h in hojas_datos) or "(ninguna)"}'
    )
    print(f'  hojas de listas:  {", ".join(hojas_listas) or "(ninguna)"}')
    print(f'  hojas de ayuda:   {", ".join(hojas_ayuda) or "(ninguna)"}')
    for h in hojas_datos:
        con_ayuda = sum(1 for c in h["columnas"] if c["ayuda"])
        print(
            f'  - "{h["nombre"]}": {len(h["columnas"])} columnas ({con_ayuda} con instrucciones), '
            f'{len(h["dimensiones"])} dimensiones, encabezados en fila {h["fila_encabezados"]}'
        )
    print(f"  catalogos distintos:  {len(catalogos)}")
    print(
        f'  tipos propuestos:     {"  ".join(f"{k}={v}" for k, v in resumen["por_tipo"].items())}'
    )
    print(
        f'  confianza:            {"  ".join(f"{k}={v}" for k, v in resumen["por_confianza"].items())}'
    )
    print(f'  obligatorios:         {resumen["obligatorios"]}')
    print(f'  reglas sugeridas:     {resumen["reglas_sugeridas"]}')
    print(f"  anomalias:            {len(anomalias)}")
    por_tipo = defaultdict(int)
    for a in anomalias:
        por_tipo[a["tipo"]] += 1
    for k in sorted(por_tipo):
        print(f"      {k}: {por_tipo[k]}")


if __name__ == "__main__":
    main()
