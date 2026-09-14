"""Utilidades compartidas por las herramientas de la Capa 1 de RUNAC.

Mismas versiones que SISOC: Python 3.11.15, openpyxl 3.1.5.
Todo lo que se escriba acá tiene que poder mudarse al repositorio sin
depender de nada que SISOC no tenga.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from typing import Iterable

# Textos que las planillas usan como "todavía no elegí nada". No son valores.
PLACEHOLDERS = {
    "seleccionar",
    "elegir",
    "elija una opcion",
    "seleccione",
    "-",
    "--",
}


def norm(valor) -> str:
    """Recorta espacios (incluido el no separable) y colapsa los repetidos."""
    if valor is None:
        return ""
    return re.sub(r"\s+", " ", str(valor).replace("\xa0", " ").strip())


def clave(valor) -> str:
    """Forma comparable de un texto: sin tildes, en minúsculas, sin espacios de más.

    Sirve para decidir si dos textos "son el mismo" a los ojos de una persona,
    aunque para la computadora sean distintos.
    """
    texto = norm(valor).lower()
    return "".join(
        c
        for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )


def es_placeholder(valor) -> bool:
    return clave(valor) in PLACEHOLDERS


def huella(valores: Iterable[str]) -> str:
    """Identidad de un conjunto de valores, ignorando orden, tildes y mayúsculas.

    Es lo que permite reconocer que la lista de provincias del MPE es la misma
    que la del MPI y no duplicar el catálogo.
    """
    base = "\u0000".join(sorted(clave(v) for v in valores))
    return hashlib.sha1(base.encode("utf-8")).hexdigest()[:12]


# MySQL no admite nombres de columna de más de 64 caracteres, y el nombre
# técnico termina siendo una columna en las tablas de la Capa 2.
LARGO_MAXIMO_NOMBRE = 64


def nombre_tecnico(titulo: str, largo: int = LARGO_MAXIMO_NOMBRE) -> str:
    """Nombre estable de un campo: sin tildes, en minúsculas, con guiones bajos.

    Si el título es muy largo, se corta y se le agrega una firma corta calculada
    sobre el título completo. Así el nombre entra en el límite de MySQL, sigue
    siendo legible y **sigue siendo el mismo cada vez que se procesa el archivo**:
    dos títulos distintos que empiezan igual no terminan con el mismo nombre.
    """
    base = re.sub(r"[^a-z0-9]+", "_", clave(titulo)).strip("_")
    base = re.sub(r"_{2,}", "_", base)
    if not base:
        return "campo"
    if len(base) <= largo:
        return base
    firma = hashlib.sha1(base.encode("utf-8")).hexdigest()[:6]
    return f"{base[:largo - 7].rstrip('_')}_{firma}"


def codificar(texto: str, largo: int = 100) -> str:
    """Código técnico de un catálogo o de una opción."""
    return nombre_tecnico(texto, largo) or "x"


def sha1_archivo(ruta) -> str:
    h = hashlib.sha1()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1024 * 256), b""):
            h.update(bloque)
    return h.hexdigest()


# --- formatos de celda ------------------------------------------------------


def clase_de_formato(fmt: str | None) -> str:
    """Traduce el formato de celda de Excel a una categoría utilizable.

    El formato es la evidencia más fuerte del tipo de dato esperado, y sobrevive
    aunque la celda esté vacía: en una plantilla sin datos es lo único que hay.
    """
    if not fmt or fmt == "General":
        return "general"
    f = re.sub(r"\[[^\]]*\]", "", str(fmt))
    f = re.sub(r'"[^"]*"', "", f)
    if (
        re.search(r"[dy]", f, re.I)
        and re.search(r"[dmy]", f, re.I)
        and not re.fullmatch(r"[hms:.\s]+", f, re.I)
    ):
        return "fecha"
    if re.search(r"[hs]", f, re.I) and ":" in f:
        return "hora"
    if f.strip() == "@":
        return "texto"
    if re.search(r"[0#]", f):
        return "decimal" if re.search(r"[.][0#]", f) else "entero"
    return "general"


def sql_texto(valor) -> str:
    """Escapa un valor para escribirlo en un INSERT."""
    if valor is None:
        return "NULL"
    if isinstance(valor, bool):
        return "1" if valor else "0"
    if isinstance(valor, (int, float)):
        return str(valor)
    escapado = (
        str(valor)
        .replace("\\", "\\\\")
        .replace("'", "''")
        .replace("\r\n", "\\n")
        .replace("\n", "\\n")
    )
    return f"'{escapado}'"


# ---------------------------------------------------------------------------
# Convención de nombres de las tablas receptoras de la Capa 2.
#
# Vive acá porque la usan dos scripts: capa2.py, que crea las tablas, e
# importar.py, que inserta en ellas. El nombre NO se guarda en la base: se
# deduce del archivo, la versión de estructura y la hoja.
# ---------------------------------------------------------------------------

MAX_IDENT = 64  # límite de MySQL para nombres de tabla


def abrev(texto: str, largo: int) -> str:
    return re.sub(r"[^a-z0-9_]", "", str(texto).lower())[:largo]


def nombre_tabla_receptora(
    codigo: str, hoja: str, varias_hojas: bool, version: int
) -> str:
    """runac_c2_<archivo>_v<n>[_<hoja>].

    La versión va en el nombre porque cada versión de estructura tiene su propia
    tabla: los datos de un período conservan la forma que tenían al cargarse.
    """
    if varias_hojas:
        sufijo = f"{abrev(codigo, 12)}_v{version}_{abrev(hoja, 12)}"
    else:
        sufijo = f"{abrev(codigo, 20)}_v{version}"
    return f"runac_c2_{sufijo}"[:MAX_IDENT]


# Instrucciones que las planillas traen pegadas al título de la hoja. No son
# parte del título: le dicen a la provincia qué hacer con el archivo. Van al
# final y separadas por un punto, así que se cortan ahí.
INSTRUCCIONES_EN_EL_TITULO = (
    "modelo para completar y adjuntar",
    "completar y adjuntar",
    "modelo para completar",
)


def titulo_sin_instrucciones(texto: str) -> str:
    """El título de la hoja, sin la instrucción que la planilla le pegó al final.

    «Listado de dispositivos penales. MODELO PARA COMPLETAR Y ADJUNTAR» es un
    título más una consigna. Guardar las dos cosas juntas hace que la consigna
    aparezca en cada pantalla que muestre el título, repetida una vez por
    archivo.
    """
    limpio = norm(texto)
    for parte in reversed(limpio.split(".")):
        if clave(parte).strip() in INSTRUCCIONES_EN_EL_TITULO:
            limpio = limpio[: limpio.rfind(parte)].rstrip(" .")
    return limpio
