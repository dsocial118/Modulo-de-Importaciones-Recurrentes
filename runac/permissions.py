"""Roles del prototipo.

**Esto es provisorio.** SISOC resuelve permisos con `iam/services.py` y alcance
territorial con sus propios mecanismos. Acá se usa lo mínimo para poder mostrar
que cada rol ve pantallas distintas.

Al integrar el módulo, este archivo se descarta entero.

El rol y la jurisdicción son dos cosas distintas: el rol define qué puede hacer,
la jurisdicción sobre qué datos.
"""

from django.contrib.auth.models import Group

ROLES = {
    "operador_provincial": "Operador provincial",
    "responsable_provincial": "Responsable provincial",
    "revisor_nacional": "Revisor técnico nacional",
    "administrador_nacional": "Administrador nacional",
}

ES_NACIONAL = ("revisor_nacional", "administrador_nacional")


def rol_de(usuario) -> str | None:
    """El rol sale del grupo de Django. Un usuario tiene uno solo."""
    if not usuario.is_authenticated:
        return None
    for g in usuario.groups.values_list("name", flat=True):
        if g in ROLES:
            return g
    return "administrador_nacional" if usuario.is_superuser else None


def nombre_del_rol(usuario) -> str:
    return ROLES.get(rol_de(usuario), "sin rol asignado")


def jurisdiccion_de(usuario) -> str | None:
    """La jurisdicción se guarda en el nombre del grupo, con prefijo.

    Provisorio: alcanza para el prototipo. En SISOC esto sale del alcance
    territorial del usuario.
    """
    if not usuario.is_authenticated:
        return None
    for g in usuario.groups.values_list("name", flat=True):
        if g.startswith("jurisdiccion:"):
            return g.split(":", 1)[1]
    # Los roles nacionales ven todas; para el prototipo se les asigna una por defecto.
    return None if rol_de(usuario) in ES_NACIONAL else None


def es_nacional(usuario) -> bool:
    return rol_de(usuario) in ES_NACIONAL


def puede_cargar(usuario) -> bool:
    return rol_de(usuario) == "operador_provincial" or usuario.is_superuser


def puede_presentar(usuario) -> bool:
    return rol_de(usuario) == "responsable_provincial" or usuario.is_superuser


def puede_revisar(usuario) -> bool:
    return rol_de(usuario) == "revisor_nacional" or usuario.is_superuser


def puede_administrar(usuario) -> bool:
    return rol_de(usuario) == "administrador_nacional" or usuario.is_superuser


def asegurar_grupos():
    """Crea los grupos de rol. Se llama desde el comando de datos iniciales."""
    for codigo in ROLES:
        Group.objects.get_or_create(name=codigo)
