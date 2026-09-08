"""Genera un Excel de prueba con datos inventados, leyendo la Capa 1.

    python mock.py --archivo MPI --filas 50
    python mock.py --todos --filas 30 --con-errores

Sirve para probar el importador sin datos reales. Con --con-errores agrega filas
deliberadamente inválidas, una por cada tipo de problema que el importador
debería detectar, para verificar que efectivamente las agarre.

Los datos son inventados. Los nombres salen de una lista corta y los documentos
de un rango que no corresponde a personas reales.
"""

from __future__ import annotations

import argparse
import re
import os
import random
from datetime import date, timedelta

import mysql.connector
from openpyxl import load_workbook

CONEXION = dict(
    host=os.environ.get("RUNAC_DB_HOST", "mysql"),
    port=3306,
    user="root",
    password="runac_local",
    database="runac",
)

NOMBRES = [
    "Ana",
    "Luis",
    "Sofía",
    "Mateo",
    "Valentina",
    "Thiago",
    "Camila",
    "Benjamín",
    "Martina",
    "Joaquín",
    "Emilia",
    "Bautista",
    "Isabella",
    "Lorenzo",
    "Renata",
]
APELLIDOS = [
    "Gómez",
    "Fernández",
    "López",
    "Martínez",
    "Rodríguez",
    "Sosa",
    "Romero",
    "Díaz",
    "Quiroga",
    "Ledesma",
    "Villalba",
    "Cabrera",
    "Ojeda",
    "Paz",
]
CALLES = [
    "San Martín",
    "Belgrano",
    "Rivadavia",
    "Mitre",
    "Sarmiento",
    "Alberdi",
    "Güemes",
]
DISPOSITIVOS = [
    "Hogar Los Álamos",
    "Residencia El Ceibo",
    "Centro Municipal Norte",
    "Programa de Acompañamiento Sur",
    "Hogar Nuestra Señora",
]

# Los documentos van en un rango alto que no corresponde a personas reales.
DOC_DESDE = 90_000_000

# Cada provincia presenta SOLO sus archivos: un mock es de una jurisdicción, y
# todos sus campos de provincia y localidad son coherentes con ella.
LOCALIDADES = {
    "Chubut": [
        "Rawson",
        "Trelew",
        "Comodoro Rivadavia",
        "Puerto Madryn",
        "Esquel",
        "Sarmiento",
        "Gaiman",
        "Dolavon",
        "Rada Tilly",
        "Trevelin",
        "El Maitén",
        "Lago Puelo",
        "El Hoyo",
        "Camarones",
        "Río Mayo",
    ],
    "Chaco": [
        "Resistencia",
        "Barranqueras",
        "Presidencia Roque Sáenz Peña",
        "Villa Ángela",
        "Charata",
        "General San Martín",
        "Las Breñas",
        "Quitilipi",
    ],
    "Salta": [
        "Salta",
        "San Ramón de la Nueva Orán",
        "Tartagal",
        "General Güemes",
        "Rosario de la Frontera",
        "Metán",
        "Cafayate",
    ],
    "Buenos Aires": [
        "La Plata",
        "Mar del Plata",
        "Bahía Blanca",
        "San Isidro",
        "Quilmes",
        "Morón",
        "Lomas de Zamora",
        "Tandil",
    ],
}
LOCALIDAD_POR_DEFECTO = ["Capital", "Centro", "Norte", "Sur"]


def clave_simple(texto) -> str:
    """Forma comparable de un texto: sin tildes, en minúsculas, sin espacios de más."""
    import unicodedata

    t = re.sub(r"\s+", " ", str(texto or "").strip()).lower()
    return "".join(
        c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn"
    )


def digito_cuil(diez: str) -> int:
    """Dígito verificador del CUIL, para que los datos de prueba sean válidos."""
    pesos = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    suma = sum(int(diez[i]) * pesos[i] for i in range(10))
    resto = 11 - (suma % 11)
    return 0 if resto == 11 else (9 if resto == 10 else resto)


def valor_inventado(
    campo: dict,
    opciones: list[str],
    i: int,
    rnd: random.Random,
    fila: dict | None = None,
    jurisdiccion: str | None = None,
):
    t = (campo["titulo_esperado"] or "").lower()
    tipo = campo["tipo_dato"]
    fila = fila if fila is not None else {}

    # Una provincia sube sólo sus archivos: todos los campos de provincia llevan
    # la jurisdicción que presenta. Si el campo tiene lista, se busca el valor
    # que le corresponde dentro de las opciones admitidas.
    if jurisdiccion and "provincia" in t:
        if opciones:
            exacto = next(
                (o for o in opciones if clave_simple(o) == clave_simple(jurisdiccion)),
                None,
            )
            if exacto:
                return exacto
        else:
            return jurisdiccion

    if opciones:
        return rnd.choice(opciones)

    if tipo == "FECHA":
        hoy = date.today()
        if "nacimiento" in t:
            return date(2010, 1, 1) + timedelta(days=rnd.randint(0, 2500))
        # Las fechas de fin van después de las de inicio, y ninguna en el futuro:
        # así los datos "sin errores" pasan limpios y los errores son los que se
        # introducen a propósito.
        if any(p in t for p in ("egreso", "cese", "finaliz", "salida", "fin ")):
            inicio = next(
                (
                    v
                    for k, v in fila.items()
                    if isinstance(v, date)
                    and any(p in k for p in ("ingreso", "inicio", "medida"))
                ),
                None,
            )
            if inicio:
                return min(hoy, inicio + timedelta(days=rnd.randint(1, 200)))
        return hoy - timedelta(days=rnd.randint(1, 700))
    if tipo == "ENTERO":
        if "edad" in t:
            return rnd.randint(3, 17)
        if "capacidad" in t or "plaza" in t:
            return rnd.randint(8, 60)
        if "cantidad" in t or "personal" in t or "agente" in t:
            return rnd.randint(1, 25)
        return rnd.randint(1, 100)
    if tipo == "DECIMAL":
        return round(rnd.uniform(1, 100), 2)

    if "apellido" in t:
        return rnd.choice(APELLIDOS)
    if "nombre" in t and "dispositivo" not in t and "programa" not in t:
        return rnd.choice(NOMBRES)
    if "dni" in t or "documento" in t:
        return str(DOC_DESDE + i * 137 + rnd.randint(0, 90))
    if "cuil" in t:
        diez = f"20{DOC_DESDE + i * 137}"[:10]
        return f"{diez[:2]}-{diez[2:]}-{digito_cuil(diez)}"
    if "mail" in t or "correo" in t:
        return f"contacto{i}@ejemplo.gob.ar"
    if "telefono" in t or "teléfono" in t:
        return f"11-4{rnd.randint(100, 999)}-{rnd.randint(1000, 9999)}"
    if "domicilio" in t or "direccion" in t or "dirección" in t or "calle" in t:
        return f"{rnd.choice(CALLES)} {rnd.randint(100, 4999)}"
    if "codigo postal" in t or "código postal" in t:
        return f"{rnd.choice('BCDEHKLMNPQRSTUWXYZ')}{rnd.randint(1000, 9999)}{rnd.choice('ABCDEFGHIJ')}"
    if "dispositivo" in t or "programa" in t or "residencia" in t or "hogar" in t:
        return rnd.choice(DISPOSITIVOS)
    if "localidad" in t or "partido" in t or "municipio" in t:
        return rnd.choice(LOCALIDADES.get(jurisdiccion or "", LOCALIDAD_POR_DEFECTO))
    if "observacion" in t or "observación" in t or "detalle" in t or "especificar" in t:
        return rnd.choice(["", "", f"Nota de ejemplo {i}"])
    if "equipo" in t or "responsable" in t:
        return f"{rnd.choice(NOMBRES)} {rnd.choice(APELLIDOS)}"
    return f"Dato {i}"


# Cada error se genera a propósito, para verificar que el importador lo detecte.
# La fila vacía va en el medio: si quedara última no sería "intercalada" y el
# importador no tendría por qué detectarla.
ERRORES = [
    ("fecha_invalida", "una fecha que no existe", "FECHA", "31/02/2026"),
    ("texto_en_numero", "letras donde va un número", "ENTERO", "doce"),
    (
        "valor_fuera_de_catalogo",
        "un valor que no está en la lista",
        None,
        "VALOR INVENTADO",
    ),
    ("fila_vacia_intercalada", "una fila vacía en el medio de los datos", None, None),
    ("obligatorio_vacio", "un campo obligatorio sin completar", None, None),
    ("texto_muy_largo", "un texto más largo de lo admitido", "TEXTO", "X" * 400),
    ("documento_repetido", "el mismo documento dos veces", None, None),
]


def leer_definicion(cur, codigo: str):
    cur.execute(
        """SELECT a.id, a.codigo, av.id AS version_id, av.nombre_esperado
                   FROM runac_c1_archivo a
                   JOIN runac_c1_archivo_version av ON av.archivo_id = a.id AND av.estado='VIGENTE'
                   WHERE a.codigo=%s""",
        (codigo,),
    )
    archivo = cur.fetchone()
    if not archivo:
        raise SystemExit(f"No existe {codigo} con una versión vigente en la Capa 1.")
    cur.execute(
        """SELECT id, nombre_esperado, fila_encabezados, orden_procesamiento
                   FROM runac_c1_hoja WHERE archivo_version_id=%s ORDER BY orden_procesamiento""",
        (archivo["version_id"],),
    )
    hojas = cur.fetchall()
    for h in hojas:
        cur.execute(
            """
            SELECT c.id, c.nombre, c.titulo_esperado, c.orden, c.tipo_dato,
                   c.longitud_maxima, c.obligatorio, cat.codigo AS catalogo
            FROM runac_c1_campo c LEFT JOIN runac_c1_catalogo cat ON cat.id=c.catalogo_id
            WHERE c.hoja_id=%s ORDER BY c.orden""",
            (h["id"],),
        )
        h["campos"] = cur.fetchall()
        for campo in h["campos"]:
            campo["opciones"] = []
            if campo["catalogo"]:
                cur.execute(
                    """SELECT o.valor_esperado FROM runac_c1_catalogo_opcion o
                               JOIN runac_c1_catalogo c ON c.id=o.catalogo_id
                               WHERE c.codigo=%s AND o.activo=1 ORDER BY o.orden""",
                    (campo["catalogo"],),
                )
                campo["opciones"] = [r["valor_esperado"] for r in cur.fetchall()]
    archivo["hojas"] = hojas
    return archivo


def main():
    p = argparse.ArgumentParser(
        description="Genera datos de prueba sobre las plantillas de la Capa 1."
    )
    p.add_argument("--archivo", default=None)
    p.add_argument("--todos", action="store_true")
    p.add_argument("--filas", type=int, default=30)
    p.add_argument("--con-errores", action="store_true")
    p.add_argument("--plantillas", default="/trabajo/capa1/plantillas")
    p.add_argument("--salida", default="/trabajo/capa1/mock")
    p.add_argument("--periodo", default="2026_T1")
    p.add_argument(
        "--jurisdiccion",
        default="Chubut",
        help="provincia que presenta: sus archivos llevan sus localidades",
    )
    p.add_argument(
        "--semilla",
        type=int,
        default=42,
        help="para que los datos sean siempre los mismos",
    )
    args = p.parse_args()

    cn = mysql.connector.connect(**CONEXION)
    cur = cn.cursor(dictionary=True)

    if args.todos:
        cur.execute(
            """SELECT a.codigo FROM runac_c1_archivo a
                       JOIN runac_c1_archivo_version av ON av.archivo_id = a.id AND av.estado='VIGENTE'
                       ORDER BY av.orden_importacion"""
        )
        codigos = [r["codigo"] for r in cur.fetchall()]
    elif args.archivo:
        codigos = [args.archivo]
    else:
        raise SystemExit("Indicar --archivo CODIGO o --todos.")

    os.makedirs(args.salida, exist_ok=True)

    for codigo in codigos:
        archivo = leer_definicion(cur, codigo)
        origen = os.path.join(args.plantillas, f"{codigo}_{args.periodo}_MODELO.xlsx")
        if not os.path.exists(origen):
            print(f"  {codigo}: falta la plantilla, se omite")
            continue

        wb = load_workbook(origen)
        rnd = random.Random(args.semilla)
        resumen = []

        for hoja in archivo["hojas"]:
            nombre = hoja["nombre_esperado"][:31]
            if nombre not in wb.sheetnames:
                continue
            ws = wb[nombre]
            campos = hoja["campos"]
            if not campos:
                continue

            # La plantilla ya trae el encabezado; los datos empiezan debajo.
            # Se busca la fila cuyo primer valor coincida con el título del primer
            # campo, ignorando el asterisco de obligatorio y los acentos.
            def comparable(v):
                import unicodedata as _u

                t = re.sub(r"\s+", " ", str(v or "").strip()).rstrip(" *").lower()
                return "".join(
                    c for c in _u.normalize("NFD", t) if _u.category(c) != "Mn"
                )

            esperado = comparable(campos[0]["titulo_esperado"])
            fila_enc = None
            for f in range(1, 12):
                if comparable(ws.cell(row=f, column=1).value) == esperado:
                    fila_enc = f
                    break
            if fila_enc is None:
                print(
                    f"  {codigo}/{nombre}: no se ubicó la fila de encabezados, se omite la hoja"
                )
                continue
            fila = fila_enc + 1

            for i in range(1, args.filas + 1):
                generados: dict = {}
                for k, campo in enumerate(campos, start=1):
                    v = valor_inventado(
                        campo, campo["opciones"], i, rnd, generados, args.jurisdiccion
                    )
                    generados[campo["nombre"]] = v
                    ws.cell(row=fila, column=k, value=v)
                fila += 1
            resumen.append((nombre, args.filas, 0))

            if args.con_errores:
                errores_puestos = []
                # Una fila por cada tipo de error, para poder verificar uno por uno.
                for clave, descripcion, tipo_objetivo, valor in ERRORES:
                    destino = next(
                        (
                            c
                            for c in campos
                            if (
                                tipo_objetivo is None or c["tipo_dato"] == tipo_objetivo
                            )
                            and (clave != "valor_fuera_de_catalogo" or c["catalogo"])
                            and (clave != "obligatorio_vacio" or c["obligatorio"])
                            and (
                                clave != "texto_muy_largo"
                                or (c["longitud_maxima"] or 0) > 0
                            )
                        ),
                        None,
                    )
                    if clave == "fila_vacia_intercalada":
                        fila += 1  # se salta una fila y se sigue: queda una vacía en el medio
                        errores_puestos.append((clave, descripcion, "—", fila - 1))
                        continue
                    if not destino and clave != "documento_repetido":
                        continue
                    generados = {}
                    for k, campo in enumerate(campos, start=1):
                        v = valor_inventado(
                            campo,
                            campo["opciones"],
                            999,
                            rnd,
                            generados,
                            args.jurisdiccion,
                        )
                        generados[campo["nombre"]] = v
                        ws.cell(row=fila, column=k, value=v)
                    if clave == "documento_repetido":
                        doc = next(
                            (
                                c
                                for c in campos
                                if "dni" in (c["titulo_esperado"] or "").lower()
                            ),
                            None,
                        )
                        if not doc:
                            continue
                        # Se copia el documento que quedó en la primera fila de datos,
                        # así el duplicado es real y no depende de reproducir el azar.
                        ws.cell(row=fila, column=doc["orden"]).value = ws.cell(
                            row=fila_enc + 1, column=doc["orden"]
                        ).value
                        errores_puestos.append(
                            (clave, descripcion, doc["titulo_esperado"], fila)
                        )
                    else:
                        # Asignar por .value, no por cell(value=...): con None, la
                        # segunda forma no vacía la celda.
                        ws.cell(row=fila, column=destino["orden"]).value = valor
                        errores_puestos.append(
                            (clave, descripcion, destino["titulo_esperado"], fila)
                        )
                    fila += 1
                resumen[-1] = (nombre, args.filas, len(errores_puestos))

                # Una hoja aparte deja constancia de qué se rompió a propósito.
                if "ERRORES_ESPERADOS" in wb.sheetnames:
                    del wb["ERRORES_ESPERADOS"]
                we = wb.create_sheet("ERRORES_ESPERADOS")
                we.append(
                    [
                        "Hoja",
                        "Fila",
                        "Campo",
                        "Error introducido",
                        "Qué debería detectar el sistema",
                    ]
                )
                for clave, descripcion, campo_nom, f in errores_puestos:
                    we.append([nombre, f, campo_nom, clave, descripcion])
                for col, ancho in zip("ABCDE", (18, 8, 34, 28, 46)):
                    we.column_dimensions[col].width = ancho

        # Formato de nombre propuesto en el análisis funcional:
        #   MPI_2026_T1_NombreProvincia.xlsx
        prov = re.sub(r"[^A-Za-z0-9]", "", clave_simple(args.jurisdiccion).title())
        sufijo = "_CON_ERRORES" if args.con_errores else ""
        destino_archivo = os.path.join(
            args.salida, f"{codigo}_{args.periodo}_{prov}{sufijo}.xlsx"
        )
        wb.save(destino_archivo)
        detalle = ", ".join(
            f"{n}: {f} filas" + (f" + {e} con errores" if e else "")
            for n, f, e in resumen
        )
        print(f"  {codigo:12} {os.path.basename(destino_archivo):42} {detalle}")

    cur.close()
    cn.close()


if __name__ == "__main__":
    main()
