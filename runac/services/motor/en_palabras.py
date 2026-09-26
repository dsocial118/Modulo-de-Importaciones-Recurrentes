"""La definición y los problemas de una importación, dichos en palabras.

Lo usan la plantilla (el comentario de cada título), el instructivo (una fila
por campo) y los dos informes de una importación (el archivo para corregir y
el informe). Está en el motor y no en los servicios de Django porque la
plantilla tiene que poder generarse también desde la línea de comandos.

Sin base de datos: todo entra por parámetro. Así se prueba sin MySQL y los
cuatro Excel dicen lo mismo con las mismas palabras.

Antes cada salida armaba su texto por su lado, y el informe mostraba cosas como
«debe ser menor igual hoy» o «es obligatorio cuando X igual "Si"» (pedido del
responsable funcional, 26-09-2026).
"""

from __future__ import annotations

import json
import re

# ---------------------------------------------------------------------------
# La definición de un campo
# ---------------------------------------------------------------------------

QUE_VA = {
    "TEXTO": "Texto",
    "ENTERO": "Número entero",
    "DECIMAL": "Número con decimales",
    "FECHA": "Fecha, como día/mes/año",
    "HORA": "Hora, como hh:mm",
}

OBLIGATORIO, OPCIONAL, SEGUN_OTRO = "Sí", "No", "Según otro dato"

# Hasta cuántas opciones se escriben en el texto. Más que eso se leen en el
# desplegable.
OPCIONES_A_LA_VISTA = 8


def parametros_de(regla: dict) -> dict:
    p = regla.get("parametros") or {}
    return json.loads(p) if isinstance(p, str) else p


def _lista(valores) -> str:
    valores = valores if isinstance(valores, list) else [valores]
    return ", ".join(f"«{v}»" for v in valores)


def regla_en_palabras(regla: dict, titulos: dict[str, str]) -> str:
    """Una regla de la Capa 1, como la diría una persona.

    `titulos` traduce el nombre técnico de un campo a su título: las reglas
    que miran otro campo lo nombran por su nombre técnico.
    """
    p = parametros_de(regla)
    tipo = regla.get("tipo")
    otro = titulos.get(p.get("campo_condicion"), p.get("campo_condicion"))
    if tipo == "COMPARAR_VALOR" and p.get("valor") == "HOY":
        return (
            "No puede ser posterior a hoy."
            if "MENOR" in (p.get("operador") or "")
            else "No puede ser anterior a hoy."
        )
    if tipo == "RANGO":
        return f'Entre {p.get("minimo")} y {p.get("maximo")}.'
    if tipo == "OBLIGATORIO_SI":
        return f"Obligatorio si «{otro}» es {_lista(p.get('valor_condicion'))}."
    if tipo == "PROHIBIDO_SI":
        return (
            f"Tiene que quedar vacío si «{otro}» es {_lista(p.get('valor_condicion'))}."
        )
    if tipo == "UNICO_EN_HOJA":
        return "No se puede repetir en la hoja."
    if tipo == "UNICO_COMBINADO":
        otros = [titulos.get(x, x) for x in p.get("campos_combinados", [])]
        return (
            "No se puede repetir la combinación de "
            + " + ".join(f"«{o}»" for o in otros)
            + "."
        )
    if tipo == "EXISTE_EN_ARCHIVO":
        return f'Tiene que figurar en el {p.get("archivo")} del período.'
    if tipo == "COINCIDE_CON_ARCHIVO":
        return f'Tiene que coincidir con el del {p.get("archivo")}.'
    if tipo == "FORMATO":
        return f'Con el formato {p.get("formato")}.'
    if tipo == "EJECUTAR_FUNCION":
        conocidas = {
            "validar_mail": "Tiene que ser un correo válido.",
            "validar_cuil": "Tiene que ser un CUIL válido: se controla el dígito verificador.",
        }
        if p.get("funcion") in conocidas:
            return conocidas[p["funcion"]]
    return regla.get("mensaje") or regla.get("descripcion") or tipo or ""


def obligatoriedad(campo: dict, reglas: list[dict]) -> str:
    if campo.get("obligatorio"):
        return OBLIGATORIO
    if any(r.get("tipo") == "OBLIGATORIO_SI" for r in reglas):
        return SEGUN_OTRO
    return OPCIONAL


def que_va(campo: dict) -> str:
    if (
        campo.get("catalogo")
        or campo.get("catalogo_codigo")
        or campo.get("catalogo_id")
    ):
        return "Una opción de la lista"
    base = QUE_VA.get(campo.get("tipo_dato"), "Texto")
    if campo.get("tipo_dato") == "TEXTO" and campo.get("longitud_maxima"):
        return f'{base}, hasta {campo["longitud_maxima"]} caracteres'
    return base


def condiciones(reglas: list[dict], titulos: dict[str, str]) -> list[str]:
    """Cuándo pasa a ser obligatorio: va con la obligatoriedad, no con los controles."""
    return [
        regla_en_palabras(r, titulos)
        for r in reglas
        if r.get("tipo") == "OBLIGATORIO_SI"
    ]


def controles(reglas: list[dict], titulos: dict[str, str]) -> list[str]:
    """Los controles del campo; los que sólo avisan dicen «Aviso»."""
    return [
        ("" if r.get("severidad") == "BLOQUEANTE" else "Aviso: ")
        + regla_en_palabras(r, titulos)
        for r in reglas
        if r.get("tipo") != "OBLIGATORIO_SI"
    ]


def comentario_de_titulo(
    campo: dict, reglas: list[dict], opciones: list[str], titulos: dict[str, str]
) -> str:
    """El globo del título de la columna: lo mismo que el instructivo, en corto."""
    ob = obligatoriedad(campo, reglas)
    lineas = [
        {
            OBLIGATORIO: "Obligatorio",
            OPCIONAL: "Opcional",
            SEGUN_OTRO: "Obligatorio según otro dato",
        }[ob],
        f"Qué va: {que_va(campo)}.",
    ]
    if opciones:
        lineas.append(
            "Valores: "
            + (
                ", ".join(opciones)
                if len(opciones) <= OPCIONES_A_LA_VISTA
                else f"{len(opciones)} opciones, en el desplegable"
            )
            + "."
        )
    lineas += condiciones(reglas, titulos)
    lineas += controles(reglas, titulos)
    if campo.get("ayuda"):
        lineas.append(campo["ayuda"].strip())
    return "\n".join(lineas)


# ---------------------------------------------------------------------------
# Un problema encontrado al importar
# ---------------------------------------------------------------------------

# Lo que se muestra en la columna «Gravedad».
GRAVEDAD = {"BLOQUEANTE": "Bloqueante", "ADVERTENCIA": "Advertencia"}


def problema_en_palabras(
    codigo: str, descripcion: str, opciones: list[str] | None = None
) -> str:
    """Qué hay que hacer, sin repetir el valor: el valor está al lado.

    Lo que no se reconoce queda con la descripción del motor tal cual: mejor
    un texto técnico que un texto inventado.
    """
    d = descripcion or ""
    if codigo == "COMPARAR_VALOR" and "hoy" in d:
        if "menor" in d:
            return "Fecha posterior a hoy: tiene que ser de hoy o anterior."
        return "Fecha anterior a hoy: tiene que ser de hoy o posterior."
    if codigo == "RANGO":
        m = re.search(
            r"(mayor|menor) que el (máximo|mínimo) esperado \(([\d.,-]+)\)", d
        )
        if m:
            limite = f"hasta {m[3]}" if m[1] == "mayor" else f"desde {m[3]}"
            return f"Fuera de lo esperable ({limite}): revisalo; si es correcto, puede quedar."
    if codigo == "OBLIGATORIO_SI":
        m = re.search(r"cuando «(.+)» igual «(.+)»", d)
        if m:
            valor = "Sí" if m[2] == "Si" else m[2]
            return f"Falta el dato: es obligatorio porque «{m[1]}» es «{valor}»."
    if codigo == "TIPO_INVALIDO":
        if "fecha" in d:
            return "No es una fecha válida: escribila como día/mes/año."
        if "hora" in d:
            return "No es una hora válida: escribila como hh:mm."
        return "Tiene que ser un número, escrito con cifras."
    if codigo == "UNICO_EN_HOJA":
        m = re.search(r"fila (\d+)", d)
        if m:
            return f"Repetido: ya está en la fila {m[1]} de esta hoja."
    if codigo == "FUERA_DE_CATALOGO":
        if opciones:
            lista = ", ".join(opciones[:6]) + (
                f" y {len(opciones) - 6} más" if len(opciones) > 6 else ""
            )
            return f"No está en la lista: elegí una opción del desplegable ({lista})."
        return "No está en la lista: elegí una opción del desplegable."
    if codigo == "OBLIGATORIO_VACIO":
        return "Dato obligatorio vacío."
    if codigo == "TEXTO_MUY_LARGO":
        m = re.search(r"máximo admitido es (\d+)", d)
        if m:
            return f"Texto demasiado largo: entran hasta {m[1]} caracteres."
    if codigo == "FILA_VACIA_INTERCALADA":
        return "Fila vacía en el medio de los datos: borrala, las filas tienen que ir seguidas."
    return d


def tipo_de_problema(texto: str) -> str:
    """El nombre corto del problema, para contarlos: la frase hasta los dos puntos."""
    return texto.split(":")[0].rstrip(".")


def fecha_legible(valor):
    """Las fechas como se leen acá: el motor guarda año-mes-día."""
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})(?:[ T].*)?", str(valor or ""))
    return f"{m[3]}/{m[2]}/{m[1]}" if m else valor
