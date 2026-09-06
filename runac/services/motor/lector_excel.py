"""Lectura de un archivo Excel con openpyxl, la misma librería que usa SISOC.

Devuelve estructuras simples (diccionarios y listas) para que el resto de las
herramientas no dependan de openpyxl.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from openpyxl import load_workbook
from openpyxl.utils import get_column_letter, column_index_from_string

from comun import clase_de_formato, norm


@dataclass
class Hoja:
    nombre: str
    indice: int
    estado: str
    max_fila: int
    max_columna: int
    celdas: dict            # (fila, columna) -> valor
    formatos: dict          # columna -> formato de celda predominante
    combinadas: list        # (fila1, col1, fila2, col2)
    validaciones: list      # listas desplegables
    columnas_ancho: dict = field(default_factory=dict)


def _rango(celda_rango) -> tuple[int, int, int, int]:
    return (celda_rango.min_row, celda_rango.min_col, celda_rango.max_row, celda_rango.max_col)


def _rangos_de_sqref(sqref) -> list[tuple[int, int, int, int]]:
    """Una validación puede cubrir varios rangos sueltos."""
    salida = []
    for r in sqref.ranges if hasattr(sqref, "ranges") else [sqref]:
        salida.append(_rango(r))
    return salida


def _valores_literales(formula: str | None) -> list[str] | None:
    """La lista escrita dentro de la validación: "a,b,c" -> [a, b, c]."""
    if not formula:
        return None
    f = str(formula).strip()
    if not f.startswith('"'):
        return None
    return f.strip('"').split(",")


def _referencia_externa(formula: str | None) -> dict | None:
    """La lista que vive en otra hoja: DESPLEGABLE!$K$2:$K$26."""
    import re

    if not formula:
        return None
    m = re.fullmatch(r"'?([^'!]+)'?!(\$?[A-Z]+\$?\d+(?::\$?[A-Z]+\$?\d+)?)", str(formula).strip())
    if not m:
        return None
    return {"hoja": m.group(1), "rango": m.group(2)}


def leer(ruta: str) -> list[Hoja]:
    """Lee todas las hojas del archivo.

    Se abre dos veces a propósito: una con los valores y otra conservando los
    estilos, porque openpyxl no permite tener ambos con read_only.
    """
    wb = load_workbook(ruta, data_only=True, read_only=False, keep_vba=False)
    hojas: list[Hoja] = []

    for indice, ws in enumerate(wb.worksheets, start=1):
        celdas: dict[tuple[int, int], object] = {}
        # Estilos por columna, contando también las celdas vacías con formato:
        # en una plantilla sin datos son la única pista del tipo esperado.
        estilos_por_columna: dict[int, dict[str, int]] = {}
        max_fila = 0
        max_col = 0

        for fila in ws.iter_rows():
            for celda in fila:
                fmt = celda.number_format
                if fmt and fmt != "General":
                    estilos_por_columna.setdefault(celda.column, {})
                    estilos_por_columna[celda.column][fmt] = estilos_por_columna[celda.column].get(fmt, 0) + 1
                valor = celda.value
                if valor is None or (isinstance(valor, str) and valor.strip() == ""):
                    continue
                celdas[(celda.row, celda.column)] = valor
                max_fila = max(max_fila, celda.row)
                max_col = max(max_col, celda.column)

        # Formato aplicado a la columna entera.
        for letra, dim in (ws.column_dimensions or {}).items():
            fmt = getattr(dim, "number_format", None)
            if fmt and fmt != "General":
                try:
                    idx = column_index_from_string(letra)
                except ValueError:
                    continue
                estilos_por_columna.setdefault(idx, {})
                estilos_por_columna[idx][fmt] = estilos_por_columna[idx].get(fmt, 0) + 1000

        formatos = {}
        for col, conteo in estilos_por_columna.items():
            formatos[col] = max(conteo.items(), key=lambda kv: kv[1])[0]

        combinadas = [_rango(r) for r in ws.merged_cells.ranges]

        validaciones = []
        for dv in ws.data_validations.dataValidation:
            if dv.type != "list":
                continue
            for r in _rangos_de_sqref(dv.sqref):
                validaciones.append({
                    "fila_desde": r[0], "col_desde": r[1],
                    "fila_hasta": r[2], "col_hasta": r[3],
                    "formula": dv.formula1,
                    "literal": _valores_literales(dv.formula1),
                    "referencia": _referencia_externa(dv.formula1),
                    # allowBlank falso significa que la celda no admite quedar vacía.
                    "admite_vacio": bool(dv.allowBlank),
                    "mensaje_error": dv.error,
                    "mensaje_ayuda": dv.prompt,
                })

        hojas.append(Hoja(
            nombre=ws.title,
            indice=indice,
            estado=ws.sheet_state,
            max_fila=max_fila,
            max_columna=max_col,
            celdas=celdas,
            formatos=formatos,
            combinadas=combinadas,
            validaciones=validaciones,
        ))

    wb.close()
    return hojas


def valor(hoja: Hoja, fila: int, columna: int):
    v = hoja.celdas.get((fila, columna))
    return None if v is None else v


def texto(hoja: Hoja, fila: int, columna: int) -> str:
    return norm(hoja.celdas.get((fila, columna)))


def formato_de(hoja: Hoja, columna: int) -> str:
    return hoja.formatos.get(columna, "General")


def clase_formato_de(hoja: Hoja, columna: int) -> str:
    return clase_de_formato(formato_de(hoja, columna))


def letra(columna: int) -> str:
    return get_column_letter(columna)
