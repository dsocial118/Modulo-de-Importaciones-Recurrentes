"""Rescata las validaciones de datos que openpyxl descarta.

Excel guarda las listas desplegables de dos maneras:

  - La forma clásica, con los valores escritos dentro de la propia validación
    ("Sí,No,Sin datos"). openpyxl la lee sin problema.

  - La forma moderna (extensión "x14"), que se usa cuando la lista vive en otra
    hoja del mismo archivo (DESPLEGABLE!$K$2:$K$26). **openpyxl 3.1.5 la
    descarta** y avisa con: "Data Validation extension is not supported and will
    be removed".

En las planillas de RUNAC la segunda forma es la que tiene los catálogos más
grandes: países, provincias, nivel educativo. Perderlas sería perder lo más
importante.

Este módulo abre el .xlsx —que es un archivo comprimido— y lee esas validaciones
del XML. Usa sólo la biblioteca estándar de Python: zipfile y xml.etree.
"""

from __future__ import annotations

import re
import zipfile
from xml.etree import ElementTree as ET

NS = {
    "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "x14": "http://schemas.microsoft.com/office/spreadsheetml/2009/9/main",
    "xm": "http://schemas.microsoft.com/office/excel/2006/main",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}

_RANGO = re.compile(r"\$?([A-Z]+)\$?(\d+)(?::\$?([A-Z]+)\$?(\d+))?$")


def _col_a_num(letras: str) -> int:
    n = 0
    for c in letras:
        n = n * 26 + (ord(c) - 64)
    return n


def _partes_rango(ref: str):
    m = _RANGO.fullmatch(ref.strip())
    if not m:
        return None
    c1 = _col_a_num(m.group(1))
    f1 = int(m.group(2))
    c2 = _col_a_num(m.group(3)) if m.group(3) else c1
    f2 = int(m.group(4)) if m.group(4) else f1
    return (f1, c1, f2, c2)


def _hojas_del_libro(z: zipfile.ZipFile) -> dict[str, str]:
    """Nombre de hoja -> ruta de su XML dentro del archivo."""
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    destino = {
        r.get("Id"): r.get("Target") for r in rels.findall("rel:Relationship", NS)
    }
    salida = {}
    for hoja in wb.findall("main:sheets/main:sheet", NS):
        rid = hoja.get(f"{{{NS['r']}}}id")
        ruta = destino.get(rid, "")
        ruta = ruta.lstrip("/")
        if not ruta.startswith("xl/"):
            ruta = "xl/" + ruta.removeprefix("xl/")
        salida[hoja.get("name")] = ruta
    return salida


def leer(ruta_xlsx: str) -> dict[str, list[dict]]:
    """Devuelve, por nombre de hoja, las validaciones que openpyxl no expone."""
    resultado: dict[str, list[dict]] = {}
    with zipfile.ZipFile(ruta_xlsx) as z:
        try:
            hojas = _hojas_del_libro(z)
        except KeyError:
            return resultado

        for nombre, ruta in hojas.items():
            try:
                xml = z.read(ruta)
            except KeyError:
                continue
            raiz = ET.fromstring(xml)
            encontradas = []
            for dv in raiz.iter(f"{{{NS['x14']}}}dataValidation"):
                if dv.get("type") != "list":
                    continue
                f1 = dv.find(f"{{{NS['x14']}}}formula1/{{{NS['xm']}}}f")
                sq = dv.find(f"{{{NS['xm']}}}sqref")
                if f1 is None or sq is None:
                    continue
                formula = (f1.text or "").strip()
                referencia = None
                m = re.fullmatch(
                    r"'?([^'!]+)'?!(\$?[A-Z]+\$?\d+(?::\$?[A-Z]+\$?\d+)?)", formula
                )
                if m:
                    referencia = {"hoja": m.group(1), "rango": m.group(2)}
                for parte in (sq.text or "").split():
                    r = _partes_rango(parte)
                    if not r:
                        continue
                    encontradas.append(
                        {
                            "fila_desde": r[0],
                            "col_desde": r[1],
                            "fila_hasta": r[2],
                            "col_hasta": r[3],
                            "formula": formula,
                            "literal": None,
                            "referencia": referencia,
                            "admite_vacio": dv.get("allowBlank") == "1",
                            # Distinguir "el autor declaró que no admite vacío" de
                            # "el atributo no está y vale el valor por omisión".
                            # Sólo lo primero es evidencia de obligatoriedad.
                            "admite_vacio_declarado": dv.get("allowBlank") is not None,
                            "mensaje_error": dv.get("error"),
                            "mensaje_ayuda": dv.get("prompt"),
                        }
                    )
            if encontradas:
                resultado[nombre] = encontradas
    return resultado
