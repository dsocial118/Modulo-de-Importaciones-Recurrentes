"""Los tipos de regla de validación de RUNAC, y la sugerencia por campo.

Los ocho tipos salen del apartado técnico:
    C:\\CNCPS\\RUNAC\\analisis_funcional\\02_apartado_tecnico.docx

Son configuración: van a las tablas runac_c1_tipo_regla y
runac_c1_tipo_regla_parametro, no a condiciones dentro de un programa.

ADVERTENCIA: las reglas concretas que sugiere este módulo son tentativas. Salen
del nombre del campo y de los ejemplos del apartado técnico, no de mirar datos
reales. Tienen que confirmarse contra la realidad de cada archivo.
"""

from __future__ import annotations

import re

from comun import clave

TIPOS_REGLA = [
    {
        "nombre": "RANGO",
        "descripcion": "Verifica que el valor se encuentre entre un mínimo y un máximo.",
        "parametros": [
            ("minimo", "DECIMAL", True, "Valor mínimo admitido, inclusive."),
            ("maximo", "DECIMAL", True, "Valor máximo admitido, inclusive."),
        ],
    },
    {
        "nombre": "COMPARAR_VALOR",
        "descripcion": "Compara el contenido del campo con un valor determinado.",
        "parametros": [
            ("operador", "TEXTO", True,
             "IGUAL, DISTINTO, MAYOR, MAYOR_IGUAL, MENOR, MENOR_IGUAL, EN_LISTA o NO_EN_LISTA."),
            ("valor", "TEXTO", True, "Valor contra el que se compara."),
        ],
    },
    {
        "nombre": "OBLIGATORIO_SI",
        "descripcion": "Determina que un campo sea obligatorio cuando otro campo cumple una condición.",
        "parametros": [
            ("campo_condicion", "CAMPO", True, "Campo cuyo valor dispara la obligatoriedad."),
            ("operador", "TEXTO", True,
             "IGUAL, DISTINTO, ES_VACIO, NO_ES_VACIO, EN_LISTA o NO_EN_LISTA."),
            ("valor_condicion", "TEXTO", False, "Valor de la condición, cuando el operador lo requiere."),
        ],
    },
    {
        "nombre": "COMPARAR_CAMPO",
        "descripcion": "Compara el contenido del campo con otro campo del mismo registro.",
        "parametros": [
            ("campo_comparacion", "CAMPO", True, "Campo del mismo registro contra el que se compara."),
            ("operador", "TEXTO", True, "IGUAL, DISTINTO, MAYOR, MAYOR_IGUAL, MENOR o MENOR_IGUAL."),
        ],
    },
    {
        "nombre": "FORMATO",
        "descripcion": "Verifica que el contenido respete un formato determinado.",
        "parametros": [("formato", "TEXTO", True, "Patrón esperado, por ejemplo NN-NNNNNNNN-N.")],
    },
    {
        "nombre": "UNICO_EN_HOJA",
        "descripcion": "Verifica que el valor no se repita dentro de la misma hoja importada.",
        "parametros": [],
    },
    {
        "nombre": "UNICO_COMBINADO",
        "descripcion": "Verifica que no se repita una combinación determinada de campos.",
        "parametros": [("campos_combinados", "LISTA", True,
                        "Nombres de los campos que en conjunto no pueden repetirse.")],
    },
    {
        "nombre": "EJECUTAR_FUNCION",
        "descripcion": "Ejecuta una función de validación implementada y habilitada previamente en SISOC.",
        "parametros": [("funcion", "TEXTO", True,
                        "Nombre de la función habilitada, por ejemplo validar_cuil.")],
    },
]

# Campos que sólo tienen sentido cuando otro campo dice que sí.
DEPENDIENTES = [
    (r"\bpueblo originario\b.*\bespecificar\b|\bpueblo originario \(especificar\)",
     r"\bse identifica con algun pueblo originario\b", "Sí"),
    (r"\btipo de discapacidad\b", r"\bpresenta alguna discapacidad\b", "Si"),
    (r"\bposee cud\b", r"\bpresenta alguna discapacidad\b", "Si"),
]

# Pares de fechas: la segunda no puede ser anterior a la primera.
PARES_FECHA = [
    (r"\begreso\b", r"\bingreso\b"),
    (r"\bcese\b", r"\bfecha de la medida\b|\binicio\b"),
    (r"\bfinalizacion\b|\bfin\b", r"\binicio\b"),
    (r"\bsalida\b", r"\bentrada\b"),
]


def sugerir_reglas(col: dict, todas: list[dict]) -> list[dict]:
    t = clave(col.get("titulo", ""))
    sug: list[dict] = []

    def agregar(tipo, parametros, motivo, confianza, severidad):
        sug.append({
            "tipo_regla": tipo, "parametros": parametros, "motivo": motivo,
            "confianza": confianza, "severidad": severidad,
        })

    # --- identidad ---
    if re.search(r"\bcuil\b|\bcuit\b", t):
        agregar("EJECUTAR_FUNCION", {"funcion": "validar_cuil"},
                "el campo es un CUIL y el apartado técnico ya prevé esa función", "alta", "BLOQUEANTE")
        agregar("FORMATO", {"formato": "NN-NNNNNNNN-N"},
                "formato de CUIL indicado como ejemplo en el apartado técnico", "media", "ADVERTENCIA")
    if re.search(r"\bmail\b|\bcorreo\b|\be-?mail\b", t):
        agregar("EJECUTAR_FUNCION", {"funcion": "validar_mail"},
                "el campo es una dirección de correo", "alta", "ADVERTENCIA")
    if re.search(r"\bdni\b", t) and "referente" not in t:
        agregar("UNICO_EN_HOJA", {},
                "el requerimiento pide que en un mismo Excel no haya un DNI repetido", "alta", "BLOQUEANTE")

    # --- rangos ---
    if re.search(r"\bedad\b", t):
        agregar("RANGO", {"minimo": 0, "maximo": 17},
                "el registro es de niños, niñas y adolescentes", "baja", "ADVERTENCIA")
    if col.get("tipo_dato") == "FECHA":
        agregar("COMPARAR_VALOR", {"operador": "MENOR_IGUAL", "valor": "HOY"},
                "una fecha registrada no debería ser futura", "media", "ADVERTENCIA")

        for patron_fin, patron_inicio in PARES_FECHA:
            if not re.search(patron_fin, t):
                continue
            inicio = next((o for o in todas
                           if o is not col and o.get("tipo_dato") == "FECHA"
                           and re.search(patron_inicio, clave(o.get("titulo", "")))), None)
            if inicio:
                agregar("COMPARAR_CAMPO",
                        {"campo_comparacion": inicio["nombre_tecnico"], "operador": "MAYOR_IGUAL"},
                        f'"{col["titulo"]}" no puede ser anterior a "{inicio["titulo"]}"',
                        "alta", "BLOQUEANTE")
                break

    # --- obligatoriedad condicional ---
    for patron, patron_disp, valor in DEPENDIENTES:
        if not re.search(patron, t):
            continue
        disp = next((o for o in todas if o is not col
                     and re.search(patron_disp, clave(o.get("titulo", "")))), None)
        if disp:
            agregar("OBLIGATORIO_SI",
                    {"campo_condicion": disp["nombre_tecnico"], "operador": "IGUAL", "valor_condicion": valor},
                    f'sólo tiene sentido completarlo cuando "{disp["titulo"]}" es "{valor}"',
                    "media", "ADVERTENCIA")

    if (re.search(r"\bespecificar\b|\botros\b|\bcual\b", t)
            and not any(s["tipo_regla"] == "OBLIGATORIO_SI" for s in sug)):
        previo = next((o for o in todas if o.get("orden") == col.get("orden", 0) - 1
                       and o.get("catalogo_huella")), None)
        if previo:
            agregar("OBLIGATORIO_SI",
                    {"campo_condicion": previo["nombre_tecnico"], "operador": "EN_LISTA",
                     "valor_condicion": "Otros"},
                    f'es el campo de detalle de "{previo["titulo"]}"', "baja", "ADVERTENCIA")

    return sug


def sugerir_reglas_de_hoja(hoja: dict) -> list[dict]:
    """Reglas que aplican a la hoja entera, no a un campo puntual."""
    cols = hoja["columnas"]
    dni = next((c for c in cols
                if re.search(r"\bdni\b", clave(c["titulo"])) and "referente" not in clave(c["titulo"])), None)
    fecha = next((c for c in cols if c.get("tipo_dato") == "FECHA"
                  and re.search(r"\bmedida\b|\bingreso\b|\binicio\b", clave(c["titulo"]))), None)
    if not (dni and fecha):
        return []
    return [{
        "tipo_regla": "UNICO_COMBINADO",
        "parametros": {"campos_combinados": [dni["nombre_tecnico"], fecha["nombre_tecnico"]]},
        "motivo": "el apartado técnico da como ejemplo no repetir la combinación de documento y fecha de inicio de la medida",
        "confianza": "media", "severidad": "BLOQUEANTE",
        "aplicar_a": dni["nombre_tecnico"],
    }]
