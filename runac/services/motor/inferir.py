"""Propone tipo de dato, longitud y obligatoriedad para cada campo.

Todo lo que sale de acá es una PROPUESTA, no una verdad. Cada una viene con:

  - de dónde salió: evidencia dura del archivo, o suposición por el nombre;
  - qué confianza merece.

Es la misma exigencia que se le pide a una afirmación técnica: si no se puede
señalar de dónde sale, hay que decir que es una inferencia.
"""

from __future__ import annotations

import re

from comun import clase_de_formato, clave

# --- pistas por el nombre del campo ----------------------------------------
# Orden importante: gana la primera que coincida.
PISTAS = [
    (
        # «ingreso», «egreso» y «alta» NO alcanzan por sí solas: son momentos,
        # y lo que se informa de un momento puede ser la fecha, la hora, la
        # edad o el destino. «Edad al ingreso» es un número y «Especificar
        # destino al egreso» es texto libre, y las dos entraban acá.
        # Una fecha de verdad lo dice: dice «fecha».
        r"\bfecha\b|\bnacimiento\b|\bvencimiento\b",
        "FECHA",
        None,
        None,
    ),
    (r"\bhora\b|\bhorario\b", "HORA", None, None),
    (
        r"\bcuil\b|\bcuit\b",
        "TEXTO",
        13,
        "se guarda como texto para no perder ceros ni guiones",
    ),
    (
        r"\bdni\b|\bdocumento\b.*\bn|\bn[°º]\s*doc",
        "TEXTO",
        15,
        "puede traer puntos, letras o documentos extranjeros",
    ),
    (
        r"\bedad\b|\bcantidad\b|\bcant\.|\btotal\b|\bnumero de\b|\bnro\.? de\b",
        "ENTERO",
        None,
        None,
    ),
    (
        r"\bcodigo postal\b|\bcp\b",
        "TEXTO",
        10,
        "los códigos postales argentinos llevan letras",
    ),
    (r"\btelefono\b|\bcelular\b", "TEXTO", 50, None),
    (r"\bmail\b|\bcorreo\b|\be-?mail\b", "TEXTO", 120, None),
    (r"\bmonto\b|\bimporte\b|\bpesos\b|\bporcentaje\b", "DECIMAL", None, None),
    (r"\bapellido\b|\bnombre\b", "TEXTO", 120, None),
    (r"\bdomicilio\b|\bdireccion\b|\bcalle\b", "TEXTO", 255, None),
    (
        r"\bobservacion|\bcomentario|\bdetalle\b|\bdescripcion\b|\bespecificar\b",
        "TEXTO",
        None,
        "texto libre y largo",
    ),
    (
        r"\bprovincia\b|\blocalidad\b|\bpartido\b|\bmunicipio\b|\bpais\b",
        "TEXTO",
        120,
        None,
    ),
]

# Nombres que NO pueden ser una fecha, por más que la celda tenga formato de
# fecha aplicado.
#
# Hace falta una lista aparte porque el mecanismo que hace ganar al nombre sólo
# se activa cuando el nombre propone OTRO tipo. Un campo llamado «ID familia
# ampliada» no propone nada —no matchea ninguna pista— así que el formato
# ganaba sin oposición, y la columna quedaba declarada FECHA.
#
# Acá el nombre no propone: VETA. Y el veto queda documentado como conflicto,
# igual que cuando propone.
NUNCA_ES_FECHA = [
    (r"\bid\b|\bidentificador\b", "es un identificador"),
    (r"\bhora\b", "es una hora, no una fecha"),
    (r"\bedad\b|\bcantidad\b|\bcant\.|\btotal\b", "cuenta algo"),
    (r"\bespecificar\b|\bespecifique\b", "es el texto libre de otro campo"),
    (r"\bnombre\b|\bapellido\b", "es un nombre"),
]


def _veto_de_fecha(titulo_clave: str):
    """Si el nombre prohíbe que sea una fecha, devuelve por qué."""
    for patron, motivo in NUNCA_ES_FECHA:
        if re.search(patron, titulo_clave):
            return motivo
    return None


# Campos que, por su rol, suelen ser imprescindibles para identificar la fila.
IDENTIFICATORIOS = [
    r"\bapellido\b",
    r"\bnombre/?s?\b",
    r"\bdni\b",
    r"\bcuil\b",
    r"\bfecha del relevamiento\b",
    r"\bfecha de nacimiento\b",
]


def _pista_por_nombre(titulo_clave: str):
    for patron, tipo, largo, nota in PISTAS:
        if re.search(patron, titulo_clave):
            return {"tipo": tipo, "largo": largo, "nota": nota}
    return None


def _obligatoriedad(col: dict, titulo_clave: str) -> tuple[bool, str, str]:
    """Decide si un campo se propone como obligatorio, y con qué respaldo."""
    if col.get("no_admite_vacio_explicito"):
        return (
            True,
            "alta",
            "la validación de Excel declara explícitamente que no admite celdas vacías",
        )
    if any(re.search(p, titulo_clave) for p in IDENTIFICATORIOS):
        return True, "baja", "supuesto: es un campo que identifica la fila"
    return False, "baja", "valor por defecto: el archivo no marca obligatoriedad"


def inferir_campo(
    col: dict,
    tiene_catalogo: bool = False,
    cantidad_valores: int = 0,
    largo_maximo_valor: int = 0,
) -> dict:
    """Propone la definición de un campo.

    `col` trae, como mínimo: titulo, formato, muestras, no_admite_vacio.
    """
    t = clave(col.get("titulo", ""))
    por_nombre = _pista_por_nombre(t)

    tipo = None
    confianza = None
    origen = None
    largo = "sin definir"
    nota = None
    conflicto = None

    # Una lista de valores manda sobre el formato de celda. Si la columna sólo
    # admite "Masculino, Femenino, Otros", no es una fecha por más que tenga
    # formato de fecha aplicado: el formato está mal puesto.
    if tiene_catalogo and clase_de_formato(col.get("formato")) in (
        "fecha",
        "entero",
        "decimal",
    ):
        conflicto = {
            "segun_formato": clase_de_formato(col.get("formato")).upper(),
            "segun_nombre": "TEXTO",
            "detalle": (
                f'La columna tiene formato "{col.get("formato")}" pero su lista de valores '
                f"admite {cantidad_valores} opciones de texto. El formato está mal aplicado."
            ),
        }
        return {
            "tipo_dato": "TEXTO",
            "longitud_maxima": (
                max(largo_maximo_valor, 20) if largo_maximo_valor else 255
            ),
            "obligatorio": _obligatoriedad(col, t)[0],
            "conflicto_de_tipo": conflicto,
            "inferencia": {
                "tipo": {
                    "valor": "TEXTO",
                    "confianza": "alta",
                    "origen": f"lista de {cantidad_valores} valores, por encima del formato de celda",
                    "nota": None,
                },
                "longitud": {
                    "valor": largo_maximo_valor or 255,
                    "origen": "medido sobre los valores del catálogo",
                },
                "obligatorio": dict(
                    zip(("valor", "confianza", "origen"), _obligatoriedad(col, t))
                ),
            },
        }

    # Si el mismo formato está aplicado a casi todas las columnas de la hoja, no
    # es una decisión sobre cada campo: es un formato puesto en bloque.
    formato_masivo = col.get("formato_masivo", False)

    # 1. Evidencia dura: el formato de celda que Excel guarda.
    clase = "general" if formato_masivo else clase_de_formato(col.get("formato"))

    # ...salvo que el nombre lo prohíba. Un formato de fecha sobre una columna
    # que se llama «ID algo» es un formato mal aplicado, no un dato de fecha.
    veto = _veto_de_fecha(t) if clase == "fecha" else None
    if veto:
        conflicto = {
            "segun_formato": "FECHA",
            "segun_nombre": (por_nombre or {}).get("tipo") or "TEXTO",
            "detalle": (
                f'El formato de celda es "{col.get("formato")}", pero el campo se llama '
                f'"{col.get("titulo")}" y {veto}. El formato está mal aplicado.'
            ),
        }
        clase = "general"

    if clase == "fecha":
        tipo, confianza, origen = (
            "FECHA",
            "alta",
            f'formato de celda "{col.get("formato")}"',
        )
    elif clase == "decimal":
        tipo, confianza, origen = (
            "DECIMAL",
            "alta",
            f'formato de celda "{col.get("formato")}"',
        )
    elif clase == "entero":
        tipo, confianza, origen = (
            "ENTERO",
            "alta",
            f'formato de celda "{col.get("formato")}"',
        )
    elif clase == "hora":
        tipo, confianza = "HORA", "alta"
        origen = f'formato de celda "{col.get("formato")}"'
        nota = None

    # 2. Evidencia dura: si tiene lista de valores, es texto de un catálogo.
    if tipo is None and tiene_catalogo:
        tipo, confianza = "TEXTO", "alta"
        largo = max(largo_maximo_valor, 20) if largo_maximo_valor else 255
        origen = f"lista de {cantidad_valores} valores"

    # 3. Evidencia dura: los datos cargados, si los hay.
    muestras = col.get("muestras") or []
    if tipo is None and len(muestras) >= 3:
        if all(re.fullmatch(r"-?\d+([.,]\d+)?", str(v).strip()) for v in muestras):
            con_decimales = any(re.search(r"[.,]\d", str(v)) for v in muestras)
            tipo = "DECIMAL" if con_decimales else "ENTERO"
            confianza = "media"
            origen = f"los {len(muestras)} valores cargados son numéricos"

    # Un formato de celda sin nada que lo respalde no merece «confianza alta».
    # El formato lo pone quien arma la planilla, a veces a lo ancho de la hoja y
    # sin mirar la columna; un nombre que dice lo mismo es otra cosa. Bajarlo a
    # «media» hace que aparezca como INFERIDO en el Excel de supuestos, que es
    # donde una persona lo mira. Fue lo que faltó con «Familia» y «Familia
    # Ampliada», que no tienen nada en el nombre para apoyarse.
    if confianza == "alta" and origen and origen.startswith("formato") and not por_nombre:
        confianza = "media"

    # El formato y el nombre se contradicen: pasa cuando la planilla quedó mal
    # formateada. Gana el nombre, y queda documentado.
    if (
        tipo
        and por_nombre
        and por_nombre["tipo"] != tipo
        and origen
        and origen.startswith("formato")
    ):
        conflicto = {
            "segun_formato": tipo,
            "segun_nombre": por_nombre["tipo"],
            "detalle": (
                f'El formato de celda es "{col.get("formato")}" ({tipo}), pero el campo se llama '
                f'"{col.get("titulo")}", que corresponde a {por_nombre["tipo"]}.'
            ),
        }
        tipo = por_nombre["tipo"]
        largo = por_nombre["largo"]
        nota = por_nombre["nota"]
        confianza = "media"
        origen = f'el nombre del campo, por encima del formato de celda "{col.get("formato")}"'

    # 4. Suposición: el nombre del campo.
    if tipo is None and por_nombre:
        tipo, confianza = por_nombre["tipo"], "baja"
        largo, nota = por_nombre["largo"], por_nombre["nota"]
        origen = "supuesto por el nombre del campo"

    # 5. Por defecto.
    if tipo is None:
        tipo, confianza, largo = "TEXTO", "baja", 255
        origen = "valor por defecto: no hay ninguna señal en el archivo"

    # Longitud: sólo aplica a TEXTO.
    if tipo != "TEXTO":
        largo = None
    elif largo == "sin definir":
        if muestras:
            largo_medido = max(len(str(v)) for v in muestras)
            largo = min(255, max(50, -(-int(largo_medido * 1.5) // 10) * 10))
        else:
            largo = 255

    obligatorio, oblig_confianza, oblig_origen = _obligatoriedad(col, t)

    return {
        "tipo_dato": tipo,
        "longitud_maxima": largo,
        "obligatorio": obligatorio,
        "conflicto_de_tipo": conflicto,
        "inferencia": {
            "tipo": {
                "valor": tipo,
                "confianza": confianza,
                "origen": origen,
                "nota": nota,
            },
            "longitud": {
                "valor": largo,
                "origen": (
                    "no aplica"
                    if largo is None
                    else ("medido sobre los datos" if muestras else "propuesto")
                ),
            },
            "obligatorio": {
                "valor": obligatorio,
                "confianza": oblig_confianza,
                "origen": oblig_origen,
            },
        },
    }
