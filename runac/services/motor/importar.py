"""Motor de importación de RUNAC.

    python importar.py --carpeta /trabajo/capa1/mock --jurisdiccion Salta --periodo 2026_T1

Lee la configuración de la Capa 1 y la ejecuta. **No sabe qué es el MPI.** Si
mañana llega una planilla distinta, este archivo no cambia: cambia la Capa 1.

El circuito, según Circuito de Importación de Archivos.docx:

  1. Reconocer qué archivos hay en la carpeta.
  2. Validar la estructura: hojas, columnas, orden y títulos.
  3. Leer las filas al staging, tal como vinieron.
  4. Validar cada fila: tipo, obligatoriedad, catálogo y reglas.
  5. Si no hay bloqueantes, pasar a la tabla tipada.
  6. Informar.

Atomicidad por archivo: si un archivo tiene al menos un error bloqueante,
ninguna de sus filas se incorpora a la tabla tipada. Quedan en la cruda para
poder informar.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import unicodedata
from datetime import date, datetime, time

import mysql.connector
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

from comun import nombre_tabla_receptora

CONEXION = dict(
    host=os.environ.get("RUNAC_DB_HOST", "mysql"),
    port=3306,
    user="root",
    password="runac_local",
    database="runac",
)

PLACEHOLDERS = {"seleccionar", "elegir", "elija una opcion", "seleccione", "-", "--"}


class ReglaInvalida(Exception):
    """Una regla que el motor no sabe evaluar.

    Es un problema de configuración de la Capa 1, no del archivo de la
    provincia. Se levanta para que se vea: si el motor devolviera «se cumple»
    ante un tipo de regla o un operador desconocido, la validación quedaría
    apagada sin que nadie se entere, que es la peor forma de fallar.
    """


def clave(v) -> str:
    t = re.sub(r"\s+", " ", str(v or "").replace("\xa0", " ").strip()).lower()
    return "".join(
        c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn"
    )


def norm(v) -> str:
    """Texto normalizado del valor.

    `str(v or "")` sería más corto y estaría mal: en Python el cero es falso, de
    modo que un «0» informado —una capacidad, una cantidad de personal— se
    convertiría en vacío y el dato desaparecería. El cero es un dato.
    """
    if v is None:
        return ""
    return re.sub(r"\s+", " ", str(v).replace("\xa0", " ").strip())


def texto_a_numero(valor) -> str | None:
    """Pasa un número escrito a mano al formato que entiende Python.

    Las provincias escriben en formato argentino: la coma separa decimales y el
    punto separa miles. Pero el punto también se usa como decimal, así que
    borrarlo siempre convertía «1.5» en 15.

    El criterio: un punto es separador de miles **sólo si lo siguen exactamente
    tres dígitos y nada más que dígitos**. En cualquier otro caso es decimal.
    Devuelve None si el texto no parece un número.
    """
    t = norm(valor).replace(" ", "")
    if not t:
        return None
    if "," in t:
        # Con coma presente, el punto sólo puede ser separador de miles.
        return t.replace(".", "").replace(",", ".")
    if re.fullmatch(r"-?\d{1,3}(\.\d{3})+", t):
        return t.replace(".", "")
    return t


def es_placeholder(v) -> bool:
    return clave(v) in PLACEHOLDERS


# ---------------------------------------------------------------------------
# Conversión de valores
# ---------------------------------------------------------------------------


def convertir(valor, tipo: str):
    """Devuelve (valor_convertido, error). Si hay error, el valor es None."""
    if valor is None or norm(valor) == "" or es_placeholder(valor):
        return None, None

    if tipo == "FECHA":
        if isinstance(valor, datetime):
            return valor.date(), None
        if isinstance(valor, date):
            return valor, None
        t = norm(valor)
        for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d/%m/%y"):
            try:
                return datetime.strptime(t, fmt).date(), None
            except ValueError:
                continue
        return None, f'"{t}" no es una fecha válida. El formato esperado es dd/mm/aaaa.'

    if tipo == "HORA":
        # Excel guarda una hora suelta como `time`, y a veces como un `datetime`
        # con una fecha de mentira (1899-12-31) que hay que descartar.
        if isinstance(valor, time):
            return valor, None
        if isinstance(valor, datetime):
            return valor.time(), None
        t = norm(valor)
        for fmt in ("%H:%M:%S", "%H:%M", "%H.%M"):
            try:
                return datetime.strptime(t, fmt).time(), None
            except ValueError:
                continue
        return None, f'"{t}" no es una hora válida. El formato esperado es hh:mm.'

    if tipo == "ENTERO":
        if isinstance(valor, bool):
            return None, "Se esperaba un número entero."
        if isinstance(valor, int):
            return valor, None
        if isinstance(valor, float):
            return (
                (int(valor), None)
                if valor == int(valor)
                else (None, f"{valor} tiene decimales y se esperaba un número entero.")
            )
        t = texto_a_numero(valor) or ""
        if re.fullmatch(r"-?\d+", t):
            return int(t), None
        if re.fullmatch(r"-?\d+\.\d+", t):
            return (
                None,
                f'"{norm(valor)}" tiene decimales y se esperaba un número entero.',
            )
        return None, f'"{norm(valor)}" no es un número entero.'

    if tipo == "DECIMAL":
        if isinstance(valor, (int, float)):
            return float(valor), None
        try:
            return float(texto_a_numero(valor) or ""), None
        except ValueError:
            return None, f'"{norm(valor)}" no es un número.'

    if isinstance(valor, datetime):
        return valor.strftime("%d/%m/%Y"), None
    if isinstance(valor, (date, time)):
        return str(valor), None
    return norm(valor), None


# ---------------------------------------------------------------------------
# Reglas
# ---------------------------------------------------------------------------


def comparar(a, operador: str, b) -> bool:
    if operador in ("IGUAL", "=="):
        return clave(a) == clave(b)
    if operador in ("DISTINTO", "!="):
        return clave(a) != clave(b)
    try:
        if operador == "MAYOR":
            return a > b
        if operador == "MAYOR_IGUAL":
            return a >= b
        if operador == "MENOR":
            return a < b
        if operador == "MENOR_IGUAL":
            return a <= b
    except TypeError:
        return True  # tipos incomparables: no se puede evaluar, no se reporta
    if operador == "EN_LISTA":
        return clave(a) in {clave(x) for x in (b if isinstance(b, list) else [b])}
    if operador == "NO_EN_LISTA":
        return clave(a) not in {clave(x) for x in (b if isinstance(b, list) else [b])}
    raise ReglaInvalida(f"El operador «{operador}» no existe.")


def condicion_se_cumple(par: dict, fila_valores: dict) -> bool:
    """¿Se cumple la condición que dispara la regla?

    La comparten OBLIGATORIO_SI y PROHIBIDO_SI: una exige que el campo esté
    completo y la otra que esté vacío, pero la condición que las dispara se lee
    igual, y por eso se calcula en un solo lugar.
    """
    cond = fila_valores.get(par.get("campo_condicion"))
    operador = par.get("operador", "IGUAL")
    if operador == "ES_VACIO":
        return cond is None or norm(cond) == ""
    if operador == "NO_ES_VACIO":
        return cond is not None and norm(cond) != ""
    return comparar(cond, operador, par.get("valor_condicion"))


def condicion_legible(par: dict) -> str:
    """Cómo se lee la condición en el mensaje que ve quien carga."""
    operador = par.get("operador", "IGUAL").lower().replace("_", " ")
    valor = par.get("valor_condicion")
    if isinstance(valor, list):
        valor = " o ".join(f"«{v}»" for v in valor)
        return f"{operador} {valor}"
    return operador if valor in (None, "") else f"{operador} «{valor}»"


def aplicar_regla(regla: dict, valor, fila_valores: dict, contexto: dict) -> str | None:
    """Devuelve el mensaje de incumplimiento, o None si la regla se cumple."""
    tipo = regla["tipo_regla"]
    par = regla["parametros"] or {}
    vacio = valor is None or norm(valor) == ""

    def titulo(nombre_tecnico):
        """Cómo se llama esa columna en la planilla."""
        titulos = contexto.get("titulos") or {}
        return titulos.get(nombre_tecnico, nombre_tecnico)

    if tipo == "RANGO":
        if vacio or not isinstance(valor, (int, float)):
            return None
        mn, mx = par.get("minimo"), par.get("maximo")
        if mn is not None and valor < mn:
            return f"El valor {valor} es menor que el mínimo esperado ({mn})."
        if mx is not None and valor > mx:
            return f"El valor {valor} es mayor que el máximo esperado ({mx})."
        return None

    if tipo == "COMPARAR_VALOR":
        if vacio:
            return None
        objetivo = par.get("valor")
        if objetivo == "HOY":
            objetivo = date.today()
            if not isinstance(valor, date):
                return None
        if not comparar(valor, par.get("operador", "IGUAL"), objetivo):
            objetivo_legible = "hoy" if par.get("valor") == "HOY" else par.get("valor")
            return f'El valor no cumple la condición: debe ser {par.get("operador", "").lower().replace("_", " ")} {objetivo_legible}.'
        return None

    if tipo == "COMPARAR_CAMPO":
        otro = fila_valores.get(par.get("campo_comparacion"))
        if vacio or otro is None:
            return None
        if not comparar(valor, par.get("operador", "IGUAL"), otro):
            return (
                f"El valor no cumple la condición respecto de "
                f'«{titulo(par.get("campo_comparacion"))}»: debe ser '
                f'{par.get("operador", "").lower().replace("_", " ")} que ese campo.'
            )
        return None

    if tipo == "OBLIGATORIO_SI":
        if condicion_se_cumple(par, fila_valores) and vacio:
            return (
                f'El campo es obligatorio cuando «{titulo(par.get("campo_condicion"))}» '
                f"{condicion_legible(par)}."
            )
        return None

    if tipo == "PROHIBIDO_SI":
        # El reverso de OBLIGATORIO_SI: hay campos que no pueden estar
        # completos. Si la planilla declara que la persona no tiene documento,
        # el número de documento tiene que estar vacío; con las dos cosas
        # cargadas no se sabe cuál de las dos es la verdadera.
        if condicion_se_cumple(par, fila_valores) and not vacio:
            return (
                f'El campo no se completa cuando «{titulo(par.get("campo_condicion"))}» '
                f"{condicion_legible(par)}, y acá dice «{norm(valor)}»."
            )
        return None

    if tipo == "EXISTE_EN_ARCHIVO":
        # La referencia entre archivos: la nómina nombra un dispositivo que
        # tiene que existir en el archivo de dispositivos ya importado. Es la
        # razón por la que hay un orden de importación.
        #
        # Los valores válidos no se consultan fila por fila: se leen una vez
        # antes de procesar el archivo y viajan en el contexto.
        if vacio:
            return None
        conocidos = (contexto.get("referencias") or {}).get(regla["id"])
        if conocidos is None:
            raise ReglaInvalida(
                "no se pudieron leer los valores del archivo referenciado "
                f'({par.get("archivo")}).'
            )
        if clave(valor) not in conocidos:
            return (
                f'No hay ningún registro con «{norm(valor)}» en {par.get("archivo")}. '
                "Hay que corregir el dato o importar antes ese archivo."
            )
        return None

    if tipo == "COINCIDE_CON_ARCHIVO":
        # No alcanza con que el registro exista: el dato que se repite en los
        # dos archivos tiene que decir lo mismo. Si el legajo y la nómina
        # nombran al mismo chico con el mismo ID, el CUIL tiene que coincidir;
        # si no coincide, uno de los dos está mal y no hay forma de saber cuál.
        if vacio:
            return None
        esperados = (contexto.get("coincidencias") or {}).get(regla["id"])
        if esperados is None:
            raise ReglaInvalida(
                "no se pudieron leer los valores del archivo referenciado "
                f'({par.get("archivo")}).'
            )
        llave = clave(fila_valores.get(par.get("clave")))
        if not llave or llave not in esperados:
            # Que la clave exista es trabajo de EXISTE_EN_ARCHIVO. Acá se
            # controla la coincidencia, y nada más: dos mensajes por el mismo
            # problema confunden a quien corrige.
            return None
        esperado = esperados[llave]
        if clave(valor) != esperado:
            return (
                f'No coincide con {par.get("archivo")}: ahí dice «{esperado}» '
                f"y acá dice «{norm(valor)}». Los dos hablan del mismo registro "
                f'({titulo(par.get("clave"))} «{norm(fila_valores.get(par.get("clave")))}»), '
                "así que uno de los dos está mal."
            )
        return None

    if tipo == "FORMATO":
        if vacio:
            return None
        patron = par.get("formato", "")
        # N = un dígito. El resto de los caracteres se toman literales.
        rx = "".join(r"\d" if c == "N" else re.escape(c) for c in patron)
        if not re.fullmatch(rx, norm(valor)):
            return f"El valor no respeta el formato esperado ({patron})."
        return None

    if tipo == "UNICO_EN_HOJA":
        if vacio:
            return None
        vistos = contexto["unicos"].setdefault(regla["id"], {})
        k = clave(valor)
        if k in vistos:
            return f"El valor ya aparece en la fila {vistos[k]} de esta misma hoja."
        vistos[k] = contexto["fila_actual"]
        return None

    if tipo == "UNICO_COMBINADO":
        campos = par.get("campos_combinados") or []
        partes = [clave(fila_valores.get(c)) for c in campos]
        if any(p == "" for p in partes):
            return None
        vistos = contexto["unicos"].setdefault(regla["id"], {})
        k = "|".join(partes)
        if k in vistos:
            return f'La combinación de {", ".join(campos)} ya aparece en la fila {vistos[k]}.'
        vistos[k] = contexto["fila_actual"]
        return None

    if tipo == "EJECUTAR_FUNCION":
        if vacio:
            return None
        funcion = FUNCIONES.get(par.get("funcion"))
        if funcion is None:
            raise ReglaInvalida(
                f'La función «{par.get("funcion")}» no está implementada.'
            )
        return funcion(valor)

    raise ReglaInvalida(f"El tipo de regla «{tipo}» no está implementado.")


def validar_cuil(valor) -> str | None:
    t = re.sub(r"[^0-9]", "", norm(valor))
    if len(t) != 11:
        return "El CUIL debe tener 11 dígitos."
    pesos = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    suma = sum(int(t[i]) * pesos[i] for i in range(10))
    resto = 11 - (suma % 11)
    verificador = 0 if resto == 11 else (9 if resto == 10 else resto)
    if verificador != int(t[10]):
        return "El CUIL no es válido: el dígito verificador no corresponde."
    return None


def validar_mail(valor) -> str | None:
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[A-Za-z]{2,}", norm(valor)):
        return "La dirección de correo no tiene un formato válido."
    return None


FUNCIONES = {"validar_cuil": validar_cuil, "validar_mail": validar_mail}


# ---------------------------------------------------------------------------
# Configuración: se lee de la Capa 1
# ---------------------------------------------------------------------------


def leer_configuracion(cur, periodo: str) -> list[dict]:
    # La configuración de un período es la de las VERSIONES que ese período usa.
    # Si el período siguiente no tuvo cambios, apunta a las mismas versiones.
    cur.execute(
        """
        SELECT a.id AS archivo_id, a.codigo,
               av.id AS version_id, av.numero AS version,
               av.nombre_esperado, av.titulo, av.orden_importacion, av.obligatorio
        FROM mir_c2_periodo_archivo pa
        JOIN mir_c2_periodo p ON p.id = pa.periodo_id
        JOIN mir_c1_archivo_version av ON av.id = pa.archivo_version_id
        JOIN mir_c1_archivo a ON a.id = av.archivo_id
        WHERE p.codigo = %s
        ORDER BY av.orden_importacion
    """,
        (periodo,),
    )
    archivos = cur.fetchall()
    for a in archivos:
        a["id"] = a["archivo_id"]  # compatibilidad con el resto del script
        cur.execute(
            """
            SELECT h.id, h.nombre_esperado, h.fila_encabezados, h.orden_procesamiento, h.obligatoria
            FROM mir_c1_hoja h
            WHERE h.archivo_version_id = %s ORDER BY h.orden_procesamiento
        """,
            (a["version_id"],),
        )
        a["hojas"] = cur.fetchall()
        varias = len(a["hojas"]) > 1
        for h in a["hojas"]:
            # El nombre de la tabla receptora no se guarda: se deduce.
            h["tabla"] = nombre_tabla_receptora(
                a["codigo"], h["nombre_esperado"], varias, a["version"]
            )
        for h in a["hojas"]:
            cur.execute(
                """
                SELECT c.id, c.nombre, c.titulo_esperado, c.orden, c.tipo_dato,
                       c.longitud_maxima, c.obligatorio, cat.codigo AS catalogo
                FROM mir_c1_campo c LEFT JOIN mir_c1_catalogo cat ON cat.id = c.catalogo_id
                WHERE c.hoja_id = %s ORDER BY c.orden
            """,
                (h["id"],),
            )
            h["campos"] = cur.fetchall()
            for campo in h["campos"]:
                campo["opciones"] = {}
                if campo["catalogo"]:
                    # La vigencia se compara como texto porque el código de
                    # período está armado para eso: «2026_T1» < «2026_T2» <
                    # «2027_T1». Una opción que se dio de baja en 2027 sigue
                    # siendo válida en los períodos anteriores, y una que se
                    # agregó después no vale hacia atrás.
                    cur.execute(
                        """
                        SELECT o.id, o.valor_esperado FROM mir_c1_catalogo_opcion o
                        JOIN mir_c1_catalogo c ON c.id = o.catalogo_id
                        WHERE c.codigo = %s AND o.activo = 1
                          AND (o.vigente_desde_periodo IS NULL
                               OR o.vigente_desde_periodo <= %s)
                          AND (o.vigente_hasta_periodo IS NULL
                               OR o.vigente_hasta_periodo >= %s)
                    """,
                        (campo["catalogo"], periodo, periodo),
                    )
                    campo["opciones"] = {
                        clave(r["valor_esperado"]): r for r in cur.fetchall()
                    }
                cur.execute(
                    """
                    SELECT r.id, r.nombre, r.parametros, tr.nombre AS tipo_regla,
                           cr.severidad, cr.mensaje AS mensaje_configurado
                    FROM mir_c1_campo_regla cr
                    JOIN mir_c1_regla r ON r.id = cr.regla_id
                    JOIN mir_c1_tipo_regla tr ON tr.id = r.tipo_regla_id
                    WHERE cr.campo_id = %s
                """,
                    (campo["id"],),
                )
                campo["reglas"] = []
                for r in cur.fetchall():
                    r["parametros"] = (
                        json.loads(r["parametros"]) if r["parametros"] else {}
                    )
                    campo["reglas"].append(r)
    return archivos


# ---------------------------------------------------------------------------
# Proceso
# ---------------------------------------------------------------------------


def reconocer(carpeta: str, archivos: list[dict]) -> tuple[list, list, list]:
    """Empareja los archivos de la carpeta con los que la Capa 1 espera."""
    presentes = [
        f
        for f in sorted(os.listdir(carpeta))
        if f.lower().endswith((".xlsx", ".xlsm")) and not f.startswith("~$")
    ]
    reconocidos, sin_reconocer, ambiguos = [], list(presentes), []
    # Los códigos más largos primero: MPJ_DAE tiene que ganarle a MPJ.
    for a in sorted(archivos, key=lambda x: -len(x["codigo"])):
        candidatos = [
            f
            for f in presentes
            if re.search(
                rf"(^|[^A-Za-z0-9]){re.escape(a['codigo'])}([^A-Za-z0-9]|$)", f, re.I
            )
            and f in sin_reconocer
        ]
        if not candidatos:
            continue
        if len(candidatos) > 1:
            # No se elige por el sistema: el usuario tiene que decir cuál va.
            ambiguos.append({"codigo": a["codigo"], "candidatos": candidatos})
            continue
        elegido = candidatos[0]
        reconocidos.append(
            {"archivo": a, "nombre": elegido, "ruta": os.path.join(carpeta, elegido)}
        )
        sin_reconocer.remove(elegido)
    faltantes = [
        a
        for a in archivos
        if a["obligatorio"]
        and not any(r["archivo"]["codigo"] == a["codigo"] for r in reconocidos)
    ]
    return reconocidos, sin_reconocer, faltantes, ambiguos


def validar_estructura(ruta: str, definicion: dict) -> list[str]:
    """Devuelve la lista de problemas de estructura. Vacía significa que está bien."""
    problemas = []
    try:
        wb = load_workbook(ruta, data_only=True, read_only=True)
    except Exception as e:  # noqa: BLE001
        return [f"El archivo no se pudo abrir: {e}"]

    for hoja in definicion["hojas"]:
        nombre = hoja["nombre_esperado"]
        if nombre not in wb.sheetnames:
            if hoja["obligatoria"]:
                problemas.append(f'Falta la hoja "{nombre}".')
            continue
        ws = wb[nombre]
        fila_enc = hoja["fila_encabezados"]
        titulos = {}
        for fila in ws.iter_rows(min_row=fila_enc, max_row=fila_enc):
            for celda in fila:
                if celda.value is not None:
                    titulos[celda.column] = norm(celda.value).rstrip(" *")
            break
        for campo in hoja["campos"]:
            encontrado = titulos.get(campo["orden"])
            if encontrado is None:
                problemas.append(
                    f'En la hoja "{nombre}" falta la columna {campo["orden"]}: '
                    f'"{campo["titulo_esperado"]}".'
                )
            elif clave(encontrado) != clave(campo["titulo_esperado"]):
                problemas.append(
                    f'En la hoja "{nombre}", la columna {campo["orden"]} dice '
                    f'"{encontrado}" y debería decir "{campo["titulo_esperado"]}".'
                )
    wb.close()
    return problemas


def identificador_seguro(nombre: str) -> str:
    """Lo que se interpola en un SQL tiene que ser lo que la Capa 1 declaró."""
    if not re.fullmatch(r"[a-z0-9_]{1,64}", nombre or ""):
        raise ReglaInvalida(f"«{nombre}» no es un nombre de tabla o columna válido.")
    return nombre


def valores_referenciados(cur, archivos, archivo, presentacion_id) -> dict:
    """Los identificadores que ya existen en los archivos que este referencia.

    Se leen una sola vez, antes de procesar el archivo, y sólo de la
    importación **vigente** de cada archivo referenciado: si la provincia
    reimportó los dispositivos, los identificadores válidos son los de la
    última importación, no los de la que quedó anulada.
    """
    referencias: dict[int, set] = {}
    for hoja in archivo["hojas"]:
        for campo in hoja["campos"]:
            for regla in campo["reglas"]:
                if regla["tipo_regla"] != "EXISTE_EN_ARCHIVO":
                    continue
                par = regla["parametros"] or {}
                destino = next(
                    (a for a in archivos if a["codigo"] == par.get("archivo")), None
                )
                if destino is None:
                    continue
                # Sin hoja declarada se buscan TODAS las del archivo: el
                # dispositivo penal se declara en la hoja que corresponde a su
                # tipo —CRC, CRSC, CAD, MPT…—, y quien nombra el dispositivo en
                # la nómina no tiene por qué saber en cuál está.
                hojas = [
                    h
                    for h in destino["hojas"]
                    if h.get("tabla")
                    and (not par.get("hoja") or h["nombre_esperado"] == par["hoja"])
                ]
                columna = identificador_seguro(par.get("campo"))
                conocidos: set = set()
                for hoja_destino in hojas:
                    tabla = identificador_seguro(hoja_destino["tabla"])
                    if not any(c["nombre"] == columna for c in hoja_destino["campos"]):
                        continue
                    cur.execute(
                        f"""SELECT DISTINCT t.`{columna}` FROM `{tabla}` t
                            JOIN mir_c2_importacion i ON i.id = t.importacion_id
                            WHERE i.presentacion_id = %s AND i.archivo_id = %s
                              AND i.estado = 'VALIDA'""",
                        (presentacion_id, destino["archivo_id"]),
                    )
                    conocidos |= {clave(f[0]) for f in cur.fetchall()}
                referencias[regla["id"]] = conocidos
    return referencias


def valores_a_coincidir(cur, archivos, archivo, presentacion_id) -> dict:
    """Para cada regla de coincidencia, el valor que el otro archivo declara.

    A diferencia de `valores_referenciados`, que junta un conjunto de valores
    válidos, acá hace falta un diccionario: la clave del registro y el valor
    que tiene que coincidir. Se lee una sola vez, igual que el otro.
    """
    coincidencias: dict[int, dict] = {}
    for hoja in archivo["hojas"]:
        for campo in hoja["campos"]:
            for regla in campo["reglas"]:
                if regla["tipo_regla"] != "COINCIDE_CON_ARCHIVO":
                    continue
                par = regla["parametros"] or {}
                destino = next(
                    (a for a in archivos if a["codigo"] == par.get("archivo")), None
                )
                if destino is None:
                    continue
                col_clave = identificador_seguro(par.get("clave"))
                col_valor = identificador_seguro(par.get("campo"))
                encontrados: dict = {}
                for hoja_destino in destino["hojas"]:
                    if not hoja_destino.get("tabla"):
                        continue
                    if (
                        par.get("hoja")
                        and hoja_destino["nombre_esperado"] != par["hoja"]
                    ):
                        continue
                    nombres = {c["nombre"] for c in hoja_destino["campos"]}
                    if col_clave not in nombres or col_valor not in nombres:
                        continue
                    tabla = identificador_seguro(hoja_destino["tabla"])
                    cur.execute(
                        f"""SELECT t.`{col_clave}`, t.`{col_valor}` FROM `{tabla}` t
                            JOIN mir_c2_importacion i ON i.id = t.importacion_id
                            WHERE i.presentacion_id = %s AND i.archivo_id = %s
                              AND i.estado = 'VALIDA'""",
                        (presentacion_id, destino["archivo_id"]),
                    )
                    for k, v in cur.fetchall():
                        if k is not None:
                            encontrados[clave(k)] = clave(v)
                coincidencias[regla["id"]] = encontrados
    return coincidencias


def procesar_hoja(cur, ruta, hoja, importacion_id, contexto_global) -> dict:
    """Lee una hoja, la valida y la deja en staging. Devuelve el resumen."""
    wb = load_workbook(ruta, data_only=True, read_only=True)
    ws = wb[hoja["nombre_esperado"]]
    campos = hoja["campos"]
    fila_enc = hoja["fila_encabezados"]

    hallazgos: list[dict] = []
    filas_crudas: list[tuple] = []
    filas_tipadas: list[tuple] = []
    # Los mensajes se leen: nombran las columnas por su título, no por el
    # nombre técnico con el que las guarda la base.
    contexto = {
        "unicos": {},
        "fila_actual": 0,
        "titulos": {c["nombre"]: c["titulo_esperado"] for c in hoja["campos"]},
        # Una regla que no se puede evaluar se informa una vez, no una por fila.
        "reglas_rotas": set(),
        # Los identificadores que existen en los archivos ya importados.
        "referencias": (contexto_global or {}).get("referencias") or {},
        # Y el valor que esos archivos declaran, para las reglas de coincidencia.
        "coincidencias": (contexto_global or {}).get("coincidencias") or {},
    }
    total = 0
    con_error = 0
    vacias_intercaladas = []
    ultima_con_datos = 0

    # En modo sólo lectura openpyxl devuelve celdas vacías sin número de columna,
    # así que la posición se toma del orden dentro de la fila.
    por_orden = {c["orden"]: c for c in campos}
    for nro, fila in enumerate(ws.iter_rows(min_row=fila_enc + 1), start=fila_enc + 1):
        valores_crudos = {}
        hay_algo = False
        for indice, celda in enumerate(fila, start=1):
            campo = por_orden.get(indice)
            if campo is None:
                continue
            v = celda.value
            valores_crudos[campo["nombre"]] = v
            if v is not None and norm(v) != "" and not es_placeholder(v):
                hay_algo = True

        if not hay_algo:
            continue
        # Filas vacías en el medio: el requerimiento las considera un error.
        if ultima_con_datos and nro > ultima_con_datos + 1:
            for f in range(ultima_con_datos + 1, nro):
                vacias_intercaladas.append(f)
        ultima_con_datos = nro
        total += 1
        contexto["fila_actual"] = nro

        # --- conversión y validaciones por campo ---
        valores_tipados = {}
        errores_fila = 0
        for campo in campos:
            crudo = valores_crudos.get(campo["nombre"])
            valor, error = convertir(crudo, campo["tipo_dato"])

            if error:
                hallazgos.append(
                    dict(
                        codigo="TIPO_INVALIDO",
                        severidad="BLOQUEANTE",
                        campo_id=campo["id"],
                        regla_id=None,
                        fila=nro,
                        campo=campo["titulo_esperado"],
                        columna=get_column_letter(campo["orden"]),
                        valor=norm(crudo),
                        detalle=error,
                    )
                )
                errores_fila += 1
                valores_tipados[campo["nombre"]] = None
                continue

            vacio = valor is None or norm(valor) == ""
            if campo["obligatorio"] and vacio:
                hallazgos.append(
                    dict(
                        codigo="OBLIGATORIO_VACIO",
                        severidad="BLOQUEANTE",
                        campo_id=campo["id"],
                        regla_id=None,
                        fila=nro,
                        campo=campo["titulo_esperado"],
                        columna=get_column_letter(campo["orden"]),
                        valor=None,
                        detalle="El campo es obligatorio y está vacío.",
                    )
                )
                errores_fila += 1

            if campo["opciones"] and not vacio:
                if clave(valor) not in campo["opciones"]:
                    hallazgos.append(
                        dict(
                            codigo="FUERA_DE_CATALOGO",
                            severidad="BLOQUEANTE",
                            campo_id=campo["id"],
                            regla_id=None,
                            fila=nro,
                            campo=campo["titulo_esperado"],
                            columna=get_column_letter(campo["orden"]),
                            valor=norm(valor),
                            detalle=f"El valor no está entre los admitidos para este campo.",
                        )
                    )
                    errores_fila += 1

            largo = campo["longitud_maxima"]
            if (
                largo
                and not vacio
                and campo["tipo_dato"] == "TEXTO"
                and len(str(valor)) > largo
            ):
                hallazgos.append(
                    dict(
                        codigo="TEXTO_MUY_LARGO",
                        severidad="BLOQUEANTE",
                        campo_id=campo["id"],
                        regla_id=None,
                        fila=nro,
                        campo=campo["titulo_esperado"],
                        columna=get_column_letter(campo["orden"]),
                        valor=str(valor)[:60] + "…",
                        detalle=f"El texto tiene {len(str(valor))} caracteres y el máximo admitido es {largo}.",
                    )
                )
                errores_fila += 1

            valores_tipados[campo["nombre"]] = valor

        # --- reglas ---
        for campo in campos:
            for regla in campo["reglas"]:
                try:
                    mensaje = aplicar_regla(
                        regla,
                        valores_tipados.get(campo["nombre"]),
                        valores_tipados,
                        contexto,
                    )
                except ReglaInvalida as falla:
                    # Una regla mal configurada no puede pasar en silencio: el
                    # archivo entraría sin haber sido controlado. Se informa una
                    # sola vez —no una por fila— y bloquea, porque nadie puede
                    # afirmar que estos datos cumplen lo que la regla pedía.
                    if regla["id"] in contexto["reglas_rotas"]:
                        continue
                    contexto["reglas_rotas"].add(regla["id"])
                    hallazgos.append(
                        dict(
                            codigo="REGLA_NO_APLICABLE",
                            severidad="BLOQUEANTE",
                            campo_id=campo["id"],
                            regla_id=regla["id"],
                            fila=nro,
                            campo=campo["titulo_esperado"],
                            columna=get_column_letter(campo["orden"]),
                            valor=None,
                            detalle=(
                                f'La regla «{regla["nombre"]}» no se pudo evaluar: '
                                f"{falla}. Es un problema de configuración: hay que "
                                "avisar a Nación antes de volver a importar."
                            ),
                        )
                    )
                    errores_fila += 1
                    continue
                # El mensaje que redactó la Capa 1 para esta combinación de campo
                # y regla manda sobre el que arma el motor: es el que entiende
                # quien carga, y por eso se puede configurar.
                if mensaje and regla.get("mensaje_configurado"):
                    mensaje = regla["mensaje_configurado"]
                if mensaje:
                    hallazgos.append(
                        dict(
                            codigo=regla["tipo_regla"],
                            severidad=regla["severidad"],
                            campo_id=campo["id"],
                            regla_id=regla["id"],
                            fila=nro,
                            campo=campo["titulo_esperado"],
                            columna=get_column_letter(campo["orden"]),
                            valor=norm(valores_tipados.get(campo["nombre"])),
                            detalle=mensaje,
                        )
                    )
                    if regla["severidad"] == "BLOQUEANTE":
                        errores_fila += 1

        if errores_fila:
            con_error += 1

        estado = "CON_ERROR" if errores_fila else "VALIDA"
        contenido = "|".join(norm(valores_crudos.get(c["nombre"])) for c in campos)
        filas_crudas.append(
            (
                importacion_id,
                nro,
                estado,
                hashlib.sha1(contenido.encode("utf-8")).hexdigest(),
                *[norm(valores_crudos.get(c["nombre"])) or None for c in campos],
            )
        )
        if not errores_fila:
            filas_tipadas.append(
                (
                    importacion_id,
                    nro,
                    *[valores_tipados.get(c["nombre"]) for c in campos],
                )
            )

    wb.close()

    for f in vacias_intercaladas:
        hallazgos.append(
            dict(
                codigo="FILA_VACIA_INTERCALADA",
                severidad="BLOQUEANTE",
                campo_id=None,
                regla_id=None,
                fila=f,
                campo=None,
                valor=None,
                detalle="Hay una fila vacía en el medio de los datos. "
                "El requerimiento pide corregirlo antes de importar.",
            )
        )

    # --- incorporación ---
    # Importación restrictiva: con un solo bloqueante no entra ninguna fila.
    # Por eso hay una sola tabla receptora y no dos: todo lo que se incorpora
    # pudo convertirse a su tipo. El valor que provocó cada incumplimiento queda
    # en mir_c2_reglas_incumplidas.
    cols = ", ".join(f"`{c['nombre']}`" for c in campos)
    bloqueantes = sum(1 for h in hallazgos if h["severidad"] == "BLOQUEANTE")

    # La hoja PREPARA su inserción; no la ejecuta. Quien decide es el archivo,
    # después de sumar los bloqueantes de todas sus hojas.
    #
    # Es lo que hace restrictiva a la importación de verdad: si cada hoja
    # insertara por su cuenta, un archivo de varias hojas podía quedar declarado
    # fallido y conservar igual las filas de las hojas que no tenían errores.
    insercion = None
    if filas_tipadas:
        con_adv = {h["fila"] for h in hallazgos if h["severidad"] == "ADVERTENCIA"}
        marcas = ", ".join(["%s"] * (4 + len(campos)))
        filas = [
            (
                imp,
                nro,
                "CON_ADVERTENCIA" if nro in con_adv else "VALIDA",
                hashlib.sha1(
                    "|".join("" if v is None else str(v) for v in resto).encode("utf-8")
                ).hexdigest(),
                *resto,
            )
            for (imp, nro, *resto) in filas_tipadas
        ]
        insercion = (
            f'INSERT INTO `{hoja["tabla"]}` '
            f"(importacion_id, numero_fila, estado, hash_contenido, {cols}) "
            f"VALUES ({marcas})",
            filas,
        )

    return {
        "hoja": hoja["nombre_esperado"],
        "total": total,
        "con_error": con_error,
        "hallazgos": hallazgos,
        "bloqueantes": bloqueantes,
        "advertencias": sum(1 for h in hallazgos if h["severidad"] == "ADVERTENCIA"),
        "insercion": insercion,
    }


class _Opciones:
    """Los mismos datos que trae la linea de comandos, para poder llamar a la
    importacion desde otro lado (por ejemplo, desde una vista web)."""

    def __init__(
        self,
        carpeta,
        jurisdiccion,
        periodo,
        usuario,
        informe,
        asignacion=None,
        silencioso=False,
    ):
        self.carpeta = carpeta
        self.jurisdiccion = jurisdiccion
        self.periodo = periodo
        self.usuario = usuario
        self.informe = informe
        self.asignacion = asignacion or {}
        self.silencioso = silencioso


def procesar_carpeta(
    carpeta,
    jurisdiccion,
    periodo,
    usuario="mir",
    # Por omisión, al lado de la carpeta que se importa. Quien llama desde la
    # aplicación pasa el suyo: `settings.RUNAC_INFORMES`.
    informe="informes",
    asignacion=None,
    conexion=None,
    silencioso=True,
):
    """Importa una carpeta y devuelve el resumen. Es lo que usa la aplicación."""
    args = _Opciones(
        carpeta, jurisdiccion, periodo, usuario, informe, asignacion, silencioso
    )
    return _ejecutar(args, conexion or CONEXION)


def main():
    p = argparse.ArgumentParser(description="Importa una carpeta de archivos de RUNAC.")
    p.add_argument("--carpeta", required=True)
    p.add_argument("--jurisdiccion", default="Salta")
    p.add_argument("--periodo", default="2026_T1")
    p.add_argument("--usuario", default="prueba")
    p.add_argument("--informe", default="informes")
    args = p.parse_args()
    args.asignacion = {}
    args.silencioso = False
    _ejecutar(args, CONEXION)


# MySQL avisa un abrazo mortal con este número, y lo que pide es exactamente
# esto: volver a intentar. No es un error del archivo ni de las reglas.
DEADLOCK = 1213


def _ejecutar(args, conexion, intentos: int = 2):
    """Abre la conexion, ejecuta la importacion y la cierra SIEMPRE.

    El cierre estaba al final del cuerpo, asi que solo se alcanzaba cuando todo
    salia bien. Una excepcion --o el return temprano cuando hay archivos
    ambiguos-- dejaba la conexion viva con su transaccion en curso, reteniendo
    los bloqueos sobre la presentacion. La importacion siguiente se quedaba
    esperando esos bloqueos y fallaba tambien: un error se convertia en todos
    los errores siguientes, y la unica salida era reiniciar el contenedor.

    Y se reintenta una vez ante un abrazo mortal. Dos importaciones seguidas
    pueden pedirse los mismos bloqueos en distinto orden --al anular la anterior
    y al registrar la nueva-- y MySQL corta una de las dos. No es un error del
    archivo: es lo que la base pide que se haga, y aparecer como una pantalla de
    error por algo que se resuelve reintentando es peor que reintentar.
    """
    ultimo = None
    for intento in range(intentos):
        cn = mysql.connector.connect(**conexion)
        try:
            return _ejecutar_con(args, cn)
        except mysql.connector.errors.InternalError as falla:
            if falla.errno != DEADLOCK or intento == intentos - 1:
                raise
            ultimo = falla
        finally:
            try:
                # Lo que no se confirmo no queda a medias esperando a nadie.
                cn.rollback()
            finally:
                cn.close()
    raise ultimo  # pragma: no cover — no se llega salvo con intentos=0


def _ejecutar_con(args, cn):
    imprimir = (lambda *a, **k: None) if getattr(args, "silencioso", False) else print

    cur = cn.cursor(dictionary=True)
    archivos = leer_configuracion(cur, args.periodo)

    imprimir(f"Carpeta: {args.carpeta}")
    imprimir(f"Jurisdicción: {args.jurisdiccion} · Período: {args.periodo}\n")

    reconocidos, sin_reconocer, faltantes, ambiguos = reconocer(args.carpeta, archivos)

    if getattr(args, "asignacion", None):
        por_codigo = {a["codigo"]: a for a in archivos}
        forzados = []
        for nombre, codigo in args.asignacion.items():
            definicion = por_codigo.get(codigo)
            ruta = os.path.join(args.carpeta, nombre)
            if not definicion or not os.path.exists(ruta):
                continue
            forzados.append({"archivo": definicion, "nombre": nombre, "ruta": ruta})
            if nombre in sin_reconocer:
                sin_reconocer.remove(nombre)
        if forzados:
            codigos = {f["archivo"]["codigo"] for f in forzados}
            nombres = {f["nombre"] for f in forzados}
            reconocidos = forzados + [
                r
                for r in reconocidos
                if r["archivo"]["codigo"] not in codigos and r["nombre"] not in nombres
            ]
            faltantes = [a for a in faltantes if a["codigo"] not in codigos]
            ambiguos = []
    imprimir("== Reconocimiento ==")
    for r in sorted(reconocidos, key=lambda x: x["archivo"]["orden_importacion"]):
        imprimir(f'   OK   {r["nombre"][:52]:54} -> {r["archivo"]["codigo"]}')
    for am in ambiguos:
        imprimir(
            f'   !!   {am["codigo"]}: hay {len(am["candidatos"])} archivos que podrían serlo, '
            f"hay que elegir uno"
        )
        for c in am["candidatos"]:
            imprimir(f"          · {c}")
    for f in sin_reconocer:
        imprimir(f"   ??   {f[:52]:54} no se pudo reconocer")
    for a in faltantes:
        imprimir(f'   --   falta: {a["codigo"]} (obligatorio)')
    if ambiguos:
        imprimir("\nNo se procesa nada hasta resolver las ambigüedades.")
        return
    imprimir()

    # Presentación del período.
    cur2 = cn.cursor()
    cur2.execute("SELECT id FROM mir_c2_periodo WHERE codigo=%s", (args.periodo,))
    fila = cur2.fetchone()
    if not fila:
        raise SystemExit(f"No existe el período {args.periodo}.")
    periodo_id = fila[0]

    # La jurisdicción es una entidad: si no existe, se da de alta.
    cur2.execute(
        "SELECT id FROM mir_c2_jurisdiccion WHERE codigo=%s OR nombre=%s",
        (args.jurisdiccion.upper(), args.jurisdiccion),
    )
    fila = cur2.fetchone()
    if fila:
        jurisdiccion_id = fila[0]
    else:
        cur2.execute(
            """INSERT INTO mir_c2_jurisdiccion (codigo, nombre, modalidad, activa)
                        VALUES (%s, %s, 'PRESENTACION_PERIODICA', 1)""",
            (args.jurisdiccion.upper()[:20], args.jurisdiccion),
        )
        jurisdiccion_id = cur2.lastrowid

    # Si la presentación ya existe se la deja como está. Antes decía
    # `ON DUPLICATE KEY UPDATE estado='EN_CARGA'`, de modo que importar un
    # archivo reabría una presentación cerrada, revisada o ya presentada sin
    # que nadie lo decidiera. Quién puede reabrirla y cuándo es una decisión
    # del circuito, no un efecto de subir un archivo.
    cur2.execute(
        """INSERT INTO mir_c2_presentacion (periodo_id, jurisdiccion_id, version, estado)
                    VALUES (%s, %s, 1, 'EN_CARGA')
                    ON DUPLICATE KEY UPDATE id = id""",
        (periodo_id, jurisdiccion_id),
    )

    def buscar_presentacion():
        cur2.execute(
            """SELECT id FROM mir_c2_presentacion
                        WHERE periodo_id=%s AND jurisdiccion_id=%s AND version=1""",
            (periodo_id, jurisdiccion_id),
        )
        return cur2.fetchone()

    # Si no aparece, se confirma y se vuelve a mirar. No es terquedad: la
    # transaccion viene leyendo la Capa 1 desde antes, y en MySQL una lectura
    # sigue viendo la foto del momento en que empezo. Si otra conexion creo la
    # presentacion despues de esa foto --el boton de borrar importaciones, o
    # armar la demostracion--, el INSERT de arriba no hizo nada porque la fila
    # ya existia, y este SELECT tampoco la ve. Confirmar cierra la transaccion
    # y la siguiente lectura saca una foto nueva.
    fila = buscar_presentacion()
    if not fila:
        cn.commit()
        fila = buscar_presentacion()
    if not fila:
        raise RuntimeError(
            f"No se pudo obtener la presentacion de {args.jurisdiccion} para "
            f"{args.periodo}. Suele ser un bloqueo dejado por una importacion "
            "anterior que fallo; volver a intentar."
        )
    presentacion_id = fila[0]

    resumen_general = []
    imprimir("== Procesamiento ==")
    for r in sorted(reconocidos, key=lambda x: x["archivo"]["orden_importacion"]):
        a = r["archivo"]
        inicio = datetime.now()
        with open(r["ruta"], "rb") as fh:
            sha = hashlib.sha1(fh.read()).hexdigest()

        cur2.execute(
            """INSERT INTO mir_c2_importacion
            (presentacion_id, archivo_id, archivo_version_id, nombre_archivo, sha1, bytes,
             ruta_archivo, estado, usuario)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'FALLIDA', %s)""",
            (
                presentacion_id,
                a["archivo_id"],
                a["version_id"],
                r["nombre"],
                sha,
                os.path.getsize(r["ruta"]),
                r["ruta"],
                args.usuario,
            ),
        )
        importacion_id = cur2.lastrowid

        # Nace FALLIDA y pasa a VALIDA sólo si supera todo: si el proceso se
        # interrumpe, queda registrada como fallida y no como válida a medias.
        problemas = validar_estructura(r["ruta"], a)
        if problemas:
            # Los errores de estructura no van fila por fila: son del archivo
            # entero, y se informan todos juntos para corregir una sola vez.
            for pr in problemas[:200]:
                cur2.execute(
                    """INSERT INTO mir_c2_errores_de_importacion
                    (importacion_id, tipo, descripcion) VALUES (%s,'COLUMNA_FALTANTE',%s)""",
                    (importacion_id, pr),
                )
            cur2.execute(
                "UPDATE mir_c2_importacion SET terminada_el=NOW() WHERE id=%s",
                (importacion_id,),
            )
            cn.commit()
            imprimir(
                f'   {a["codigo"]:12} ESTRUCTURA INVÁLIDA — {len(problemas)} problemas'
            )
            for pr in problemas[:4]:
                imprimir(f"                  · {pr}")
            resumen_general.append(
                {
                    "codigo": a["codigo"],
                    "estado": "ESTRUCTURA_INVALIDA",
                    "problemas": problemas,
                    "hojas": [],
                }
            )
            continue

        # Los identificadores que este archivo puede referenciar se leen una vez
        # —no fila por fila— de la importación vigente del archivo referenciado.
        contexto_global = {
            "referencias": valores_referenciados(cur2, archivos, a, presentacion_id),
            "coincidencias": valores_a_coincidir(cur2, archivos, a, presentacion_id),
        }
        hojas_resumen = []
        for hoja in a["hojas"]:
            if not hoja.get("tabla"):
                continue
            hojas_resumen.append(
                procesar_hoja(cur2, r["ruta"], hoja, importacion_id, contexto_global)
            )

        total = sum(h["total"] for h in hojas_resumen)
        con_error = sum(h["con_error"] for h in hojas_resumen)
        bloqueantes = sum(h["bloqueantes"] for h in hojas_resumen)
        advertencias = sum(h["advertencias"] for h in hojas_resumen)

        # Importación restrictiva: recién ahora, con el archivo entero evaluado,
        # se sabe si corresponde incorporar. Un bloqueante en cualquier hoja
        # impide que entre una fila de todo el archivo.
        if not bloqueantes:
            for h in hojas_resumen:
                if h.get("insercion"):
                    sql, filas = h["insercion"]
                    cur2.executemany(sql, filas)

        for h in hojas_resumen:
            for hg in h["hallazgos"]:
                if hg.get("campo_id") is None:
                    # Sin campo no hay dónde señalar: es un problema del archivo
                    # entero y va a la otra tabla. Un incumplimiento CON campo y
                    # SIN regla es una validación intrínseca del campo (tipo,
                    # obligatoriedad, catálogo, longitud) y sí corresponde acá.
                    tipo = (
                        "FILA_VACIA_INTERCALADA"
                        if hg["codigo"] == "FILA_VACIA_INTERCALADA"
                        else "ARCHIVO_ILEGIBLE"
                    )
                    cur2.execute(
                        """INSERT INTO mir_c2_errores_de_importacion
                        (importacion_id, tipo, hoja, numero_fila, descripcion)
                        VALUES (%s,%s,%s,%s,%s)""",
                        (importacion_id, tipo, h["hoja"], hg["fila"], hg["detalle"]),
                    )
                    continue
                cur2.execute(
                    """INSERT INTO mir_c2_reglas_incumplidas
                    (importacion_id, campo_id, regla_id, codigo, severidad, nombre_hoja,
                     numero_fila, columna, nombre_campo, valor_encontrado, descripcion)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (
                        importacion_id,
                        hg["campo_id"],
                        hg["regla_id"],
                        hg["codigo"],
                        hg["severidad"],
                        h["hoja"],
                        hg["fila"],
                        hg.get("columna"),
                        hg["campo"],
                        (hg["valor"] or "")[:1000],
                        hg["detalle"],
                    ),
                )

        # Importación restrictiva: con un solo bloqueante el archivo no entra.
        estado = "FALLIDA" if bloqueantes else "VALIDA"
        incorporadas = 0 if bloqueantes else total
        ms = int((datetime.now() - inicio).total_seconds() * 1000)
        cur2.execute(
            """UPDATE mir_c2_importacion SET estado=%s, filas_leidas=%s, filas_incorporadas=%s,
                        bloqueantes=%s, advertencias=%s, terminada_el=NOW(),
                        duracion_ms=%s WHERE id=%s""",
            (
                estado,
                total,
                incorporadas,
                bloqueantes,
                advertencias,
                ms,
                importacion_id,
            ),
        )

        # Una sola importación vigente por archivo. Cuando la nueva entra, la
        # anterior se anula: si no, las dos quedaban VALIDAS y no había forma de
        # decir cuál manda. Las filas de la anulada siguen en la tabla receptora
        # —son la constancia de lo que se cargó—, y por eso todo lo que las lea
        # tiene que hacerlo por importación vigente y no por presentación.
        #
        # Se anula cuando la nueva se incorpora, no cuando se intenta: un
        # archivo que vuelve a importarse con errores no puede hacerle perder a
        # la provincia lo que ya tenía cargado.
        if estado == "VALIDA":
            cur2.execute(
                """UPDATE mir_c2_importacion SET estado='ANULADA'
                    WHERE presentacion_id=%s AND archivo_id=%s AND id<>%s
                      AND estado='VALIDA'""",
                (presentacion_id, a["archivo_id"], importacion_id),
            )
        cn.commit()

        marca = (
            "NO IMPORTADO"
            if bloqueantes
            else ("CON ADVERTENCIAS" if advertencias else "IMPORTADO")
        )
        imprimir(
            f'   {a["codigo"]:12} {marca:18} {total:5} filas · {total - con_error:5} sin problemas · '
            f"{bloqueantes:4} bloqueantes · {advertencias:4} advertencias · {ms} ms"
        )
        resumen_general.append(
            {
                "codigo": a["codigo"],
                "estado": estado,
                "total": total,
                "validas": total - con_error,
                "bloqueantes": bloqueantes,
                "advertencias": advertencias,
                "hojas": hojas_resumen,
                "problemas": [],
            }
        )

    # --- informe ---
    lineas = []
    w = lineas.append
    w(f"# Resultado de la importación — {args.jurisdiccion}, período {args.periodo}")
    w("")
    w(f'**Fecha:** {datetime.now().strftime("%d/%m/%Y %H:%M")}  ')
    w(f"**Carpeta:** `{args.carpeta}`")
    w("")
    w("| Archivo | Estado | Filas | Sin problemas | Bloqueantes | Advertencias |")
    w("|---|---|---|---|---|---|")
    for r in resumen_general:
        if r["estado"] == "ESTRUCTURA_INVALIDA":
            w(
                f'| {r["codigo"]} | **Estructura inválida** | — | — | {len(r["problemas"])} | — |'
            )
        else:
            w(
                f'| {r["codigo"]} | {r["estado"]} | {r["total"]} | {r["validas"]} | '
                f'{r["bloqueantes"]} | {r["advertencias"]} |'
            )
    w("")
    if sin_reconocer or faltantes:
        w("## Archivos")
        w("")
        for f in sin_reconocer:
            w(f"- No se pudo reconocer: `{f}`")
        for a in faltantes:
            w(f'- **Falta** el archivo obligatorio `{a["codigo"]}`')
        w("")

    for r in resumen_general:
        if not r.get("hojas") and not r["problemas"]:
            continue
        w(f'## {r["codigo"]}')
        w("")
        if r["problemas"]:
            w(
                "**La estructura del archivo no corresponde. No se procesó ninguna fila.**"
            )
            w("")
            for pr in r["problemas"]:
                w(f"- {pr}")
            w("")
            continue
        for h in r["hojas"]:
            if not h["hallazgos"]:
                continue
            w(f'### Hoja {h["hoja"]}')
            w("")
            por_codigo: dict[str, int] = {}
            for hg in h["hallazgos"]:
                por_codigo[hg["codigo"]] = por_codigo.get(hg["codigo"], 0) + 1
            w("| Problema | Casos |")
            w("|---|---|")
            for k, v in sorted(por_codigo.items(), key=lambda kv: -kv[1]):
                w(f"| {k} | {v} |")
            w("")
            w("| Fila | Campo | Severidad | Valor | Qué pasa |")
            w("|---|---|---|---|---|")
            for hg in h["hallazgos"][:300]:
                w(
                    f'| {hg["fila"]} | {hg["campo"] or "—"} | {hg["severidad"]} | '
                    f'{(hg["valor"] or "—")[:40]} | {hg["detalle"]} |'
                )
            if len(h["hallazgos"]) > 300:
                w("")
                w(f'*(se muestran 300 de {len(h["hallazgos"])})*')
            w("")

    os.makedirs(args.informe, exist_ok=True)
    destino = os.path.join(
        args.informe, f"importacion_{args.jurisdiccion}_{args.periodo}.md"
    )
    with open(destino, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lineas))
    imprimir(f"\ninforme: {destino}")

    cur.close()
    cur2.close()

    return {
        "resumen": resumen_general,
        "presentacion_id": presentacion_id,
        "sin_reconocer": sin_reconocer,
        "faltantes": [a["codigo"] for a in faltantes],
        "informe": destino,
    }


if __name__ == "__main__":
    main()
