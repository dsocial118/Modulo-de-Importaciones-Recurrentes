"""Crea los usuarios de prueba del prototipo.

    python manage.py datos_iniciales

Los usuarios son de prueba y la contraseña es la misma para todos. Al integrar
el módulo a SISOC esto se descarta: los usuarios los maneja el sistema.
"""

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand

from runac.permissions import ROLES, asegurar_grupos

CLAVE = "runac"

USUARIOS = [
    ("operador", "operador_provincial", "Chaco"),
    ("responsable", "responsable_provincial", "Chaco"),
    ("revisor", "revisor_nacional", None),
    ("admin", "administrador_nacional", None),
]


class Command(BaseCommand):
    help = "Crea los usuarios de prueba del prototipo."

    def handle(self, *args, **opciones):
        asegurar_grupos()
        for nombre, rol, jurisdiccion in USUARIOS:
            usuario, creado = User.objects.get_or_create(
                username=nombre, defaults={"first_name": ROLES[rol]}
            )
            usuario.set_password(CLAVE)
            usuario.is_staff = rol == "administrador_nacional"
            usuario.is_superuser = rol == "administrador_nacional"
            usuario.save()

            usuario.groups.clear()
            usuario.groups.add(Group.objects.get(name=rol))
            if jurisdiccion:
                grupo, _ = Group.objects.get_or_create(
                    name=f"jurisdiccion:{jurisdiccion}"
                )
                usuario.groups.add(grupo)

            estado = "creado" if creado else "actualizado"
            donde = f" · {jurisdiccion}" if jurisdiccion else ""
            self.stdout.write(f"  {nombre:14} {ROLES[rol]}{donde}  ({estado})")

        self.stdout.write(
            self.style.SUCCESS(f"\nListo. La contraseña de todos es: {CLAVE}")
        )
