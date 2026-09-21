"""Editar una regla desde la pantalla, sin tocar código.

El módulo promete que «cambiar una regla es cambiar un dato». Hasta ahora eso
era cierto para nosotros —con un UPDATE— y no para quien usa el sistema. Acá
está la parte que lo vuelve cierto para el responsable nacional.

Alcance deliberado, porque son las dos cosas que se piden todo el tiempo:

  - la **severidad**: si el control avisa o frena;
  - los **límites** de un rango: mínimo y máximo, para lo que avisa y para lo
    que frena, y en un solo formulario de cuatro casilleros.

Ese formulario también **crea y quita**: un casillero vacío que se completa es
una regla nueva, y uno que se vacía la quita. No hace falta una pantalla aparte
para eso, y el rango es el tipo de regla más usado con diferencia. Los otros
nueve tipos todavía se cargan desde la definición.

LO QUE HAY QUE SABER ANTES DE LEER EL CÓDIGO
--------------------------------------------

Una regla y su aplicación son cosas distintas:

    mir_c1_regla         «entre 0 y 5000». Una sola fila, REUTILIZABLE.
    mir_c1_campo_regla   esa regla aplicada a un campo, con su severidad.

Y las reglas **están compartidas**: al escribir esto había 90 reglas para 156
aplicaciones, y la de «máximo 5000» la usaban catorce campos. Editarla sin más
cambiaría los catorce de una vez, que es exactamente lo que quien edita no
espera.

Por eso `cambiar_limites()` **desprende**: si la regla está compartida, la
aplicación pasa a apuntar a otra regla con los valores nuevos, y las demás
quedan intactas. Es invisible para quien edita, y es lo que evita el accidente.

La severidad no necesita nada de esto: vive en la aplicación, así que ya es
propia de cada campo.
"""

import json
import re

from django.db import connection, transaction

SEVERIDADES = ("ADVERTENCIA", "BLOQUEANTE")


class NoSePuede(Exception):
    """Lo pedido no se puede hacer, con un motivo que se le muestra a la persona."""


class ErroresDeValidacion(NoSePuede):
    """Varios problemas a la vez, para corregirlos de una pasada y no de a uno."""

    def __init__(self, errores: list):
        self.errores = errores
        super().__init__(" · ".join(errores))


# ---------------------------------------------------------------------------
# Cuándo se puede cambiar la definición
# ---------------------------------------------------------------------------


def periodo_abierto():
    """El período en curso, si hay alguno abierto.

    **La definición se cambia antes de que arranque el operativo, y no
    después.** Con un período abierto hay provincias cargando contra las reglas
    que se les comunicaron: moverlas a mitad de camino significa que dos
    provincias presentaron lo mismo y a una le fue bien y a la otra mal.

    Que quede fuera del sistema es deliberado: si aparece algo que de verdad no
    puede esperar, se hace de manera controlada y con constancia, no con un
    casillero. La regla es del responsable funcional, del 21-09-2026.
    """
    with connection.cursor() as cur:
        cur.execute(
            "SELECT codigo FROM mir_c2_periodo WHERE estado = 'ABIERTO' ORDER BY codigo LIMIT 1"
        )
        fila = cur.fetchone()
    return fila[0] if fila else None


def exigir_periodo_en_preparacion():
    """Freno común a todo lo que cambia la definición."""
    abierto = periodo_abierto()
    if abierto:
        raise NoSePuede(
            f"El período {abierto} ya está abierto: con el operativo en curso la "
            "definición no se cambia. Si hace falta corregir algo, se hace de "
            "manera controlada y fuera del sistema."
        )


# ---------------------------------------------------------------------------
# Consulta
# ---------------------------------------------------------------------------


def aplicacion(aplicacion_id: int) -> dict:
    """Una regla aplicada a un campo, con todo lo que hace falta para editarla."""
    with connection.cursor() as cur:
        cur.execute(
            """
            SELECT cr.id, cr.campo_id, cr.severidad,
                   r.id AS regla_id, r.nombre, r.descripcion, r.parametros,
                   tr.id AS tipo_id, tr.nombre AS tipo,
                   c.titulo_esperado AS campo,
                   (SELECT COUNT(*) FROM mir_c1_campo_regla x
                     WHERE x.regla_id = r.id) AS usos
              FROM mir_c1_campo_regla cr
              JOIN mir_c1_regla r ON r.id = cr.regla_id
              JOIN mir_c1_tipo_regla tr ON tr.id = r.tipo_regla_id
              JOIN mir_c1_campo c ON c.id = cr.campo_id
             WHERE cr.id = %s
            """,
            [aplicacion_id],
        )
        fila = cur.fetchone()
        if not fila:
            raise NoSePuede("Esa regla no existe.")
        nombres = [d[0] for d in cur.description]

    datos = dict(zip(nombres, fila))
    par = datos["parametros"]
    datos["parametros"] = json.loads(par) if isinstance(par, str) else (par or {})
    return datos


# ---------------------------------------------------------------------------
# Cambios
# ---------------------------------------------------------------------------


def cambiar_severidad(aplicacion_id: int, severidad: str) -> dict:
    """Si el control avisa o frena. Es propio del campo: no afecta a nadie más."""
    # Primero lo que no necesita la base: un valor inválido se rechaza sin ir a
    # preguntar en qué estado está el período.
    if severidad not in SEVERIDADES:
        raise NoSePuede(f"«{severidad}» no es una severidad válida.")
    exigir_periodo_en_preparacion()

    actual = aplicacion(aplicacion_id)
    if actual["severidad"] == severidad:
        return {"cambio": False, "desprendida": False}

    with connection.cursor() as cur:
        cur.execute(
            "UPDATE mir_c1_campo_regla SET severidad = %s WHERE id = %s",
            [severidad, aplicacion_id],
        )
    return {"cambio": True, "desprendida": False, "desde": actual["severidad"]}


@transaction.atomic
def cambiar_limites(aplicacion_id: int, minimo, maximo, entero: bool = False) -> dict:
    """Los límites de un rango. Desprende la regla si estaba compartida.

    `minimo` y `maximo` pueden venir vacíos: un rango con un solo extremo es
    válido —«no puede ser negativo», sin techo— y es lo que permite escribir la
    regla que hace falta sin inventar el otro número.
    """
    actual = aplicacion(aplicacion_id)
    if actual["tipo"] != "RANGO":
        raise NoSePuede(
            f'Los límites sólo se cambian en reglas de rango, y ésta es «{actual["tipo"]}».'
        )

    nuevos = _limites(minimo, maximo, entero=entero)
    if nuevos == {
        k: v for k, v in actual["parametros"].items() if k in ("minimo", "maximo")
    }:
        return {"cambio": False, "desprendida": False}
    if not nuevos:
        raise NoSePuede("Hay que indicar al menos un límite: mínimo, máximo o los dos.")

    # Los parámetros que la regla tuviera además de los límites se conservan:
    # no es asunto de esta pantalla borrarlos.
    parametros = {**actual["parametros"], **nuevos}
    for sobra in ("minimo", "maximo"):
        if sobra not in nuevos:
            parametros.pop(sobra, None)

    desprendida = actual["usos"] > 1
    with connection.cursor() as cur:
        if not desprendida:
            cur.execute(
                "UPDATE mir_c1_regla SET parametros = %s WHERE id = %s",
                [json.dumps(parametros, ensure_ascii=False), actual["regla_id"]],
            )
            return {
                "cambio": True,
                "desprendida": False,
                "regla_id": actual["regla_id"],
            }

        # Compartida: esta aplicación pasa a apuntar a otra regla. Si ya existe
        # una idéntica se reusa, para no llenar el catálogo de duplicados.
        regla_id = _regla_equivalente(cur, actual["tipo_id"], parametros)
        if regla_id is None:
            regla_id = _crear_regla(
                cur,
                actual["tipo_id"],
                f'{actual["nombre"]}__ap{actual["id"]}',
                parametros,
            )
        cur.execute(
            "UPDATE mir_c1_campo_regla SET regla_id = %s WHERE id = %s",
            [regla_id, aplicacion_id],
        )
    return {
        "cambio": True,
        "desprendida": True,
        "regla_id": regla_id,
        "otros_campos": actual["usos"] - 1,
    }


@transaction.atomic
def guardar_rangos(campo_id: int, avisa: tuple, frena: tuple) -> dict:
    """Los dos techos de un campo, en una sola operación.

    La pantalla muestra **un renglón por campo** con cuatro casilleros —mínimo y
    máximo de lo que avisa, mínimo y máximo de lo que frena— en vez de un
    renglón por regla. Es como se piensa el control: «más de 200 es raro, más de
    2.000 es imposible» es una definición, no dos.

    Y ese formulario hace las tres cosas sin pantallas aparte:

        casillero vacío que se completa   ->  la regla se CREA
        valor que cambia                  ->  la regla se MODIFICA
        casillero que se vacía            ->  la regla se QUITA

    Que quitar sea vaciar un casillero es deliberado: deja a la vista qué
    campos no tienen control, que es la pregunta que nadie se estaba haciendo.
    """
    exigir_periodo_en_preparacion()
    cambios = {"creadas": 0, "cambiadas": 0, "quitadas": 0, "desprendidas": 0}
    entero = _datos_de_campos([campo_id]).get(campo_id, {}).get("tipo") == "ENTERO"

    for severidad, crudos in (("ADVERTENCIA", avisa), ("BLOQUEANTE", frena)):
        limites = _limites(*crudos, entero=entero)
        with connection.cursor() as cur:
            existente = _rango_del_campo(cur, campo_id, severidad)

            if not limites:
                if existente:
                    cur.execute(
                        "DELETE FROM mir_c1_campo_regla WHERE id = %s", [existente]
                    )
                    cambios["quitadas"] += 1
                continue

            if existente:
                resultado = cambiar_limites(existente, *crudos, entero=entero)
                if resultado["cambio"]:
                    cambios["cambiadas"] += 1
                    cambios["desprendidas"] += 1 if resultado["desprendida"] else 0
                continue

            tipo_id = _tipo_rango(cur)
            regla_id = _regla_equivalente(cur, tipo_id, limites)
            if regla_id is None:
                regla_id = _crear_regla(
                    cur, tipo_id, f"rango_campo{campo_id}_{severidad.lower()}", limites
                )
            cur.execute(
                "INSERT INTO mir_c1_campo_regla (campo_id, regla_id, severidad)"
                " VALUES (%s, %s, %s)",
                [campo_id, regla_id, severidad],
            )
            cambios["creadas"] += 1

    cambios["hubo"] = any(cambios[k] for k in ("creadas", "cambiadas", "quitadas"))
    return cambios


def guardar_hoja(cambios: dict, severidades: dict = None) -> dict:
    """Guarda de una sola vez todo lo que se tocó en la hoja.

    La pantalla no tiene un botón por fila sino uno solo arriba: quien revisa
    una hoja de sesenta columnas ajusta varias y guarda una vez, y un botón por
    fila es un botón que alguien no va a apretar.

    **O entra todo o no entra nada.** Primero se valida la hoja entera; si algo
    falla no se escribe una sola fila y se devuelven todos los problemas juntos,
    para que se corrijan de una pasada. Guardar la mitad y callarse la otra
    mitad es peor que no guardar.

    `cambios` es, por campo: `obligatorio`, `advierte` y `bloquea`, y cada uno
    puede faltar —sólo llega lo que se tocó—.
    """
    exigir_periodo_en_preparacion()
    severidades = severidades or {}
    if not cambios and not severidades:
        return {"campos": 0, "detalle": []}

    preparados, errores = _revisar_todo(cambios, severidades)
    if errores:
        raise ErroresDeValidacion(errores)

    detalle = []
    with transaction.atomic():
        detalle.extend(_aplicar_severidades(severidades))
        for campo, pedido, rangos in preparados:
            if "obligatorio" in pedido:
                hecho = cambiar_obligatorio(campo["id"], pedido["obligatorio"])
                if hecho["cambio"]:
                    detalle.append(
                        f'«{campo["titulo"]}»: '
                        + (
                            "ahora es obligatoria"
                            if hecho["obligatorio"]
                            else "deja de ser obligatoria"
                        )
                    )
            if rangos is not None:
                hecho = guardar_rangos(campo["id"], *rangos)
                if hecho["hubo"]:
                    detalle.append(f'«{campo["titulo"]}»: {_resumen(hecho)}')

    return {"campos": len(preparados), "detalle": detalle}


def cambiar_obligatorio(campo_id: int, obligatorio: bool) -> dict:
    """Si la columna hay que completarla sí o sí.

    Vive en el campo, no en una regla: es parte de qué se espera del archivo, y
    por eso la plantilla que se le entrega a la provincia también cambia.
    """
    exigir_periodo_en_preparacion()
    with connection.cursor() as cur:
        cur.execute("SELECT obligatorio FROM mir_c1_campo WHERE id = %s", [campo_id])
        fila = cur.fetchone()
        if not fila:
            raise NoSePuede("Ese campo no existe.")
        if bool(fila[0]) == bool(obligatorio):
            return {"cambio": False}
        cur.execute(
            "UPDATE mir_c1_campo SET obligatorio = %s WHERE id = %s",
            [1 if obligatorio else 0, campo_id],
        )
    return {"cambio": True, "obligatorio": bool(obligatorio)}


# ---------------------------------------------------------------------------
# Interno
# ---------------------------------------------------------------------------


def _revisar_todo(cambios: dict, severidades: dict):
    """Valida la hoja entera antes de escribir nada, y junta todos los problemas."""
    campos = _datos_de_campos(list(cambios))
    preparados, errores = [], []

    for campo_id, pedido in cambios.items():
        campo = campos.get(campo_id)
        if campo is None:
            errores.append(f"El campo {campo_id} no existe.")
            continue
        try:
            preparados.append((campo, pedido, _validar_campo(campo, pedido)))
        except NoSePuede as error:
            errores.append(f'«{campo["titulo"]}»: {error}')

    for severidad in severidades.values():
        if severidad not in SEVERIDADES:
            errores.append(f"«{severidad}» no es una severidad válida.")

    return preparados, errores


def _aplicar_severidades(severidades: dict) -> list:
    """Cambia si cada condición advierte o bloquea, y cuenta lo que cambió."""
    hechos = []
    for aplicacion_id, severidad in severidades.items():
        datos = aplicacion(aplicacion_id)
        if cambiar_severidad(aplicacion_id, severidad)["cambio"]:
            hechos.append(
                f'«{datos["campo"]}»: la condición ahora '
                + ("bloquea" if severidad == "BLOQUEANTE" else "advierte")
            )
    return hechos


def _datos_de_campos(ids: list) -> dict:
    """Título y tipo de cada campo, que es lo que hace falta para validar."""
    if not ids:
        return {}
    marcas = ", ".join(["%s"] * len(ids))
    with connection.cursor() as cur:
        cur.execute(
            f"SELECT id, titulo_esperado, tipo_dato FROM mir_c1_campo WHERE id IN ({marcas})",
            ids,
        )
        return {
            fila[0]: {"id": fila[0], "titulo": fila[1], "tipo": fila[2]}
            for fila in cur.fetchall()
        }


def _validar_campo(campo: dict, pedido: dict):
    """Revisa los límites de un campo. Devuelve los crudos si hay que guardarlos."""
    if "advierte" not in pedido and "bloquea" not in pedido:
        return None

    entero = campo["tipo"] == "ENTERO"
    advierte = _limites(*pedido.get("advierte", ("", "")), entero=entero)
    bloquea = _limites(*pedido.get("bloquea", ("", "")), entero=entero)
    _exigir_que_bloquea_contenga_a_advierte(advierte, bloquea)
    return (pedido.get("advierte", ("", "")), pedido.get("bloquea", ("", "")))


def _exigir_que_bloquea_contenga_a_advierte(advierte: dict, bloquea: dict):
    """El rango que bloquea tiene que ser el más amplio de los dos.

    Si no, hay valores que frenan el archivo **sin haber advertido nunca**: con
    advierte 20-50 y bloquea 30-40, un 45 bloquea y jamás hubo un aviso. El que
    advierte marca lo normal; el que bloquea, lo posible.
    """
    if not advierte or not bloquea:
        return

    piso_a, piso_b = advierte.get("minimo"), bloquea.get("minimo")
    if piso_a is not None and piso_b is not None and piso_b > piso_a:
        raise NoSePuede(
            f"el rango que bloquea tiene que empezar en {piso_a} o menos: con un mínimo "
            f"de {piso_b} habría valores que frenan sin haber advertido."
        )

    techo_a, techo_b = advierte.get("maximo"), bloquea.get("maximo")
    if techo_a is not None and techo_b is not None and techo_b < techo_a:
        raise NoSePuede(
            f"el rango que bloquea tiene que terminar en {techo_a} o más: con un máximo "
            f"de {techo_b} habría valores que frenan sin haber advertido."
        )


def _resumen(hecho: dict) -> str:
    """Lo que pasó con los rangos de un campo, en una línea."""
    partes = [
        f"{hecho[clave]} {palabra}"
        for clave, palabra in (
            ("creadas", "condición nueva"),
            ("cambiadas", "cambiada"),
            ("quitadas", "quitada"),
        )
        if hecho[clave]
    ]
    return ", ".join(partes)


def _sin_separadores(crudo) -> str:
    """«5.000» y «1,5» escritos como los escribe cualquiera, leídos bien.

    El punto es ambiguo: en «5.000» separa miles y en «5.5» separa decimales.
    Se resuelve por la forma —grupos de exactamente tres cifras— y no por
    adivinanza, así que «5.000» son cinco mil y «5.5» son cinco y medio.
    """
    texto = str(crudo).strip().replace(" ", "")
    if re.fullmatch(r"-?\d{1,3}(\.\d{3})+", texto):
        return texto.replace(".", "")
    if re.fullmatch(r"-?\d{1,3}(\.\d{3})+,\d+", texto):
        return texto.replace(".", "").replace(",", ".")
    return texto.replace(",", ".")


def _limites(minimo, maximo, entero: bool = False) -> dict:
    """Los dos extremos, ya validados. Vacío significa «sin ese extremo».

    `entero` viene del tipo del campo: en una columna que cuenta cosas, un
    límite con decimales no es un límite, es un error de tipeo que después
    rechaza datos buenos.
    """
    salida = {}
    for clave, crudo in (("minimo", minimo), ("maximo", maximo)):
        if crudo is None or str(crudo).strip() == "":
            continue
        try:
            numero = float(_sin_separadores(crudo))
        except ValueError as error:
            raise NoSePuede(f"«{crudo}» no es un número.") from error
        if entero and numero != int(numero):
            raise NoSePuede(
                f"El campo es un número entero: el límite «{crudo}» no puede tener decimales."
            )
        salida[clave] = int(numero) if numero == int(numero) else numero

    if (
        "minimo" in salida
        and "maximo" in salida
        and salida["minimo"] > salida["maximo"]
    ):
        raise NoSePuede("El mínimo no puede ser mayor que el máximo.")
    return salida


def _regla_equivalente(cur, tipo_id: int, parametros: dict):
    """Una regla del mismo tipo y los mismos parámetros, si ya existe."""
    cur.execute(
        "SELECT id, parametros FROM mir_c1_regla WHERE tipo_regla_id = %s",
        [tipo_id],
    )
    for regla_id, crudos in cur.fetchall():
        otros = json.loads(crudos) if isinstance(crudos, str) else (crudos or {})
        if otros == parametros:
            return regla_id
    return None


def _crear_regla(cur, tipo_id: int, base: str, parametros: dict) -> int:
    """Una regla nueva con esos parámetros.

    El nombre tiene que ser único en la tabla, así que se le agrega un sufijo
    hasta que entre. Es un identificador técnico: no se le muestra a nadie.
    """
    nombre = base[:240]
    sufijo = 0
    while True:
        cur.execute("SELECT 1 FROM mir_c1_regla WHERE nombre = %s", [nombre])
        if not cur.fetchone():
            break
        sufijo += 1
        nombre = f"{base[:240]}_{sufijo}"

    cur.execute(
        "INSERT INTO mir_c1_regla (tipo_regla_id, nombre, descripcion, parametros)"
        " VALUES (%s, %s, %s, %s)",
        [
            tipo_id,
            nombre,
            _descripcion(parametros),
            json.dumps(parametros, ensure_ascii=False),
        ],
    )
    cur.execute("SELECT LAST_INSERT_ID()")
    return cur.fetchone()[0]


def _tipo_rango(cur) -> int:
    cur.execute("SELECT id FROM mir_c1_tipo_regla WHERE nombre = 'RANGO'")
    fila = cur.fetchone()
    if not fila:
        raise NoSePuede("El tipo de regla RANGO no está cargado.")
    return fila[0]


def _rango_del_campo(cur, campo_id: int, severidad: str):
    """La aplicación de rango que ese campo tiene con esa severidad, si tiene."""
    cur.execute(
        """
        SELECT cr.id FROM mir_c1_campo_regla cr
          JOIN mir_c1_regla r ON r.id = cr.regla_id
          JOIN mir_c1_tipo_regla tr ON tr.id = r.tipo_regla_id
         WHERE cr.campo_id = %s AND cr.severidad = %s AND tr.nombre = 'RANGO'
         ORDER BY cr.id LIMIT 1
        """,
        [campo_id, severidad],
    )
    fila = cur.fetchone()
    return fila[0] if fila else None


def _descripcion(parametros: dict) -> str:
    """El texto que se ve en la pantalla de reglas, en castellano."""
    minimo, maximo = parametros.get("minimo"), parametros.get("maximo")
    if minimo is not None and maximo is not None:
        return f"El valor debe estar entre {minimo} y {maximo}."
    if maximo is not None:
        return f"El valor no puede ser mayor que {maximo}."
    if minimo is not None:
        return f"El valor no puede ser menor que {minimo}."
    return ""
