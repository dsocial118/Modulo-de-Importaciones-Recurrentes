"""Edición de un dato ya importado.

El análisis funcional lo define así: los errores **bloqueantes** se corrigen en
el Excel y el archivo se vuelve a importar; las **advertencias** se resuelven
dentro del sistema, editando el dato o justificándolo.

Esto es lo segundo. Reglas que se aplican acá y no en las vistas:

  - Sólo edita la jurisdicción. El nivel nacional observa, no modifica.
  - Sólo se edita mientras la presentación está en carga o subsanando; con la
    carga cerrada, primero hay que reabrirla.
  - Toda edición queda registrada con usuario, fecha, valor anterior y valor
    nuevo, en `mir_c2_historial_cambios`.

La tabla que recibe los datos se deduce por convención, con la misma función que
usan el generador y el importador: si se desincronizan, se escribe en una tabla
que no existe.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from django.db import connection, transaction

from runac.services import circuito_service as circuito
from runac.services.importacion_service import con_nombres_de_archivo, nombres_cortos

_MOTOR = Path(__file__).resolve().parent / "motor"
if str(_MOTOR) not in sys.path:
    sys.path.insert(0, str(_MOTOR))

# El import va acá y no arriba porque depende del sys.path de las líneas previas.
from comun import (  # noqa: E402  # pylint: disable=wrong-import-position
    nombre_tabla_receptora,
)
import en_palabras  # noqa: E402  # pylint: disable=wrong-import-position
from importar import (  # noqa: E402  # pylint: disable=wrong-import-position
    ReglaInvalida,
    aplicar_regla,
    clave,
    mensaje_para_quien_carga,
    norm,
    texto_a_numero,
)

# Reglas que no se pueden decidir mirando una sola fila: preguntan por el resto
# de la hoja. Al corregir un dato se re-evalúa la fila, no la hoja entera, así
# que estas quedan como estaban hasta la próxima importación.
REGLAS_DE_HOJA_COMPLETA = ("UNICO_EN_HOJA", "UNICO_COMBINADO")

# Estados de la presentación en los que la jurisdicción todavía puede corregir.
ESTADOS_EDITABLES = ("EN_CARGA", "OBSERVADA", "SUBSANADA")

FILAS_POR_PAGINA = 25


class EdicionNoPermitida(Exception):
    """La edición no corresponde: por estado, por rol o por dato inválido."""


class HaceFaltaConfirmar(Exception):
    """El dato lo usan filas de otros archivos: hay que decidir si se actualizan.

    Como en una base relacional, un cambio no puede dejar huérfano lo que lo
    referencia (pedido del responsable funcional, 27-09-2026): se cambió el
    nombre de un dispositivo y las nóminas quedaron nombrando uno que ya no
    existía. Se pregunta; si se acepta, se actualizan todas; si no, no cambia
    nada.
    """

    def __init__(self, usos: list[dict]):
        cuantas = sum(len(g["filas"]) for g in usos)
        super().__init__(
            f"Ese dato lo usan {cuantas} fila(s) de otros archivos. "
            "Hay que confirmar si se actualizan también."
        )
        self.usos = usos


def _filas(cursor) -> list[dict[str, Any]]:
    columnas = [c[0] for c in cursor.description]
    return [dict(zip(columnas, fila)) for fila in cursor.fetchall()]


def _identificador_seguro(nombre: str) -> str:
    """Un nombre de tabla o columna que se interpola en SQL tiene que ser
    exactamente lo que la Capa 1 declaró: nada más."""
    if not re.fullmatch(r"[a-z0-9_]{1,64}", nombre or ""):
        raise EdicionNoPermitida("Nombre de campo o tabla no válido.")
    return nombre


# ---------------------------------------------------------------------------
# Contexto de la importación
# ---------------------------------------------------------------------------


def contexto_de(importacion_id: int) -> dict[str, Any]:
    """Todo lo que hace falta para editar: archivo, versión, hojas y estado."""
    with connection.cursor() as cur:
        cur.execute(
            """
            SELECT i.id, i.nombre_archivo, i.estado AS estado_importacion,
                   a.codigo AS archivo_codigo, a.id AS archivo_id,
                   av.id AS version_id, av.numero AS version,
                   s.id AS presentacion_id, s.estado AS estado_presentacion,
                   j.nombre AS jurisdiccion, p.codigo AS periodo
            FROM mir_c2_importacion i
            JOIN mir_c1_archivo a ON a.id = i.archivo_id
            JOIN mir_c1_archivo_version av ON av.id = i.archivo_version_id
            JOIN mir_c2_presentacion s ON s.id = i.presentacion_id
            JOIN mir_c2_jurisdiccion j ON j.id = s.jurisdiccion_id
            JOIN mir_c2_periodo p ON p.id = s.periodo_id
            WHERE i.id = %s
            """,
            [importacion_id],
        )
        datos = _filas(cur)
        if not datos:
            return {}
        datos = datos[0]

        cur.execute(
            """
            SELECT id, nombre_esperado, orden_procesamiento, referencia
            FROM mir_c1_hoja WHERE archivo_version_id = %s
            ORDER BY orden_procesamiento
            """,
            [datos["version_id"]],
        )
        datos["hojas"] = _filas(cur)

    datos["editable"] = datos["estado_presentacion"] in ESTADOS_EDITABLES
    return datos


def campos_de_la_hoja(hoja_id: int) -> list[dict[str, Any]]:
    with connection.cursor() as cur:
        cur.execute(
            """
            SELECT c.id, c.nombre, c.titulo_esperado, c.orden, c.tipo_dato,
                   c.longitud_maxima, c.obligatorio, c.identifica, cat.codigo AS catalogo
            FROM mir_c1_campo c
            LEFT JOIN mir_c1_catalogo cat ON cat.id = c.catalogo_id
            WHERE c.hoja_id = %s ORDER BY c.orden
            """,
            [hoja_id],
        )
        return _filas(cur)


def opciones_de(catalogo: str, periodo: str | None = None) -> list[str]:
    """Los valores admitidos de un campo con lista cerrada, en ese período.

    La vigencia importa: una opción dada de baja en 2027 sigue siendo válida en
    los períodos anteriores, y una agregada después no vale hacia atrás. Sin
    esto, la pantalla de corrección ofrecía opciones que la importación rechaza
    —o rechazaba las que el archivo traía con razón—. La comparación es de
    texto porque el código de período está armado para eso: «2026_T1» <
    «2026_T2» < «2027_T1».
    """
    if not catalogo:
        return []
    sql = """
        SELECT o.valor_esperado FROM mir_c1_catalogo_opcion o
        JOIN mir_c1_catalogo c ON c.id = o.catalogo_id
        WHERE c.codigo = %s AND o.activo = 1
    """
    parametros: list[Any] = [catalogo]
    if periodo:
        sql += """
          AND (o.vigente_desde_periodo IS NULL OR o.vigente_desde_periodo <= %s)
          AND (o.vigente_hasta_periodo IS NULL OR o.vigente_hasta_periodo >= %s)
        """
        parametros += [periodo, periodo]
    with connection.cursor() as cur:
        cur.execute(sql + " ORDER BY o.orden", parametros)
        return [f[0] for f in cur.fetchall()]


def reglas_de_los_campos(campos: list[dict]) -> dict[int, list[dict]]:
    """Las reglas de Capa 1 de cada campo, para volver a aplicarlas al corregir.

    Es la misma consulta que hace el motor al importar. Se repite acá y no se
    reutiliza porque el motor lee con su propia conexión, fuera de Django; lo
    que no se puede permitir es que difieran, y por eso las dos leen las mismas
    tablas y no una copia.
    """
    if not campos:
        return {}
    marcas = ", ".join(["%s"] * len(campos))
    with connection.cursor() as cur:
        cur.execute(
            f"""
            SELECT cr.campo_id, r.id, r.nombre, r.parametros,
                   tr.nombre AS tipo_regla, cr.severidad,
                   cr.mensaje AS mensaje_configurado
            FROM mir_c1_campo_regla cr
            JOIN mir_c1_regla r ON r.id = cr.regla_id
            JOIN mir_c1_tipo_regla tr ON tr.id = r.tipo_regla_id
            WHERE cr.campo_id IN ({marcas})
            """,
            [c["id"] for c in campos],
        )
        por_campo: dict[int, list[dict]] = {}
        for regla in _filas(cur):
            crudo = regla["parametros"]
            if isinstance(crudo, (bytes, bytearray)):
                crudo = crudo.decode("utf-8")
            regla["parametros"] = (
                crudo if isinstance(crudo, dict) else json.loads(crudo or "{}")
            )
            por_campo.setdefault(regla["campo_id"], []).append(regla)
    return por_campo


def celda_observable(importacion_id: int, numero_fila: int, campo_id: int) -> str:
    """Comprueba que el dato exista y devuelve de quién es su fila.

    Para observar un dato: el campo tiene que ser de una hoja de esta
    importación y la fila tiene que haber entrado. Si no, EdicionNoPermitida.
    """
    contexto = contexto_de(importacion_id)
    if not contexto:
        raise EdicionNoPermitida("No existe esa importación.")
    hoja = None
    for h in contexto["hojas"]:
        campos = campos_de_la_hoja(h["id"])
        if any(c["id"] == int(campo_id) for c in campos):
            hoja = h
            break
    if not hoja or hoja.get("referencia"):
        raise EdicionNoPermitida("Ese campo no es de esta importación.")
    tabla = _identificador_seguro(
        nombre_tabla_receptora(
            contexto["archivo_codigo"],
            hoja["nombre_esperado"],
            len(contexto["hojas"]) > 1,
            contexto["version"],
        )
    )
    columnas = (
        ", ".join(f"`{_identificador_seguro(c['nombre'])}`" for c in campos) or "1"
    )
    with connection.cursor() as cur:
        cur.execute(
            f"SELECT {columnas} FROM `{tabla}` WHERE importacion_id = %s AND numero_fila = %s",
            [importacion_id, numero_fila],
        )
        valores = cur.fetchone()
    if valores is None:
        raise EdicionNoPermitida("Esa fila no está entre los datos importados.")
    fila = dict(zip([c["nombre"] for c in campos], valores))
    return identificacion_de_la_fila(campos, fila)


def identificacion_de_la_fila(campos: list[dict], fila: dict) -> str:
    """«12 · Gómez · Martina · 90000137»: los valores de los campos identificatorios.

    Es `identificar_fila` del motor, sobre los valores ya importados. Si no hay
    ninguno cargado, queda vacía y la pantalla muestra sólo el número de fila.
    """
    partes = [
        _texto_del_valor(fila.get(c["nombre"])).strip()
        for c in campos
        if c.get("identifica")
    ]
    return " · ".join(p for p in partes if p)[:255]


def _texto_del_valor(valor) -> str:
    """Cómo se muestra un valor en el campo de edición.

    Las fechas se muestran como las escribe la provincia: dd/mm/aaaa.
    """
    if valor is None:
        return ""
    if hasattr(valor, "strftime"):
        return valor.strftime("%d/%m/%Y")
    return str(valor)


# ---------------------------------------------------------------------------
# Lectura de los datos importados
# ---------------------------------------------------------------------------


def datos_de_la_hoja(
    importacion_id: int,
    hoja: dict,
    pagina: int = 1,
    solo_con_advertencia: bool = False,
    solo_filas: list[int] | None = None,
) -> dict[str, Any]:
    """Las filas importadas de una hoja, con sus advertencias.

    `solo_filas` acota a esas filas: por ejemplo, las que tienen observaciones
    sin resolver.
    """
    contexto = contexto_de(importacion_id)
    if not contexto:
        return {}

    varias = len(contexto["hojas"]) > 1
    tabla = _identificador_seguro(
        nombre_tabla_receptora(
            contexto["archivo_codigo"],
            hoja["nombre_esperado"],
            varias,
            contexto["version"],
        )
    )
    campos = campos_de_la_hoja(hoja["id"])

    with connection.cursor() as cur:
        # Las advertencias de esta hoja, agrupadas por fila y por campo.
        cur.execute(
            """
            SELECT numero_fila, nombre_campo, severidad, descripcion, valor_encontrado,
                   codigo
            FROM mir_c2_reglas_incumplidas
            WHERE importacion_id = %s AND nombre_hoja = %s AND resuelta = 0
            """,
            [importacion_id, hoja["nombre_esperado"]],
        )
        avisos: dict[int, list[dict]] = {}
        nombres = nombres_cortos()
        for aviso in _filas(cur):
            # En palabras, como en los Excel: no «debe ser menor igual hoy».
            aviso["descripcion"] = con_nombres_de_archivo(
                en_palabras.problema_en_palabras(aviso["codigo"], aviso["descripcion"]),
                nombres,
            )
            avisos.setdefault(aviso["numero_fila"], []).append(aviso)

        filtro = ""
        parametros: list[Any] = [importacion_id]
        if solo_con_advertencia and avisos:
            marcas = ", ".join(["%s"] * len(avisos))
            filtro = f" AND numero_fila IN ({marcas})"
            parametros += list(avisos)
        elif solo_con_advertencia:
            filtro = " AND 1 = 0"
        if solo_filas is not None:
            if solo_filas:
                marcas = ", ".join(["%s"] * len(solo_filas))
                filtro += f" AND numero_fila IN ({marcas})"
                parametros += [int(n) for n in solo_filas]
            else:
                filtro += " AND 1 = 0"

        cur.execute(
            f"SELECT COUNT(*) FROM `{tabla}` WHERE importacion_id = %s{filtro}",
            parametros,
        )
        total = cur.fetchone()[0]

        pagina = max(1, int(pagina or 1))
        desplazamiento = (pagina - 1) * FILAS_POR_PAGINA
        columnas = ", ".join(f"`{_identificador_seguro(c['nombre'])}`" for c in campos)
        cur.execute(
            f"""SELECT id, numero_fila, estado, {columnas}
                 FROM `{tabla}` WHERE importacion_id = %s{filtro}
                 ORDER BY numero_fila LIMIT %s OFFSET %s""",
            parametros + [FILAS_POR_PAGINA, desplazamiento],
        )
        filas = _filas(cur)

    # Las opciones de cada campo con lista cerrada se leen una sola vez.
    opciones_por_campo = {
        c["nombre"]: opciones_de(c["catalogo"], contexto["periodo"])
        for c in campos
        if c.get("catalogo")
    }

    for fila in filas:
        # De quién es la fila, como en el informe: «Fila 5» sola no le dice nada
        # a quien corrige (pedido de la DNPYPI el 22-09, #67). Misma regla que
        # el motor al importar: los campos que la Capa 1 marca como
        # identificatorios, en su orden.
        fila["identificacion"] = identificacion_de_la_fila(campos, fila)
        fila["avisos"] = avisos.get(fila["numero_fila"], [])
        con_aviso = {a["nombre_campo"] for a in fila["avisos"] if a["nombre_campo"]}
        # El template no puede resolver fila[campo]: las celdas se arman acá.
        fila["celdas"] = [
            {
                "campo": campo,
                "nombre": campo["nombre"],
                "titulo": campo["titulo_esperado"],
                "obligatorio": bool(campo["obligatorio"]),
                "valor": _texto_del_valor(fila.get(campo["nombre"])),
                "opciones": opciones_por_campo.get(campo["nombre"], []),
                "tiene_aviso": campo["titulo_esperado"] in con_aviso,
            }
            for campo in campos
        ]

    paginas = max(1, -(-total // FILAS_POR_PAGINA))
    return {
        "contexto": contexto,
        "hoja": hoja,
        "campos": campos,
        "filas": filas,
        "total": total,
        "pagina": pagina,
        "paginas": paginas,
        "con_advertencia": sum(1 for a in avisos.values() if a),
        "tabla": tabla,
    }


# ---------------------------------------------------------------------------
# Revalidación de la fila corregida
# ---------------------------------------------------------------------------


REGLAS_ENTRE_ARCHIVOS = ("EXISTE_EN_ARCHIVO", "COINCIDE_CON_ARCHIVO")


def valores_de_otros_archivos(  # pylint: disable=too-many-locals  # dos consultas por regla
    reglas: dict[int, list[dict]], presentacion_id: int
) -> dict[str, dict]:
    """Lo que las reglas entre archivos necesitan saber de los otros archivos.

    Es lo mismo que el motor lee antes de importar (`valores_referenciados` y
    `valores_a_coincidir` en `motor/importar.py`): de la importación **vigente**
    de cada archivo referenciado, dentro de la misma presentación. Faltaba al
    corregir un dato, y sin esto toda corrección de una nómina que cruza con el
    legajo se rechazaba con «no se pudieron leer los valores del archivo
    referenciado» —visto el 25-09-2026—.

    Si el archivo referenciado no está importado, la regla queda sin datos y el
    motor lo dice, igual que al importar.
    """
    referencias: dict[int, set] = {}
    coincidencias: dict[int, dict] = {}
    todas = [r for lista in reglas.values() for r in lista]
    with connection.cursor() as cur:
        for regla in todas:
            if regla["tipo_regla"] not in REGLAS_ENTRE_ARCHIVOS:
                continue
            par = regla["parametros"] or {}
            cur.execute(
                """
                SELECT i.id, av.id AS version_id, av.numero AS version
                FROM mir_c2_importacion i
                JOIN mir_c1_archivo a ON a.id = i.archivo_id
                JOIN mir_c1_archivo_version av ON av.id = i.archivo_version_id
                WHERE i.presentacion_id = %s AND a.codigo = %s AND i.estado = 'VALIDA'
                ORDER BY i.id DESC LIMIT 1
                """,
                [presentacion_id, par.get("archivo")],
            )
            vigente = _filas(cur)
            if not vigente:
                continue
            vigente = vigente[0]
            cur.execute(
                """SELECT h.nombre_esperado,
                          GROUP_CONCAT(c.nombre SEPARATOR '|') AS campos
                   FROM mir_c1_hoja h JOIN mir_c1_campo c ON c.hoja_id = h.id
                   WHERE h.archivo_version_id = %s
                   GROUP BY h.id""",
                [vigente["version_id"]],
            )
            hojas = _filas(cur)
            varias = len(hojas) > 1
            existe = regla["tipo_regla"] == "EXISTE_EN_ARCHIVO"
            columnas = (
                [par.get("campo")] if existe else [par.get("clave"), par.get("campo")]
            )
            juntados: set = set()
            pares: dict = {}
            for hoja in hojas:
                # Sin hoja declarada se buscan todas, como hace el motor: el
                # dispositivo penal está en la hoja que corresponde a su tipo.
                if par.get("hoja") and hoja["nombre_esperado"] != par["hoja"]:
                    continue
                if not all(col in hoja["campos"].split("|") for col in columnas):
                    continue
                tabla = _identificador_seguro(
                    nombre_tabla_receptora(
                        par.get("archivo"),
                        hoja["nombre_esperado"],
                        varias,
                        vigente["version"],
                    )
                )
                elegidas = ", ".join(
                    f"`{_identificador_seguro(col)}`" for col in columnas
                )
                cur.execute(
                    f"SELECT {elegidas} FROM `{tabla}` WHERE importacion_id = %s",
                    [vigente["id"]],
                )
                for fila in cur.fetchall():
                    if existe:
                        juntados.add(clave(fila[0]))
                    elif fila[0] is not None:
                        pares[clave(fila[0])] = clave(fila[1])
            if existe:
                referencias[regla["id"]] = juntados
            else:
                coincidencias[regla["id"]] = pares
    return {"referencias": referencias, "coincidencias": coincidencias}


def hallazgos_de_la_fila(
    campos: list[dict],
    valores: dict,
    periodo: str | None = None,
    presentacion_id: int | None = None,
) -> list[dict]:
    """Vuelve a aplicar sobre una fila todo lo que se controló al importar.

    Se re-evalúa la **fila entera** y no sólo el campo tocado: hay reglas que
    miran otro campo —«la fecha de egreso no puede ser anterior a la de
    ingreso», «si el vínculo es familiar el parentesco es obligatorio»—, así que
    corregir un dato puede resolver la advertencia de otro, o crearla.

    Con la presentación, se leen además los otros archivos, para las reglas
    que cruzan con ellos.
    """
    titulos = {c["nombre"]: c["titulo_esperado"] for c in campos}
    contexto = {"unicos": {}, "fila_actual": 0, "titulos": titulos}
    reglas = reglas_de_los_campos(campos)
    if presentacion_id is not None:
        contexto.update(valores_de_otros_archivos(reglas, presentacion_id))
    hallazgos: list[dict] = []

    def anotar(campo, codigo, severidad, detalle, regla_id=None, valor=None):
        hallazgos.append(
            {
                "codigo": codigo,
                "severidad": severidad,
                "campo_id": campo["id"],
                "regla_id": regla_id,
                "nombre_campo": campo["titulo_esperado"],
                "valor": valor,
                "descripcion": detalle,
            }
        )

    for campo in campos:
        valor = valores.get(campo["nombre"])
        vacio = valor is None or norm(valor) == ""

        if campo["obligatorio"] and vacio:
            anotar(
                campo,
                "OBLIGATORIO_VACIO",
                "BLOQUEANTE",
                "El campo es obligatorio y está vacío.",
            )
        if campo.get("catalogo") and not vacio:
            admitidos = opciones_de(campo["catalogo"], periodo)
            if admitidos and clave(valor) not in {clave(o) for o in admitidos}:
                anotar(
                    campo,
                    "FUERA_DE_CATALOGO",
                    "BLOQUEANTE",
                    "El valor no está entre los admitidos para este campo.",
                    valor=norm(valor),
                )
        largo = campo.get("longitud_maxima")
        if (
            largo
            and not vacio
            and campo["tipo_dato"] == "TEXTO"
            and len(str(valor)) > largo
        ):
            anotar(
                campo,
                "TEXTO_MUY_LARGO",
                "BLOQUEANTE",
                f"El texto tiene {len(str(valor))} caracteres y el máximo "
                f"admitido es {largo}.",
            )

        for regla in reglas.get(campo["id"], []):
            if regla["tipo_regla"] in REGLAS_DE_HOJA_COMPLETA:
                continue
            try:
                mensaje = aplicar_regla(regla, valor, valores, contexto)
            except ReglaInvalida as falla:
                anotar(
                    campo,
                    "REGLA_NO_APLICABLE",
                    "BLOQUEANTE",
                    f'La regla «{regla["nombre"]}» no se pudo evaluar: {falla}.',
                    regla_id=regla["id"],
                )
                continue
            if mensaje:
                anotar(
                    campo,
                    regla["tipo_regla"],
                    regla["severidad"],
                    mensaje_para_quien_carga(regla, valor, mensaje),
                    regla_id=regla["id"],
                    valor=norm(valor),
                )
    return hallazgos


def _reconciliar_advertencias(
    cur, importacion_id: int, nombre_hoja: str, numero_fila: int, hallazgos: list[dict]
) -> None:
    """Deja los incumplimientos de la fila como quedaron después de corregir.

    Antes se marcaba como resuelta cualquier advertencia de esa fila y ese
    campo, sin volver a evaluar la regla y **sin mirar de qué hoja era**: en un
    archivo de varias hojas, corregir la fila 5 de una hoja daba por resuelta la
    fila 5 de la otra. Ahora se resuelve lo que efectivamente dejó de
    incumplirse, se vuelve a abrir lo que sigue incumpliéndose y se registra lo
    que la corrección haya creado.
    """
    cur.execute(
        """
        SELECT id, codigo, campo_id, regla_id, resuelta
        FROM mir_c2_reglas_incumplidas
        WHERE importacion_id = %s AND nombre_hoja = %s AND numero_fila = %s
        """,
        [importacion_id, nombre_hoja, numero_fila],
    )
    registrados = _filas(cur)

    def sena(dato) -> tuple:
        return (dato["codigo"], dato["campo_id"], dato["regla_id"])

    vigentes = {sena(h) for h in hallazgos}
    for reg in registrados:
        sigue = sena(reg) in vigentes
        if bool(reg["resuelta"]) is not sigue:
            continue  # ya está como corresponde
        cur.execute(
            "UPDATE mir_c2_reglas_incumplidas SET resuelta = %s WHERE id = %s",
            [0 if sigue else 1, reg["id"]],
        )

    conocidos = {sena(r) for r in registrados}
    for hallazgo in hallazgos:
        if sena(hallazgo) in conocidos:
            continue
        cur.execute(
            """
            INSERT INTO mir_c2_reglas_incumplidas
                (importacion_id, campo_id, regla_id, codigo, severidad,
                 nombre_hoja, numero_fila, nombre_campo, valor_encontrado,
                 descripcion)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            [
                importacion_id,
                hallazgo["campo_id"],
                hallazgo["regla_id"],
                hallazgo["codigo"],
                hallazgo["severidad"],
                nombre_hoja,
                numero_fila,
                hallazgo["nombre_campo"],
                hallazgo["valor"],
                hallazgo["descripcion"],
            ],
        )


# ---------------------------------------------------------------------------
# Edición
# ---------------------------------------------------------------------------


def _convertir(valor: str, campo: dict, periodo: str | None = None):
    """Convierte lo que escribió el operador al tipo del campo.

    Devuelve (valor, error). Es la misma exigencia que en la importación: no se
    guarda un dato que no respeta lo que la Capa 1 declaró.
    """
    texto = (valor or "").strip()
    if texto == "":
        if campo["obligatorio"]:
            return None, "El campo es obligatorio: no puede quedar vacío."
        return None, None

    if campo["tipo_dato"] == "FECHA":
        for formato in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
            try:
                return datetime.strptime(texto, formato).date(), None
            except ValueError:
                continue
        return None, f'"{texto}" no es una fecha válida. Se espera dd/mm/aaaa.'

    # La interpretación numérica es la MISMA que la de la importación, y por eso
    # se toma de allá: si cada pantalla la resolviera por su cuenta, un valor
    # corregido a mano podría guardarse distinto del que entró por el archivo.
    if campo["tipo_dato"] in ("ENTERO", "DECIMAL"):
        limpio = texto_a_numero(texto) or ""
        if campo["tipo_dato"] == "ENTERO":
            if re.fullmatch(r"-?\d+", limpio):
                return int(limpio), None
            if re.fullmatch(r"-?\d+\.\d+", limpio):
                return (
                    None,
                    f'"{texto}" tiene decimales y se esperaba un número entero.',
                )
            return None, f'"{texto}" no es un número entero.'
        try:
            return float(limpio), None
        except ValueError:
            return None, f'"{texto}" no es un número.'

    maximo = campo.get("longitud_maxima")
    if maximo and len(texto) > maximo:
        return None, f"El texto tiene {len(texto)} caracteres y el máximo es {maximo}."

    if campo.get("catalogo"):
        admitidos = opciones_de(campo["catalogo"], periodo)
        if admitidos and texto not in admitidos:
            return None, "El valor no está entre los admitidos para este campo."

    return texto, None


def _vigente(cur, presentacion_id: int, codigo: str) -> dict | None:
    """La importación vigente de un archivo en la presentación, con su versión."""
    cur.execute(
        """
        SELECT i.id, av.id AS version_id, av.numero AS version
        FROM mir_c2_importacion i
        JOIN mir_c1_archivo a ON a.id = i.archivo_id
        JOIN mir_c1_archivo_version av ON av.id = i.archivo_version_id
        WHERE i.presentacion_id = %s AND a.codigo = %s AND i.estado = 'VALIDA'
        ORDER BY i.id DESC LIMIT 1
        """,
        [presentacion_id, codigo],
    )
    filas = _filas(cur)
    return filas[0] if filas else None


def _tablas_de(cur, codigo: str, vigente: dict) -> list[dict]:
    """Las hojas de la versión vigente de un archivo, con su tabla y sus campos."""
    cur.execute(
        """SELECT h.id, h.nombre_esperado,
                  GROUP_CONCAT(c.nombre SEPARATOR '|') AS campos
           FROM mir_c1_hoja h JOIN mir_c1_campo c ON c.hoja_id = h.id
           WHERE h.archivo_version_id = %s
           GROUP BY h.id""",
        [vigente["version_id"]],
    )
    hojas = _filas(cur)
    varias = len(hojas) > 1
    for h in hojas:
        h["campos"] = set((h["campos"] or "").split("|"))
        h["tabla"] = _identificador_seguro(
            nombre_tabla_receptora(
                codigo, h["nombre_esperado"], varias, vigente["version"]
            )
        )
    return hojas


def _usos_del_dato(
    cur, contexto: dict, hoja: dict, numero_fila: int, fila: dict, campo: str
) -> list[dict]:
    """Las filas de OTROS archivos que usan este dato, con su valor de hoy.

    Son las que cuelgan de las reglas entre archivos (EXISTE_EN_ARCHIVO y
    COINCIDE_CON_ARCHIVO) que apuntan a este archivo y a este campo, en la
    importación vigente de la misma presentación. Si otra fila de este mismo
    archivo sigue teniendo el valor viejo, las que lo nombran no quedan
    huérfanas y no se tocan.
    """
    anterior = fila.get(campo)
    if anterior is None or str(anterior).strip() == "":
        return []
    codigo = contexto["archivo_codigo"]
    presentacion_id = contexto["presentacion_id"]
    cur.execute(
        """
        SELECT tr.nombre AS tipo, r.parametros, c.nombre AS campo_hijo,
               c.titulo_esperado AS titulo_hijo, h.id AS hoja_id,
               h.nombre_esperado AS hoja, av.id AS version_id, a.codigo AS archivo
        FROM mir_c1_campo_regla cr
        JOIN mir_c1_regla r ON r.id = cr.regla_id
        JOIN mir_c1_tipo_regla tr ON tr.id = r.tipo_regla_id
        JOIN mir_c1_campo c ON c.id = cr.campo_id
        JOIN mir_c1_hoja h ON h.id = c.hoja_id
        JOIN mir_c1_archivo_version av ON av.id = h.archivo_version_id
        JOIN mir_c1_archivo a ON a.id = av.archivo_id
        WHERE tr.nombre IN ('EXISTE_EN_ARCHIVO', 'COINCIDE_CON_ARCHIVO')
        """
    )
    reglas = _filas(cur)
    usos: dict[tuple, dict] = {}
    for regla in reglas:
        crudo = regla["parametros"]
        if isinstance(crudo, (bytes, bytearray)):
            crudo = crudo.decode("utf-8")
        par = crudo if isinstance(crudo, dict) else json.loads(crudo or "{}")
        if par.get("archivo") != codigo or par.get("campo") != campo:
            continue
        if par.get("hoja") and par["hoja"] != hoja["nombre_esperado"]:
            continue
        existe = regla["tipo"] == "EXISTE_EN_ARCHIVO"
        llave = None
        if existe:
            # ¿Otra fila de este archivo sigue diciendo lo mismo? Entonces lo
            # que la nombra sigue teniendo a quién nombrar.
            propio = _vigente(cur, presentacion_id, codigo)
            sigue = False
            for h in _tablas_de(cur, codigo, propio) if propio else []:
                if campo not in h["campos"]:
                    continue
                cur.execute(
                    f"SELECT numero_fila, `{_identificador_seguro(campo)}` FROM `{h['tabla']}` "
                    "WHERE importacion_id = %s",
                    [propio["id"]],
                )
                for n, v in cur.fetchall():
                    if h["id"] == hoja["id"] and n == numero_fila:
                        continue
                    if clave(v) == clave(anterior):
                        sigue = True
                        break
                if sigue:
                    break
            if sigue:
                continue
        else:
            llave = fila.get(par.get("clave"))
            if llave is None or str(llave).strip() == "":
                continue
        hijo = _vigente(cur, presentacion_id, regla["archivo"])
        if not hijo or hijo["version_id"] != regla["version_id"]:
            continue
        tabla_hijo = next(
            (
                h
                for h in _tablas_de(cur, regla["archivo"], hijo)
                if h["id"] == regla["hoja_id"]
            ),
            None,
        )
        if not tabla_hijo:
            continue
        campos_hijo = campos_de_la_hoja(regla["hoja_id"])
        columnas = ", ".join(
            f"`{_identificador_seguro(c['nombre'])}`" for c in campos_hijo
        )
        cur.execute(
            f"SELECT numero_fila, {columnas} FROM `{tabla_hijo['tabla']}` "
            "WHERE importacion_id = %s ORDER BY numero_fila",
            [hijo["id"]],
        )
        nombres = ["numero_fila"] + [c["nombre"] for c in campos_hijo]
        for valores in cur.fetchall():
            f = dict(zip(nombres, valores))
            if clave(f.get(regla["campo_hijo"])) != clave(anterior):
                continue
            if not existe and clave(f.get(par.get("clave"))) != clave(llave):
                continue
            grupo = usos.setdefault(
                (hijo["id"], regla["hoja_id"], regla["campo_hijo"]),
                {
                    "archivo": regla["archivo"],
                    "importacion_id": hijo["id"],
                    "hoja_id": regla["hoja_id"],
                    "hoja": regla["hoja"],
                    "campo": regla["campo_hijo"],
                    "campo_titulo": regla["titulo_hijo"],
                    "filas": [],
                },
            )
            if all(x["numero_fila"] != f["numero_fila"] for x in grupo["filas"]):
                grupo["filas"].append(
                    {
                        "numero_fila": f["numero_fila"],
                        "identificacion": identificacion_de_la_fila(campos_hijo, f),
                    }
                )
    return list(usos.values())


@transaction.atomic
def editar(
    importacion_id: int,
    hoja_id: int,
    numero_fila: int,
    nombre_campo: str,
    valor_nuevo: str,
    usuario: str,
    motivo: str = "",
    en_cascada: bool = False,
) -> dict[str, Any]:
    """Corrige un dato y deja constancia. Devuelve el valor guardado.

    Si el dato lo usan filas de otros archivos, sin `en_cascada` no se toca
    nada y se levanta `HaceFaltaConfirmar` con esas filas; con `en_cascada`,
    se corrigen también, cada una con su constancia. Todo entra junto o nada.
    """
    contexto = contexto_de(importacion_id)
    if not contexto:
        raise EdicionNoPermitida("No existe esa importación.")
    if not contexto["editable"]:
        raise EdicionNoPermitida(
            f'La presentación está en «{contexto["estado_presentacion"]}». '
            "Para corregir, primero hay que reabrir la carga."
        )
    if contexto["estado_importacion"] != "VALIDA":
        raise EdicionNoPermitida(
            "Esa importación no incorporó datos: no hay nada que editar. "
            "Se corrige el Excel y se vuelve a importar."
        )

    hoja = next((h for h in contexto["hojas"] if h["id"] == int(hoja_id)), None)
    if not hoja:
        raise EdicionNoPermitida("La hoja no pertenece a esta importación.")

    campos = campos_de_la_hoja(hoja["id"])
    campo = next((c for c in campos if c["nombre"] == nombre_campo), None)
    if not campo:
        raise EdicionNoPermitida("El campo no pertenece a esta hoja.")

    valor, error = _convertir(valor_nuevo, campo, contexto["periodo"])
    if error:
        raise EdicionNoPermitida(error)

    varias = len(contexto["hojas"]) > 1
    tabla = _identificador_seguro(
        nombre_tabla_receptora(
            contexto["archivo_codigo"],
            hoja["nombre_esperado"],
            varias,
            contexto["version"],
        )
    )
    columna = _identificador_seguro(campo["nombre"])

    with connection.cursor() as cur:
        # La fila entera, no sólo la celda: hace falta para volver a aplicar las
        # reglas que comparan un campo con otro.
        todas = ", ".join(f"`{_identificador_seguro(c['nombre'])}`" for c in campos)
        cur.execute(
            f"SELECT {todas} FROM `{tabla}` "
            "WHERE importacion_id = %s AND numero_fila = %s",
            [importacion_id, numero_fila],
        )
        actual = cur.fetchone()
        if actual is None:
            raise EdicionNoPermitida("No existe esa fila en la importación.")
        fila_actual = dict(zip([c["nombre"] for c in campos], actual))
        valor_anterior = fila_actual[campo["nombre"]]

        if str(valor_anterior or "") == str(valor or ""):
            return {"sin_cambios": True, "valor": valor_anterior}

        # Lo que usa este dato en otros archivos, con el valor de antes.
        usos = _usos_del_dato(
            cur, contexto, hoja, numero_fila, fila_actual, campo["nombre"]
        )
        if usos and not en_cascada:
            raise HaceFaltaConfirmar(usos)

        # Antes de guardar: cómo queda la fila con el valor nuevo. Un dato que
        # deja la fila con un error bloqueante no se guarda —el archivo entró
        # porque no tenía ninguno, y una corrección no puede romper eso—.
        fila_nueva = {**fila_actual, campo["nombre"]: valor}
        hallazgos = hallazgos_de_la_fila(
            campos, fila_nueva, contexto["periodo"], contexto["presentacion_id"]
        )
        bloqueantes = [h for h in hallazgos if h["severidad"] == "BLOQUEANTE"]
        if bloqueantes:
            raise EdicionNoPermitida(
                "Con ese valor la fila queda con un error que impide la carga: "
                + bloqueantes[0]["descripcion"]
            )

        cur.execute(
            f"UPDATE `{tabla}` SET `{columna}` = %s "
            "WHERE importacion_id = %s AND numero_fila = %s",
            [valor, importacion_id, numero_fila],
        )

        # Si el dato estaba observado, corregirlo lo subsana: la jurisdicción
        # no tiene que ir a responder aparte (27-09-2026). Con el mismo
        # cursor, para que entren las dos cosas o ninguna.
        observacion_id = circuito.subsanar_al_corregir(
            cur,
            importacion_id,
            numero_fila,
            campo["id"],
            usuario,
            valor_anterior,
            valor,
            motivo,
        )

        # La constancia: quién, cuándo, qué había y qué quedó, y a qué
        # observación respondió, si respondió a alguna.
        cur.execute(
            """
            INSERT INTO mir_c2_historial_cambios
                (importacion_id, numero_fila, campo_id, observacion_id,
                 valor_anterior, valor_nuevo, motivo, usuario)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            [
                importacion_id,
                numero_fila,
                campo["id"],
                observacion_id,
                None if valor_anterior is None else str(valor_anterior),
                None if valor is None else str(valor),
                (motivo or "").strip() or None,
                usuario,
            ],
        )

        # Qué advertencias quedan realmente incumplidas después de la
        # corrección, en esta hoja y en esta fila.
        _reconciliar_advertencias(
            cur, importacion_id, hoja["nombre_esperado"], numero_fila, hallazgos
        )

        # El estado de la fila lo deciden las advertencias que quedan, no el
        # hecho de haberla tocado: una fila corregida del todo vuelve a ser
        # VALIDA y deja de aparecer en el filtro «sólo con advertencias».
        cur.execute(
            f"UPDATE `{tabla}` SET estado = %s "
            "WHERE importacion_id = %s AND numero_fila = %s",
            [
                "CON_ADVERTENCIA" if hallazgos else "EDITADA",
                importacion_id,
                numero_fila,
            ],
        )

    # Y las filas de otros archivos que lo usaban pasan al valor nuevo, cada
    # una con su constancia. Si alguna no puede, no entra nada: es la misma
    # transacción.
    actualizadas = 0
    origen = con_nombres_de_archivo(contexto["archivo_codigo"])
    for grupo in usos:
        for f in grupo["filas"]:
            editar(
                importacion_id=grupo["importacion_id"],
                hoja_id=grupo["hoja_id"],
                numero_fila=f["numero_fila"],
                nombre_campo=grupo["campo"],
                valor_nuevo=valor_nuevo,
                usuario=usuario,
                motivo=(
                    f"Actualizado junto con {origen}, fila {numero_fila}: "
                    f"«{valor_anterior}» por «{valor}»."
                ),
                en_cascada=True,
            )
            actualizadas += 1

    return {
        "sin_cambios": False,
        "en_cascada": actualizadas,
        "valor": valor,
        "anterior": valor_anterior,
        "advertencias": len(hallazgos),
        # Lo que quedó observado EN ESTE CAMPO, con su texto. Devolver sólo el
        # total de la fila confundía: se corregía el dato y el número no bajaba,
        # porque contaba también las observaciones de los otros campos.
        "observaciones": [
            con_nombres_de_archivo(
                en_palabras.problema_en_palabras(h.get("codigo"), h["descripcion"])
            )
            for h in hallazgos
            if h["campo_id"] == campo["id"]
        ],
    }


def cantidad_de_correcciones(importacion_id: int) -> int:
    """Cuántas correcciones se hicieron dentro del sistema sobre esta importación.

    Es lo que se pierde si se la reemplaza, y por eso se dice antes de hacerlo.
    """
    with connection.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) FROM mir_c2_historial_cambios WHERE importacion_id = %s",
            [importacion_id],
        )
        return cur.fetchone()[0]


def historial_de(
    importacion_id: int, numero_fila: int | None = None, limite: int | None = 200
) -> list[dict]:
    """Las correcciones hechas sobre esta importación, la más reciente primero.

    `limite=None` las trae todas: es lo que usa la descarga del historial.
    """
    sql = """
        SELECT h.numero_fila, h.valor_anterior, h.valor_nuevo, h.motivo,
               h.fecha, h.usuario, h.identificador_registro,
               c.titulo_esperado AS campo
        FROM mir_c2_historial_cambios h
        LEFT JOIN mir_c1_campo c ON c.id = h.campo_id
        WHERE h.importacion_id = %s
    """
    parametros: list[Any] = [importacion_id]
    if numero_fila is not None:
        sql += " AND h.numero_fila = %s"
        parametros.append(numero_fila)
    sql += " ORDER BY h.fecha DESC, h.id DESC"
    if limite:
        sql += " LIMIT %s"
        parametros.append(limite)
    with connection.cursor() as cur:
        cur.execute(sql, parametros)
        cambios = _filas(cur)

    documentos = _documentos_de(importacion_id)
    for cambio in cambios:
        cambio["documento"] = documentos.get(cambio["numero_fila"], "")
    return cambios


def _documentos_de(importacion_id: int) -> dict[int, str]:
    """El documento de cada fila, para poder leer el historial.

    «Fila 6» no le dice nada a nadie: identifica la posición en el Excel, no a
    la persona. Con el documento al lado, el historial se puede contrastar con
    el expediente sin volver a abrir el archivo.

    En los archivos de dispositivos no hay documento —no son personas— y la
    columna queda vacía, sin que eso sea un problema.
    """
    contexto = contexto_de(importacion_id)
    if not contexto:
        return {}

    varias = len(contexto["hojas"]) > 1
    documentos: dict[int, str] = {}
    for hoja in contexto["hojas"]:
        tabla = nombre_tabla_receptora(
            contexto["archivo_codigo"],
            hoja["nombre_esperado"],
            varias,
            contexto["version"],
        )
        with connection.cursor() as cur:
            cur.execute(
                """SELECT 1 FROM information_schema.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s
                      AND COLUMN_NAME = 'n_dni'""",
                [tabla],
            )
            if not cur.fetchone():
                continue
            cur.execute(
                f"SELECT numero_fila, `n_dni` FROM `{_identificador_seguro(tabla)}` "
                "WHERE importacion_id = %s",
                [importacion_id],
            )
            documentos.update({f[0]: f[1] or "" for f in cur.fetchall()})
    return documentos
