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

from django.db import connection, transaction

SEVERIDADES = ("ADVERTENCIA", "BLOQUEANTE")


class NoSePuede(Exception):
    """Lo pedido no se puede hacer, con un motivo que se le muestra a la persona."""


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
    if severidad not in SEVERIDADES:
        raise NoSePuede(f"«{severidad}» no es una severidad válida.")

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
def cambiar_limites(aplicacion_id: int, minimo, maximo) -> dict:
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

    nuevos = _limites(minimo, maximo)
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
    cambios = {"creadas": 0, "cambiadas": 0, "quitadas": 0, "desprendidas": 0}

    for severidad, crudos in (("ADVERTENCIA", avisa), ("BLOQUEANTE", frena)):
        limites = _limites(*crudos)
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
                resultado = cambiar_limites(existente, *crudos)
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


# ---------------------------------------------------------------------------
# Interno
# ---------------------------------------------------------------------------


def _limites(minimo, maximo) -> dict:
    """Los dos extremos, ya validados. Vacío significa «sin ese extremo»."""
    salida = {}
    for clave, crudo in (("minimo", minimo), ("maximo", maximo)):
        if crudo is None or str(crudo).strip() == "":
            continue
        try:
            numero = float(str(crudo).replace(",", "."))
        except ValueError as error:
            raise NoSePuede(f"«{crudo}» no es un número.") from error
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
