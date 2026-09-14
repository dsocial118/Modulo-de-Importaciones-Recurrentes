"""Deja el prototipo con una presentación completa, lista para mostrar.

    docker exec runac_proto_web python manage.py armar_demo

Importa los cinco archivos de Chubut en orden, deja el MPI con advertencias
—sin eso la pantalla de corrección queda vacía, que es justo lo que hay que
mostrar— y corrige tres de ellas para que el historial tenga contenido.

**Por qué existe.** La demo se rehacía a mano cada vez que se vaciaba la base, y
se vació varias veces: probando el circuito, usando el botón de borrar, o por
algo que no se pudo determinar. Rehacerla de memoria, minutos antes de una
reunión, es la peor forma de descubrir que falta un paso.

Es una herramienta de prueba y se va con el prototipo, igual que el botón de
borrar importaciones.
"""

from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand
from django.db import connection

from runac.services import circuito_service as circuito
from runac.services import edicion_service as edicion
from runac.services import importacion_service as svc

ARCHIVOS = Path(__file__).resolve().parents[2] / "demo"
JURISDICCION = "Chubut"
PERIODO = "2026_T1"

# El MPI va con la variante que trae advertencias, a propósito: un archivo
# perfecto no permite mostrar la corrección dentro del sistema, que es la mitad
# interesante del circuito.
PLAN = [
    ("DISP_PENAL", "DISP_PENAL_2026_T1_Chubut.xlsx"),
    ("DISP_SCP", "DISP_SCP_2026_T1_Chubut.xlsx"),
    ("MPI", "MPI_2026_T1_Chubut_CON_ADVERTENCIAS.xlsx"),
    ("MPE", "MPE_2026_T1_Chubut.xlsx"),
    ("MPJ_DAE", "MPJ_DAE_2026_T1_Chubut.xlsx"),
]

# Dos formas distintas de resolver la misma advertencia: completar el dato que
# faltaba, y corregir el campo que lo exigía. El historial muestra las dos.
CORRECCIONES = [
    ("Pueblo originario (especificar)", "Qom", "Lo informó la provincia por nota"),
    ("Pueblo originario (especificar)", "Mapuche", "Se verificó contra el expediente"),
    (
        "¿Se identifica con algún pueblo originario?",
        "No",
        "Estaba mal cargado: no se identifica con ningún pueblo",
    ),
]


class Command(BaseCommand):
    help = "Arma la presentación de demostración de Chubut, desde cero."

    def add_arguments(self, parser):
        parser.add_argument(
            "--conservar",
            action="store_true",
            help="no borra lo que haya: sólo importa lo que falte",
        )

    def handle(self, *args, **opciones):
        if not opciones["conservar"]:
            borrados = circuito.borrar_todas_las_importaciones()
            self.stdout.write(
                f'Se borró lo anterior: {borrados["importaciones"]} importaciones, '
                f'{borrados["filas"]} registros.'
            )

        for codigo, nombre in PLAN:
            ruta = ARCHIVOS / nombre
            if not ruta.exists():
                raise FileNotFoundError(f"Falta el archivo de demostración: {ruta}")
            with open(ruta, "rb") as fh:
                subido = SimpleUploadedFile(nombre, fh.read())
            resultado = svc.importar_uno(
                codigo, subido, JURISDICCION, PERIODO, "operador"
            )
            if resultado.get("rechazado"):
                self.stderr.write(f'{codigo}: {resultado["mensaje"]}')
                continue
            self.stdout.write(f"{codigo}: importado")

        self._corregir()
        self._resumir()

    def _corregir(self):
        """Deja hechas unas correcciones, para que el historial no esté vacío."""
        with connection.cursor() as cur:
            cur.execute(
                """SELECT i.id FROM runac_c2_importacion i
                     JOIN runac_c1_archivo a ON a.id = i.archivo_id
                    WHERE a.codigo = 'MPI' AND i.estado = 'VALIDA'
                    ORDER BY i.id DESC LIMIT 1"""
            )
            fila = cur.fetchone()
        if not fila:
            self.stderr.write("El MPI no entró: no se corrige nada.")
            return

        importacion = fila[0]
        contexto = edicion.contexto_de(importacion)
        hoja = contexto["hojas"][0]
        campos = {
            c["titulo_esperado"]: c for c in edicion.campos_de_la_hoja(hoja["id"])
        }

        # Las filas se eligen de las que efectivamente tienen la advertencia, y
        # distintas entre sí: dos correcciones sobre la misma fila se leen como
        # una corrección de una corrección, que no es lo que se quiere mostrar.
        with connection.cursor() as cur:
            cur.execute(
                """SELECT DISTINCT numero_fila FROM runac_c2_reglas_incumplidas
                    WHERE importacion_id = %s AND resuelta = 0
                      AND nombre_campo = %s
                    ORDER BY numero_fila""",
                [importacion, "Pueblo originario (especificar)"],
            )
            filas = [f[0] for f in cur.fetchall()]

        for numero, (titulo, valor, motivo) in zip(filas, CORRECCIONES):
            campo = campos.get(titulo)
            if not campo:
                continue
            edicion.editar(
                importacion,
                hoja["id"],
                numero,
                campo["nombre"],
                valor,
                "operador",
                motivo,
            )
        self.stdout.write(f"{len(filas[: len(CORRECCIONES)])} correcciones registradas")

    def _resumir(self):
        estado = svc.estado_de_la_presentacion(JURISDICCION, PERIODO)
        self.stdout.write("")
        for archivo in estado["archivos"]:
            imp = archivo.get("importacion") or {}
            self.stdout.write(
                f'  {archivo["codigo"]:12} {archivo["estado"]:10} '
                f'filas={imp.get("filas_incorporadas") or "—":>4} '
                f'advertencias={imp.get("advertencias") or 0}'
            )
        listo = "sí" if estado["listo"] else "NO"
        self.stdout.write(f"\nPresentación completa: {listo}")
