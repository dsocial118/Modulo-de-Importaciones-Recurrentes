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

CONEXION = dict(host=os.environ.get("RUNAC_DB_HOST", "mysql"), port=3306,
                user="root", password="runac_local", database="runac")

PLACEHOLDERS = {"seleccionar", "elegir", "elija una opcion", "seleccione", "-", "--"}


def clave(v) -> str:
    t = re.sub(r"\s+", " ", str(v or "").replace("\xa0", " ").strip()).lower()
    return "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn")


def norm(v) -> str:
    return re.sub(r"\s+", " ", str(v or "").replace("\xa0", " ").strip())


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

    if tipo == "ENTERO":
        if isinstance(valor, bool):
            return None, "Se esperaba un número entero."
        if isinstance(valor, int):
            return valor, None
        if isinstance(valor, float):
            return (int(valor), None) if valor == int(valor) else (None, f"{valor} tiene decimales y se esperaba un número entero.")
        t = norm(valor).replace(".", "").replace(" ", "")
        if re.fullmatch(r"-?\d+", t):
            return int(t), None
        return None, f'"{norm(valor)}" no es un número entero.'

    if tipo == "DECIMAL":
        if isinstance(valor, (int, float)):
            return float(valor), None
        t = norm(valor).replace(".", "").replace(",", ".")
        try:
            return float(t), None
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
    return True


def aplicar_regla(regla: dict, valor, fila_valores: dict, contexto: dict) -> str | None:
    """Devuelve el mensaje de incumplimiento, o None si la regla se cumple."""
    tipo = regla["tipo_regla"]
    par = regla["parametros"] or {}
    vacio = valor is None or norm(valor) == ""

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
            legible = "hoy" if par.get("valor") == "HOY" else par.get("valor")
            return f'El valor no cumple la condición: debe ser {par.get("operador", "").lower().replace("_", " ")} {legible}.'
        return None

    if tipo == "COMPARAR_CAMPO":
        otro = fila_valores.get(par.get("campo_comparacion"))
        if vacio or otro is None:
            return None
        if not comparar(valor, par.get("operador", "IGUAL"), otro):
            return (f'El valor no cumple la condición respecto de "{par.get("campo_comparacion")}": '
                    f'debe ser {par.get("operador", "").lower().replace("_", " ")} que ese campo.')
        return None

    if tipo == "OBLIGATORIO_SI":
        cond = fila_valores.get(par.get("campo_condicion"))
        op = par.get("operador", "IGUAL")
        dispara = (cond is None or norm(cond) == "") if op == "ES_VACIO" else \
                  (cond is not None and norm(cond) != "") if op == "NO_ES_VACIO" else \
                  comparar(cond, op, par.get("valor_condicion"))
        if dispara and vacio:
            return (f'El campo es obligatorio cuando "{par.get("campo_condicion")}" '
                    f'{op.lower().replace("_", " ")} "{par.get("valor_condicion")}".')
        return None

    if tipo == "FORMATO":
        if vacio:
            return None
        patron = par.get("formato", "")
        # N = un dígito. El resto de los caracteres se toman literales.
        rx = "".join(r"\d" if c == "N" else re.escape(c) for c in patron)
        if not re.fullmatch(rx, norm(valor)):
            return f'El valor no respeta el formato esperado ({patron}).'
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
            return (f'La combinación de {", ".join(campos)} ya aparece en la fila {vistos[k]}.')
        vistos[k] = contexto["fila_actual"]
        return None

    if tipo == "EJECUTAR_FUNCION":
        return FUNCIONES.get(par.get("funcion"), lambda v: None)(valor) if not vacio else None

    return None


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
    cur.execute("""
        SELECT a.id, a.codigo, a.nombre_esperado, a.titulo, a.orden_importacion, a.obligatorio
        FROM runac_c1_archivo a ORDER BY a.orden_importacion
    """)
    archivos = cur.fetchall()
    for a in archivos:
        cur.execute("""
            SELECT h.id, h.nombre_esperado, h.fila_encabezados, h.orden_procesamiento, h.obligatoria,
                   e.tabla_cruda, e.tabla_tipada, e.id AS estructura_id
            FROM runac_c1_hoja h
            LEFT JOIN runac_c2_estructura e ON e.hoja_id = h.id
                 AND e.periodo_id = (SELECT id FROM runac_c2_periodo WHERE codigo = %s)
            WHERE h.archivo_id = %s ORDER BY h.orden_procesamiento
        """, (periodo, a["id"]))
        a["hojas"] = cur.fetchall()
        for h in a["hojas"]:
            cur.execute("""
                SELECT c.id, c.nombre, c.titulo_esperado, c.orden, c.tipo_dato,
                       c.longitud_maxima, c.obligatorio, cat.codigo AS catalogo
                FROM runac_c1_campo c LEFT JOIN runac_c1_catalogo cat ON cat.id = c.catalogo_id
                WHERE c.hoja_id = %s ORDER BY c.orden
            """, (h["id"],))
            h["campos"] = cur.fetchall()
            for campo in h["campos"]:
                campo["opciones"] = {}
                if campo["catalogo"]:
                    cur.execute("""
                        SELECT o.id, o.valor_esperado FROM runac_c1_catalogo_opcion o
                        JOIN runac_c1_catalogo c ON c.id = o.catalogo_id
                        WHERE c.codigo = %s AND o.activo = 1
                    """, (campo["catalogo"],))
                    campo["opciones"] = {clave(r["valor_esperado"]): r for r in cur.fetchall()}
                cur.execute("""
                    SELECT r.id, r.nombre, r.parametros, tr.nombre AS tipo_regla, cr.severidad
                    FROM runac_c1_campo_regla cr
                    JOIN runac_c1_regla r ON r.id = cr.regla_id
                    JOIN runac_c1_tipo_regla tr ON tr.id = r.tipo_regla_id
                    WHERE cr.campo_id = %s
                """, (campo["id"],))
                campo["reglas"] = []
                for r in cur.fetchall():
                    r["parametros"] = json.loads(r["parametros"]) if r["parametros"] else {}
                    campo["reglas"].append(r)
    return archivos


# ---------------------------------------------------------------------------
# Proceso
# ---------------------------------------------------------------------------

def reconocer(carpeta: str, archivos: list[dict]) -> tuple[list, list, list]:
    """Empareja los archivos de la carpeta con los que la Capa 1 espera."""
    presentes = [f for f in sorted(os.listdir(carpeta)) if f.lower().endswith((".xlsx", ".xlsm"))
                 and not f.startswith("~$")]
    reconocidos, sin_reconocer, ambiguos = [], list(presentes), []
    # Los códigos más largos primero: MPJ_DAE tiene que ganarle a MPJ.
    for a in sorted(archivos, key=lambda x: -len(x["codigo"])):
        candidatos = [f for f in presentes
                      if re.search(rf"(^|[^A-Za-z0-9]){re.escape(a['codigo'])}([^A-Za-z0-9]|$)", f, re.I)
                      and f in sin_reconocer]
        if not candidatos:
            continue
        if len(candidatos) > 1:
            # No se elige por el sistema: el usuario tiene que decir cuál va.
            ambiguos.append({"codigo": a["codigo"], "candidatos": candidatos})
            continue
        elegido = candidatos[0]
        reconocidos.append({"archivo": a, "nombre": elegido, "ruta": os.path.join(carpeta, elegido)})
        sin_reconocer.remove(elegido)
    faltantes = [a for a in archivos if a["obligatorio"]
                 and not any(r["archivo"]["codigo"] == a["codigo"] for r in reconocidos)]
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
                problemas.append(f'En la hoja "{nombre}" falta la columna {campo["orden"]}: '
                                 f'"{campo["titulo_esperado"]}".')
            elif clave(encontrado) != clave(campo["titulo_esperado"]):
                problemas.append(f'En la hoja "{nombre}", la columna {campo["orden"]} dice '
                                 f'"{encontrado}" y debería decir "{campo["titulo_esperado"]}".')
    wb.close()
    return problemas


def procesar_hoja(cur, ruta, hoja, importacion_id, contexto_global) -> dict:
    """Lee una hoja, la valida y la deja en staging. Devuelve el resumen."""
    wb = load_workbook(ruta, data_only=True, read_only=True)
    ws = wb[hoja["nombre_esperado"]]
    campos = hoja["campos"]
    fila_enc = hoja["fila_encabezados"]

    hallazgos: list[dict] = []
    filas_crudas: list[tuple] = []
    filas_tipadas: list[tuple] = []
    contexto = {"unicos": {}, "fila_actual": 0}
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
                hallazgos.append(dict(codigo="TIPO_INVALIDO", severidad="BLOQUEANTE",
                                      campo_id=campo["id"], regla_id=None, fila=nro,
                                      campo=campo["titulo_esperado"], valor=norm(crudo), detalle=error))
                errores_fila += 1
                valores_tipados[campo["nombre"]] = None
                continue

            vacio = valor is None or norm(valor) == ""
            if campo["obligatorio"] and vacio:
                hallazgos.append(dict(codigo="OBLIGATORIO_VACIO", severidad="BLOQUEANTE",
                                      campo_id=campo["id"], regla_id=None, fila=nro,
                                      campo=campo["titulo_esperado"], valor=None,
                                      detalle="El campo es obligatorio y está vacío."))
                errores_fila += 1

            if campo["opciones"] and not vacio:
                if clave(valor) not in campo["opciones"]:
                    hallazgos.append(dict(codigo="FUERA_DE_CATALOGO", severidad="BLOQUEANTE",
                                          campo_id=campo["id"], regla_id=None, fila=nro,
                                          campo=campo["titulo_esperado"], valor=norm(valor),
                                          detalle=f'El valor no está entre los admitidos para este campo.'))
                    errores_fila += 1

            largo = campo["longitud_maxima"]
            if largo and not vacio and campo["tipo_dato"] == "TEXTO" and len(str(valor)) > largo:
                hallazgos.append(dict(codigo="TEXTO_MUY_LARGO", severidad="BLOQUEANTE",
                                      campo_id=campo["id"], regla_id=None, fila=nro,
                                      campo=campo["titulo_esperado"], valor=str(valor)[:60] + "…",
                                      detalle=f"El texto tiene {len(str(valor))} caracteres y el máximo admitido es {largo}."))
                errores_fila += 1

            valores_tipados[campo["nombre"]] = valor

        # --- reglas ---
        for campo in campos:
            for regla in campo["reglas"]:
                mensaje = aplicar_regla(regla, valores_tipados.get(campo["nombre"]),
                                        valores_tipados, contexto)
                if mensaje:
                    hallazgos.append(dict(codigo=regla["tipo_regla"], severidad=regla["severidad"],
                                          campo_id=campo["id"], regla_id=regla["id"], fila=nro,
                                          campo=campo["titulo_esperado"],
                                          valor=norm(valores_tipados.get(campo["nombre"])),
                                          detalle=mensaje))
                    if regla["severidad"] == "BLOQUEANTE":
                        errores_fila += 1

        if errores_fila:
            con_error += 1

        estado = "CON_ERROR" if errores_fila else "VALIDA"
        contenido = "|".join(norm(valores_crudos.get(c["nombre"])) for c in campos)
        filas_crudas.append((importacion_id, nro, estado,
                             hashlib.sha1(contenido.encode("utf-8")).hexdigest(),
                             *[norm(valores_crudos.get(c["nombre"])) or None for c in campos]))
        if not errores_fila:
            filas_tipadas.append((importacion_id, nro, *[valores_tipados.get(c["nombre"]) for c in campos]))

    wb.close()

    for f in vacias_intercaladas:
        hallazgos.append(dict(codigo="FILA_VACIA_INTERCALADA", severidad="BLOQUEANTE",
                              campo_id=None, regla_id=None, fila=f, campo=None, valor=None,
                              detalle="Hay una fila vacía en el medio de los datos. "
                                      "El requerimiento pide corregirlo antes de importar."))

    # --- staging ---
    cols = ", ".join(f"`{c['nombre']}`" for c in campos)
    if filas_crudas:
        marcas = ", ".join(["%s"] * (4 + len(campos)))
        cur.executemany(
            f'INSERT INTO `{hoja["tabla_cruda"]}` (importacion_id, numero_fila, estado, hash_contenido, {cols}) '
            f"VALUES ({marcas})", filas_crudas)

    bloqueantes = sum(1 for h in hallazgos if h["severidad"] == "BLOQUEANTE")
    # Atomicidad por archivo: con un solo bloqueante, no se normaliza nada.
    if filas_tipadas and bloqueantes == 0:
        marcas = ", ".join(["%s"] * (2 + len(campos)))
        cur.executemany(
            f'INSERT INTO `{hoja["tabla_tipada"]}` (importacion_id, numero_fila, {cols}) VALUES ({marcas})',
            filas_tipadas)

    return {"hoja": hoja["nombre_esperado"], "total": total, "con_error": con_error,
            "hallazgos": hallazgos, "bloqueantes": bloqueantes,
            "advertencias": sum(1 for h in hallazgos if h["severidad"] == "ADVERTENCIA")}


class _Opciones:
    """Los mismos datos que trae la línea de comandos, para poder llamar a la
    importación desde otro lado (por ejemplo, desde una vista web)."""

    def __init__(self, carpeta, jurisdiccion, periodo, usuario, informe, asignacion=None, silencioso=False):
        self.carpeta = carpeta
        self.jurisdiccion = jurisdiccion
        self.periodo = periodo
        self.usuario = usuario
        self.informe = informe
        self.asignacion = asignacion or {}
        self.silencioso = silencioso


def procesar_carpeta(carpeta, jurisdiccion, periodo, usuario="prototipo",
                     informe="/trabajo/capa1/informes", asignacion=None,
                     conexion=None, silencioso=True):
    """Importa una carpeta y devuelve el resumen. Es lo que usa el prototipo."""
    args = _Opciones(carpeta, jurisdiccion, periodo, usuario, informe, asignacion, silencioso)
    return _ejecutar(args, conexion or CONEXION)


def main():
    p = argparse.ArgumentParser(description="Importa una carpeta de archivos de RUNAC.")
    p.add_argument("--carpeta", required=True)
    p.add_argument("--jurisdiccion", default="Salta")
    p.add_argument("--periodo", default="2026_T1")
    p.add_argument("--usuario", default="prueba")
    p.add_argument("--informe", default="/trabajo/capa1/informes")
    args = p.parse_args()
    args.asignacion = {}
    args.silencioso = False
    _ejecutar(args, CONEXION)


def _ejecutar(args, conexion):
    imprimir = (lambda *a, **k: None) if getattr(args, "silencioso", False) else print
    cn = mysql.connector.connect(**conexion)
    cur = cn.cursor(dictionary=True)
    archivos = leer_configuracion(cur, args.periodo)

    imprimir(f"Carpeta: {args.carpeta}")
    imprimir(f"Jurisdicción: {args.jurisdiccion} · Período: {args.periodo}\n")

    reconocidos, sin_reconocer, faltantes, ambiguos = reconocer(args.carpeta, archivos)
    imprimir("== Reconocimiento ==")
    for r in sorted(reconocidos, key=lambda x: x["archivo"]["orden_importacion"]):
        imprimir(f'   OK   {r["nombre"][:52]:54} -> {r["archivo"]["codigo"]}')
    for am in ambiguos:
        imprimir(f'   !!   {am["codigo"]}: hay {len(am["candidatos"])} archivos que podrían serlo, '
              f"hay que elegir uno")
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
    cur2.execute("SELECT id FROM runac_c2_periodo WHERE codigo=%s", (args.periodo,))
    fila = cur2.fetchone()
    if not fila:
        raise SystemExit(f"No existe el período {args.periodo}.")
    periodo_id = fila[0]
    cur2.execute("""INSERT INTO runac_c2_presentacion (periodo_id, jurisdiccion, version, estado)
                    VALUES (%s, %s, 1, 'BORRADOR')
                    ON DUPLICATE KEY UPDATE estado = 'BORRADOR'""", (periodo_id, args.jurisdiccion))
    cur2.execute("""SELECT id FROM runac_c2_presentacion
                    WHERE periodo_id=%s AND jurisdiccion=%s AND version=1""", (periodo_id, args.jurisdiccion))
    presentacion_id = cur2.fetchone()[0]

    resumen_general = []
    imprimir("== Procesamiento ==")
    for r in sorted(reconocidos, key=lambda x: x["archivo"]["orden_importacion"]):
        a = r["archivo"]
        inicio = datetime.now()
        with open(r["ruta"], "rb") as fh:
            sha = hashlib.sha1(fh.read()).hexdigest()

        cur2.execute("""INSERT INTO runac_c2_importacion
            (presentacion_id, estructura_id, nombre_archivo, sha1, bytes, estado, usuario)
            VALUES (%s, %s, %s, %s, %s, 'VALIDANDO_ESTRUCTURA', %s)""",
                     (presentacion_id, a["hojas"][0]["estructura_id"] if a["hojas"] else None,
                      r["nombre"], sha, os.path.getsize(r["ruta"]), args.usuario))
        importacion_id = cur2.lastrowid

        problemas = validar_estructura(r["ruta"], a)
        if problemas:
            cur2.execute("""UPDATE runac_c2_importacion SET estado='ESTRUCTURA_INVALIDA',
                            detalle_error=%s, terminada_el=NOW() WHERE id=%s""",
                         ("\n".join(problemas), importacion_id))
            for pr in problemas[:200]:
                cur2.execute("""INSERT INTO runac_c2_hallazgo
                    (importacion_id, codigo, severidad, descripcion) VALUES (%s,'ESTRUCTURA','BLOQUEANTE',%s)""",
                             (importacion_id, pr))
            cn.commit()
            imprimir(f'   {a["codigo"]:12} ESTRUCTURA INVÁLIDA — {len(problemas)} problemas')
            for pr in problemas[:4]:
                imprimir(f"                  · {pr}")
            resumen_general.append({"codigo": a["codigo"], "estado": "ESTRUCTURA_INVALIDA",
                                    "problemas": problemas, "hojas": []})
            continue

        cur2.execute("UPDATE runac_c2_importacion SET estado='VALIDANDO_CONTENIDO' WHERE id=%s",
                     (importacion_id,))
        hojas_resumen = []
        for hoja in a["hojas"]:
            if not hoja["tabla_cruda"]:
                continue
            hojas_resumen.append(procesar_hoja(cur2, r["ruta"], hoja, importacion_id, {}))

        total = sum(h["total"] for h in hojas_resumen)
        con_error = sum(h["con_error"] for h in hojas_resumen)
        bloqueantes = sum(h["bloqueantes"] for h in hojas_resumen)
        advertencias = sum(h["advertencias"] for h in hojas_resumen)

        for h in hojas_resumen:
            for hg in h["hallazgos"]:
                cur2.execute("""INSERT INTO runac_c2_hallazgo
                    (importacion_id, campo_id, regla_id, codigo, severidad, nombre_hoja,
                     numero_fila, nombre_campo, valor_encontrado, descripcion)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                             (importacion_id, hg["campo_id"], hg["regla_id"], hg["codigo"],
                              hg["severidad"], h["hoja"], hg["fila"], hg["campo"],
                              (hg["valor"] or "")[:1000], hg["detalle"]))

        estado = "CON_ERRORES" if bloqueantes else ("REQUIERE_REVISION" if advertencias else "VALIDADO")
        ms = int((datetime.now() - inicio).total_seconds() * 1000)
        cur2.execute("""UPDATE runac_c2_importacion SET estado=%s, filas_totales=%s, filas_validas=%s,
                        filas_con_error=%s, bloqueantes=%s, advertencias=%s, terminada_el=NOW(),
                        duracion_ms=%s WHERE id=%s""",
                     (estado, total, total - con_error, con_error, bloqueantes, advertencias, ms, importacion_id))
        cn.commit()

        marca = {"CON_ERRORES": "CON ERRORES", "REQUIERE_REVISION": "CON ADVERTENCIAS", "VALIDADO": "VALIDADO"}[estado]
        imprimir(f'   {a["codigo"]:12} {marca:18} {total:5} filas · {total - con_error:5} sin problemas · '
              f"{bloqueantes:4} bloqueantes · {advertencias:4} advertencias · {ms} ms")
        resumen_general.append({"codigo": a["codigo"], "estado": estado, "total": total,
                                "validas": total - con_error, "bloqueantes": bloqueantes,
                                "advertencias": advertencias, "hojas": hojas_resumen, "problemas": []})

    # --- informe ---
    L = []
    w = L.append
    w(f"# Resultado de la importación — {args.jurisdiccion}, período {args.periodo}")
    w("")
    w(f'**Fecha:** {datetime.now().strftime("%d/%m/%Y %H:%M")}  ')
    w(f"**Carpeta:** `{args.carpeta}`")
    w("")
    w("| Archivo | Estado | Filas | Sin problemas | Bloqueantes | Advertencias |")
    w("|---|---|---|---|---|---|")
    for r in resumen_general:
        if r["estado"] == "ESTRUCTURA_INVALIDA":
            w(f'| {r["codigo"]} | **Estructura inválida** | — | — | {len(r["problemas"])} | — |')
        else:
            w(f'| {r["codigo"]} | {r["estado"]} | {r["total"]} | {r["validas"]} | '
              f'{r["bloqueantes"]} | {r["advertencias"]} |')
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
            w("**La estructura del archivo no corresponde. No se procesó ninguna fila.**")
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
                w(f'| {hg["fila"]} | {hg["campo"] or "—"} | {hg["severidad"]} | '
                  f'{(hg["valor"] or "—")[:40]} | {hg["detalle"]} |')
            if len(h["hallazgos"]) > 300:
                w("")
                w(f'*(se muestran 300 de {len(h["hallazgos"])})*')
            w("")

    os.makedirs(args.informe, exist_ok=True)
    destino = os.path.join(args.informe, f"importacion_{args.jurisdiccion}_{args.periodo}.md")
    with open(destino, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))
    imprimir(f"\ninforme: {destino}")

    cur.close()
    cur2.close()
    cn.close()
    return {
        "reconocidos": [{"codigo": r["archivo"]["codigo"], "nombre": r["nombre"]} for r in reconocidos],
        "sin_reconocer": sin_reconocer,
        "faltantes": [a["codigo"] for a in faltantes],
        "ambiguos": ambiguos,
        "archivos": resumen_general,
        "presentacion_id": presentacion_id,
        "informe": destino,
    }


if __name__ == "__main__":
    main()
