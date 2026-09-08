"""Roles del prototipo: qué puede hacer cada uno y qué ve.

**Esto es provisorio.** SISOC resuelve permisos con `iam/services.py` y alcance
territorial con sus propios mecanismos. Acá se usa lo mínimo para que cada rol
vea y pueda lo que le corresponde. Al integrar el módulo, este archivo se
descarta entero.

El rol y la jurisdicción son dos cosas distintas: el rol define qué puede hacer,
la jurisdicción sobre qué datos.

Dos conceptos que no hay que confundir:

  - **Menú**: qué secciones se le ofrecen a cada rol.
  - **Acceso**: a qué secciones puede entrar, aunque no estén en su menú. El
    revisor nacional, por ejemplo, no tiene "Resultado" en el menú pero entra
    desde la bandeja de revisión.

Ocultar un enlace no es un permiso: el acceso se verifica en la vista, con
`SeccionPermitidaMixin`.
"""

from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied

ROLES = {
    "operador_provincial": "Operador provincial",
    "responsable_provincial": "Responsable provincial",
    "revisor_nacional": "Revisor técnico nacional",
    "administrador_nacional": "Administrador nacional",
}

ES_NACIONAL = ("revisor_nacional", "administrador_nacional")
ES_PROVINCIAL = ("operador_provincial", "responsable_provincial")
TODOS = tuple(ROLES)

# Cada sección: etiqueta, ruta, quién la ve en el menú y quién puede entrar.
# El orden es el del circuito, para que el menú se lea como el recorrido.
SECCIONES = {
    "inicio": {
        "etiqueta": "Inicio",
        "url": "runac:inicio",
        "icono": "bi-house",
        "menu": TODOS,
        "acceso": TODOS,
    },
    "plantillas": {
        "etiqueta": "Plantillas",
        "url": "runac:plantillas",
        "icono": "bi-download",
        "menu": ES_PROVINCIAL + ("administrador_nacional",),
        "acceso": TODOS,
    },
    "cargar": {
        "etiqueta": "Cargar archivos",
        "url": "runac:cargar",
        "icono": "bi-upload",
        "menu": ES_PROVINCIAL,
        "acceso": ES_PROVINCIAL + ("administrador_nacional",),
    },
    "resultado": {
        "etiqueta": "Resultado",
        "url": "runac:resultado",
        "icono": "bi-clipboard-check",
        "menu": ES_PROVINCIAL,
        # El revisor entra desde la bandeja, aunque no lo tenga en el menú.
        "acceso": TODOS,
    },
    "revision": {
        "etiqueta": "Revisión nacional",
        "url": "runac:revision",
        "icono": "bi-search",
        "menu": ES_NACIONAL,
        "acceso": ES_NACIONAL,
    },
    "estructura": {
        "etiqueta": "Estructura",
        "url": "runac:estructura",
        "icono": "bi-diagram-3",
        "menu": TODOS,
        "acceso": TODOS,
    },
}


def rol_de(usuario) -> str | None:
    """El rol sale del grupo de Django. Un usuario tiene uno solo."""
    if not usuario or not usuario.is_authenticated:
        return None
    for grupo in usuario.groups.values_list("name", flat=True):
        if grupo in ROLES:
            return grupo
    return "administrador_nacional" if usuario.is_superuser else None


def nombre_del_rol(usuario) -> str:
    return ROLES.get(rol_de(usuario), "sin rol asignado")


def jurisdiccion_de(usuario) -> str | None:
    """La jurisdicción se guarda en el nombre del grupo, con prefijo.

    Provisorio: alcanza para el prototipo. En SISOC esto sale del alcance
    territorial del usuario.
    """
    if not usuario or not usuario.is_authenticated:
        return None
    for grupo in usuario.groups.values_list("name", flat=True):
        if grupo.startswith("jurisdiccion:"):
            return grupo.split(":", 1)[1]
    return None


def es_nacional(usuario) -> bool:
    return rol_de(usuario) in ES_NACIONAL


def es_provincial(usuario) -> bool:
    return rol_de(usuario) in ES_PROVINCIAL


def menu_de(usuario) -> list[dict]:
    """Las secciones que este usuario ve en la barra de navegación."""
    rol = rol_de(usuario)
    if not rol:
        return []
    return [
        {"clave": clave, **datos}
        for clave, datos in SECCIONES.items()
        if rol in datos["menu"]
    ]


def puede_entrar(usuario, seccion: str) -> bool:
    """Si este usuario puede acceder a la sección, esté o no en su menú."""
    rol = rol_de(usuario)
    if not rol:
        return False
    datos = SECCIONES.get(seccion)
    return bool(datos) and rol in datos["acceso"]


class SeccionPermitidaMixin:
    """Verifica el acceso en la vista, no sólo en el menú.

    Ocultar un enlace no impide entrar escribiendo la dirección. Las vistas
    declaran a qué sección pertenecen y este mixin corta el paso.
    """

    seccion: str = ""

    def dispatch(self, request, *args, **kwargs):
        # Sin sesión no es un problema de permisos: es que falta entrar. Se deja
        # pasar para que LoginRequiredMixin redirija al inicio de sesión.
        autenticado = bool(request.user and request.user.is_authenticated)
        if (
            autenticado
            and self.seccion
            and not puede_entrar(request.user, self.seccion)
        ):
            raise PermissionDenied("Tu rol no tiene acceso a esta sección del sistema.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Marca la sección activa, para que el menú se resalte solo."""
        contexto = super().get_context_data(**kwargs)
        contexto.setdefault("seccion_actual", self.seccion)
        return contexto


# --- Acciones concretas -----------------------------------------------------


def puede_cargar(usuario) -> bool:
    """Importar archivos: es tarea del operador provincial."""
    return rol_de(usuario) == "operador_provincial" or bool(usuario.is_superuser)


def puede_presentar(usuario) -> bool:
    """Cerrar la carga y presentar: responde institucionalmente por los datos."""
    return rol_de(usuario) == "responsable_provincial" or bool(usuario.is_superuser)


def puede_editar_datos(usuario) -> bool:
    """Corregir un dato ya importado.

    El documento funcional lo asigna al operador provincial, y el responsable
    puede hacer todo lo del operador. El nivel nacional NO edita datos
    provinciales: observa.
    """
    return rol_de(usuario) in ES_PROVINCIAL or bool(usuario.is_superuser)


def puede_revisar(usuario) -> bool:
    """Observar y habilitar la presentación."""
    return rol_de(usuario) == "revisor_nacional" or bool(usuario.is_superuser)


def puede_administrar(usuario) -> bool:
    return rol_de(usuario) == "administrador_nacional" or bool(usuario.is_superuser)


def asegurar_grupos():
    """Crea los grupos de rol. Se llama desde el comando de datos iniciales."""
    for codigo in ROLES:
        Group.objects.get_or_create(name=codigo)
