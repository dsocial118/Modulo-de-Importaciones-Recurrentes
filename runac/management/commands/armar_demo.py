"""Deja el sistema con una presentación completa, lista para mostrar.

    docker exec runac_proto_web python manage.py armar_demo

Lo mismo que hace el botón «Armar demostración» del inicio. La lógica vive en
`services/demo_service.py` porque la usan los dos.

Es una herramienta de prueba y se va al integrar a SISOC, igual que el botón de
borrar importaciones.
"""

from django.core.management.base import BaseCommand

from runac.services import demo_service


class Command(BaseCommand):
    help = "Arma la presentación de demostración de Chubut, desde cero."

    def add_arguments(self, parser):
        parser.add_argument(
            "--conservar",
            action="store_true",
            help="no borra lo que haya: sólo importa lo que falte",
        )

    def handle(self, *args, **opciones):
        resumen = demo_service.armar(borrar_antes=not opciones["conservar"])

        if resumen["borrado"]:
            borrado = resumen["borrado"]
            self.stdout.write(
                f'Se borró lo anterior: {borrado["importaciones"]} importaciones, '
                f'{borrado["filas"]} registros.'
            )
        for codigo in resumen["importados"]:
            self.stdout.write(f"{codigo}: importado")
        for codigo, motivo in resumen["rechazados"]:
            self.stderr.write(f"{codigo}: {motivo}")
        self.stdout.write(f'{resumen["correcciones"]} correcciones registradas\n')

        for archivo in resumen["estado"]["archivos"]:
            imp = archivo.get("importacion") or {}
            self.stdout.write(
                f'  {archivo["codigo"]:12} {archivo["estado"]:10} '
                f'filas={imp.get("filas_incorporadas") or "—":>4} '
                f'advertencias={imp.get("advertencias") or 0}'
            )
        listo = "sí" if resumen["estado"]["listo"] else "NO"
        self.stdout.write(f"\nPresentación completa: {listo}")
