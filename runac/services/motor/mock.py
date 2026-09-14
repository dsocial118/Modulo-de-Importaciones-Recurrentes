"""Genera un Excel de prueba con datos inventados, leyendo la Capa 1.

    python mock.py --archivo MPI --filas 50
    python mock.py --todos --filas 30 --con-errores
    python mock.py --todos --filas 30 --con-advertencias

Sirve para probar el importador sin datos reales. Hay tres juegos de archivos y
cada uno prueba una cosa distinta:

  - **limpio**: no tiene que producir ni un hallazgo. Es el que dice que el
    importador no inventa problemas donde no los hay.
  - **--con-advertencias**: sólo advertencias. Es el que sirve para mostrar la
    corrección dentro del sistema, que es lo que se hace con una advertencia.
  - **--con-errores**: errores bloqueantes, uno de cada tipo, para verificar
    que el importador los agarre y que el archivo no entre.

Para que el archivo limpio salga limpio, el generador **lee las reglas de la
Capa 1 y las respeta**: si la situación de documentación dice que no hay número
de DNI, no escribe uno. Es el mismo principio que el resto del módulo —la
lógica está en los datos—, y si no fuera así habría que acordarse de actualizar
el generador cada vez que se agrega una regla.

Los datos son inventados. Los nombres salen de una lista corta y los documentos
de un rango que no corresponde a personas reales.
"""

from __future__ import annotations

import argparse
import json
import re
import os
import random
from datetime import date, timedelta

import mysql.connector
from openpyxl import load_workbook

# El generador aplica las MISMAS condiciones que el importador: si usara una
# copia propia, un archivo "limpio" podría no serlo.
from importar import condicion_se_cumple

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


def es_de_dispositivo(titulo: str) -> bool:
    """¿El campo nombra un lugar donde se aloja a alguien, y no a una persona?

    «disposit» y no «dispositivo» porque las planillas traen «dispositvo», sin
    la i, y ese es justamente el campo que la nómina penal referencia.

    «residencia» y «hogar» están acá y no más abajo por un motivo: el MPE llama
    a ese campo «Nombre de la residencia/hogar», y la rama que reparte nombres
    de pila se queda con cualquier título que diga «nombre». Así, la nómina de
    protección quedaba nombrando residencias que se llamaban Ana o Thiago, y la
    regla que verifica que la residencia exista fallaba en las treinta filas.
    """
    return any(p in titulo for p in ("disposit", "programa", "residencia", "hogar"))


def fuera_de_rango(par: dict, candidato):
    """Un valor que la regla de rango tiene que rechazar.

    Se pasa por arriba del máximo, que es lo que se ve mal a simple vista —500
    horas semanales, 8888 agentes—. Si la regla sólo declara un mínimo, se va
    por abajo, que para una cantidad significa un negativo.
    """
    maximo, minimo = par.get("maximo"), par.get("minimo")
    if maximo is not None:
        return int(maximo) + 1
    if minimo is not None:
        return int(minimo) - 1
    return candidato


def valor_condicionado(
    campo: dict, fila: dict, candidato, rnd: random.Random, sembrar_aviso: bool = False
):
    """Ajusta el valor para que respete las reglas condicionales de la Capa 1.

    Devuelve (valor, motivo_del_aviso). Sin esto, el archivo «limpio» salía con
    incumplimientos: se sorteaba «no posee N° DNI» y a continuación se escribía
    un número de DNI, o se declaraba un pueblo originario y se dejaba en blanco
    cuál. Son contradicciones que el importador detecta —y hace bien—, pero que
    no tienen que estar en el archivo que se usa para probar que todo anda.

    Con `sembrar_aviso`, las de severidad ADVERTENCIA se dejan incumplidas a
    propósito: es lo que hace falta para mostrar la corrección dentro del
    sistema, que es lo que se hace con una advertencia y no con un bloqueante.
    """
    for regla in campo.get("reglas") or []:
        par = regla.get("parametros") or {}
        tipo, severidad = regla["tipo_regla"], regla["severidad"]
        es_aviso = severidad == "ADVERTENCIA"

        # Las reglas que se aplican SIEMPRE, sin condición previa. Sin ellas,
        # los dos archivos de dispositivos salían sin una sola advertencia: no
        # tienen campos dependientes, así que lo único que se sembraba —las
        # condicionales— no los tocaba.
        if sembrar_aviso and es_aviso:
            if tipo == "EXISTE_EN_ARCHIVO":
                return "Dispositivo no declarado", regla["nombre"]
            if tipo == "RANGO":
                return fuera_de_rango(par, candidato), regla["nombre"]
            if tipo == "COMPARAR_VALOR" and par.get("valor") == "HOY":
                # La regla pide que la fecha no sea futura: se la pone futura.
                return (
                    date.today() + timedelta(days=rnd.randint(30, 400)),
                    regla["nombre"],
                )

        if tipo not in ("PROHIBIDO_SI", "OBLIGATORIO_SI"):
            continue
        if not condicion_se_cumple(par, fila):
            continue
        vacio = candidato is None or str(candidato).strip() == ""
        if sembrar_aviso and es_aviso:
            # Se incumple a propósito, y de forma segura: la regla que exige el
            # dato lo deja vacío y la que lo prohíbe se asegura de que haya uno.
            if tipo == "OBLIGATORIO_SI":
                return None, regla["nombre"]
            return (candidato if not vacio else f"Dato {rnd.randint(1, 99)}"), regla[
                "nombre"
            ]
        if tipo == "PROHIBIDO_SI":
            return None, None
        if vacio:
            return f"Dato requerido {rnd.randint(1, 99)}", None
    return candidato, None


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
    # «Nombre del dispositvo» viene así, sin la i, en las planillas de
    # dispositivos penales. Con «dispositivo» escrito completo, ese campo caía
    # en la rama de las personas y se llenaba con un nombre de pila: la nómina
    # nombraba dispositivos que no existían en el archivo de dispositivos.
    if "nombre" in t and not es_de_dispositivo(t):
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
    if es_de_dispositivo(t):
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
            # Las reglas se leen para respetarlas al generar: el archivo limpio
            # tiene que salir limpio sin que nadie mantenga una lista aparte.
            cur.execute(
                """SELECT r.id, r.nombre, r.parametros, tr.nombre AS tipo_regla,
                          cr.severidad
                     FROM runac_c1_campo_regla cr
                     JOIN runac_c1_regla r ON r.id = cr.regla_id
                     JOIN runac_c1_tipo_regla tr ON tr.id = r.tipo_regla_id
                    WHERE cr.campo_id = %s""",
                (campo["id"],),
            )
            campo["reglas"] = []
            for r in cur.fetchall():
                crudo = r["parametros"]
                if isinstance(crudo, (bytes, bytearray)):
                    crudo = crudo.decode("utf-8")
                r["parametros"] = (
                    crudo if isinstance(crudo, dict) else json.loads(crudo or "{}")
                )
                campo["reglas"].append(r)
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
    p.add_argument(
        "--con-advertencias",
        action="store_true",
        help="deja incumplidas a proposito las reglas de severidad ADVERTENCIA",
    )
    p.add_argument("--plantillas", default="/trabajo/capa1/plantillas")
    p.add_argument("--salida", default="/trabajo/entregables/06_Archivos_de_prueba")
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

            avisos_puestos = []
            for i in range(1, args.filas + 1):
                # Una de cada tres filas lleva advertencias: así el archivo
                # tiene también filas correctas y se ve la diferencia.
                sembrar = bool(args.con_advertencias) and i % 3 == 0
                generados: dict = {}
                for k, campo in enumerate(campos, start=1):
                    v = valor_inventado(
                        campo, campo["opciones"], i, rnd, generados, args.jurisdiccion
                    )
                    v, aviso = valor_condicionado(campo, generados, v, rnd, sembrar)
                    if aviso:
                        avisos_puestos.append(
                            (nombre, fila, campo["titulo_esperado"], aviso)
                        )
                    generados[campo["nombre"]] = v
                    ws.cell(row=fila, column=k, value=v)
                fila += 1
            resumen.append((nombre, args.filas, len(avisos_puestos)))

            if avisos_puestos:
                # Una hoja aparte deja constancia de qué se dejó incumplido.
                if "ADVERTENCIAS_ESPERADAS" not in wb.sheetnames:
                    wa = wb.create_sheet("ADVERTENCIAS_ESPERADAS")
                    wa.append(["Hoja", "Fila", "Campo", "Regla que se incumple"])
                    for col, ancho in zip("ABCD", (18, 8, 40, 46)):
                        wa.column_dimensions[col].width = ancho
                for aviso in avisos_puestos:
                    wb["ADVERTENCIAS_ESPERADAS"].append(list(aviso))

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
        sufijo = ""
        if args.con_errores:
            sufijo = "_CON_ERRORES"
        elif args.con_advertencias:
            sufijo = "_CON_ADVERTENCIAS"
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
