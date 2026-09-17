"""Compara las tablas receptoras con lo que declara la Capa 1.

    python sincronizar_receptoras.py            # informa, no toca nada
    python sincronizar_receptoras.py --aplicar  # afloja lo que corresponde

La tabla receptora se genera a partir de la definición: una columna sale
NOT NULL porque el campo es obligatorio. Si después la obligatoriedad cambia
—por ejemplo, porque pasa a ser condicional— la tabla queda más exigente que la
definición y la importación falla al insertar.

Esto vive en Python y no en un guion SQL porque **el nombre de la tabla
receptora no está guardado en ningún lado: se deduce por convención**, con la
misma función que usan el generador y el importador. Un SQL que quisiera
reconstruirlo tendría que repetir esa convención, y el día que cambiara habría
dos versiones de la verdad.

Sólo AFLOJA restricciones —de NOT NULL a NULL—, nunca al revés. Endurecer una
columna puede fallar sobre datos ya cargados, y eso no es algo que un script
deba decidir solo: lo informa y lo decide una persona.
"""

from __future__ import annotations

import argparse
import os

import mysql.connector

from comun import nombre_tabla_receptora

CONEXION = dict(
    host=os.environ.get("RUNAC_DB_HOST", "mysql"),
    port=3306,
    user="root",
    password="runac_local",
    database="runac",
)


def definicion(cur) -> dict[str, dict[str, int]]:
    """Qué columnas espera cada tabla receptora, y si admiten vacío.

    Devuelve {tabla: {columna: obligatorio}}. Recorre TODAS las versiones, no
    sólo las vigentes: una versión histórica conserva su tabla y sus datos.
    """
    cur.execute(
        """
        SELECT a.codigo, av.numero AS version, h.nombre_esperado AS hoja,
               c.nombre AS campo, c.obligatorio,
               (SELECT COUNT(*) FROM mir_c1_hoja h2
                 WHERE h2.archivo_version_id = av.id) AS hojas
        FROM mir_c1_campo c
        JOIN mir_c1_hoja h ON h.id = c.hoja_id
        JOIN mir_c1_archivo_version av ON av.id = h.archivo_version_id
        JOIN mir_c1_archivo a ON a.id = av.archivo_id
        """
    )
    esperado: dict[str, dict[str, int]] = {}
    for f in cur.fetchall():
        tabla = nombre_tabla_receptora(
            f["codigo"], f["hoja"], f["hojas"] > 1, f["version"]
        )
        esperado.setdefault(tabla, {})[f["campo"]] = int(f["obligatorio"])
    return esperado


def realidad(cur) -> dict[str, dict[str, tuple[str, bool]]]:
    """Cómo están hoy las columnas de las tablas receptoras que existen."""
    cur.execute(
        """
        SELECT TABLE_NAME AS tabla, COLUMN_NAME AS columna,
               COLUMN_TYPE AS tipo, IS_NULLABLE AS admite_vacio
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME LIKE 'runac\\_c2\\_%'
        """
    )
    actual: dict[str, dict[str, tuple[str, bool]]] = {}
    for f in cur.fetchall():
        actual.setdefault(f["tabla"], {})[f["columna"]] = (
            f["tipo"],
            f["admite_vacio"] == "YES",
        )
    return actual


def diferencias(esperado, actual):
    """Las columnas donde la tabla y la definición no coinciden.

    Devuelve dos listas: las que hay que aflojar y las que habría que endurecer.
    """
    aflojar, endurecer = [], []
    for tabla, campos in esperado.items():
        columnas = actual.get(tabla)
        if not columnas:
            continue  # la tabla de esa versión todavía no se creó
        for campo, obligatorio in campos.items():
            if campo not in columnas:
                continue
            tipo, admite_vacio = columnas[campo]
            if not obligatorio and not admite_vacio:
                aflojar.append((tabla, campo, tipo))
            elif obligatorio and admite_vacio:
                endurecer.append((tabla, campo, tipo))
    return sorted(aflojar), sorted(endurecer)


def main():
    p = argparse.ArgumentParser(
        description="Compara las tablas receptoras con la definición de la Capa 1."
    )
    p.add_argument(
        "--aplicar",
        action="store_true",
        help="afloja las columnas que la Capa 1 declara opcionales",
    )
    args = p.parse_args()

    cn = mysql.connector.connect(**CONEXION)
    cur = cn.cursor(dictionary=True)
    aflojar, endurecer = diferencias(definicion(cur), realidad(cur))
    cur.close()

    if not aflojar and not endurecer:
        print("Las tablas receptoras coinciden con la Capa 1.")
        cn.close()
        return

    if aflojar:
        print(f"\nColumnas NOT NULL que la Capa 1 declara opcionales ({len(aflojar)}):")
        for tabla, campo, tipo in aflojar:
            print(f"  {tabla}.{campo}  ({tipo})")
        if args.aplicar:
            cur = cn.cursor()
            for tabla, campo, tipo in aflojar:
                cur.execute(f"ALTER TABLE `{tabla}` MODIFY `{campo}` {tipo} NULL")
            cn.commit()
            cur.close()
            print(f"  → {len(aflojar)} aflojadas.")
        else:
            print("  (no se tocó nada: correr con --aplicar)")

    if endurecer:
        # No se aplica: podría fallar sobre datos ya cargados, y además suele
        # ser señal de una decisión funcional pendiente y no de un descuido.
        print(
            f"\nColumnas que admiten vacío y la Capa 1 declara obligatorias "
            f"({len(endurecer)}). NO se modifican: revisar una por una."
        )
        for tabla, campo, tipo in endurecer:
            print(f"  {tabla}.{campo}  ({tipo})")

    cn.close()


if __name__ == "__main__":
    main()
