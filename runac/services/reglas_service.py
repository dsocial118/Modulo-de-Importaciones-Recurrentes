"""Editar una regla desde la pantalla, sin tocar código.

El módulo promete que «cambiar una regla es cambiar un dato». Hasta ahora eso
era cierto para nosotros —con un UPDATE— y no para quien usa el sistema. Acá
está la parte que lo vuelve cierto para el responsable nacional.

Alcance deliberado: **se cambia lo que ya existe**, no se crean reglas nuevas.
Dos cosas, que son las que se piden todo el tiempo:

  - la **severidad**: si el control avisa o frena;
  - los **límites** de un rango: mínimo y máximo.

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
            regla_id = _crear_regla(cur, actual, parametros)
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


def _crear_regla(cur, actual: dict, parametros: dict) -> int:
    """Una regla nueva con los valores nuevos, derivada de la que se desprendió.

    El nombre lleva el identificador de la aplicación porque la columna es
    única y dos campos pueden terminar con los mismos límites por caminos
    distintos.
    """
    nombre = f'{actual["nombre"]}__ap{actual["id"]}'[:255]
    descripcion = _descripcion(parametros) or actual["descripcion"]
    cur.execute(
        "INSERT INTO mir_c1_regla (tipo_regla_id, nombre, descripcion, parametros)"
        " VALUES (%s, %s, %s, %s)",
        [
            actual["tipo_id"],
            nombre,
            descripcion,
            json.dumps(parametros, ensure_ascii=False),
        ],
    )
    cur.execute("SELECT LAST_INSERT_ID()")
    return cur.fetchone()[0]


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
