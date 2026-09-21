"""Qué espera cada archivo: la pantalla de reglas.

Es de sólo lectura: la estructura la produce la skill `runac-capa1`. Acá se
muestra para que quien carga no tenga que adivinar qué va en cada columna.

Se arma para consultarla, no para auditar el modelo. De ahí las decisiones:

  - **Se elige archivo y hoja**, y se ve esa hoja sola. Un archivo con seis
    hojas volcadas una debajo de la otra no se consulta.
  - **Sin contadores.** Cuántas listas tiene un archivo no le sirve a nadie que
    esté por completarlo.
  - **Sin nombre técnico**, salvo para el administrador.
  - **El tipo de dato en castellano**: «Fecha», «Texto, hasta 120 caracteres»,
    y no `TEXTO(120)`.
"""

import json
from urllib.parse import quote

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView

from runac.permissions import SeccionPermitidaMixin, puede_administrar
from runac.services import importacion_service as svc
from runac.services import reglas_service

# Listas demasiado largas para enumerar: se nombra el conjunto. Son doce sobre
# ochenta y una, así que se escriben a mano; pluralizar en castellano por
# programa sale mal enseguida («máximo nivel educativo alcanzado» no tiene
# plural razonable).
NOMBRE_DE_LISTA_LARGA = {
    "pais_de_nacimiento": "Países válidos",
    "provincia": "Provincias válidas",
    "provincias": "Provincias válidas",
    "motivos_de_intervencion_aplican_tanto_para_mpe_y_mpi_acordadas_en_2019"
    "_con_las_24_jurisdicciones": "Motivos de intervención acordados en 2019",
    "causas_de_las_medidas_mpi": "Causas de la medida",
    "procedencia_inmediata": "Procedencias válidas",
    "maximo_nivel_educativo_alcanzado_2": "Niveles educativos",
    "maximo_nivel_educativo_alcanzado_3": "Niveles educativos",
    "tiempo_en_comisaria": "Tramos de tiempo",
    "destino_al_egreso": "Destinos válidos",
    "destinadas_al_cuidado_del_nya": "Tramos de cantidad de personal",
    "destinadas_a_tareas_de_apoyo_administrativo_mantenimiento_cocina_etc": "Tramos de cantidad de personal",
}

# A partir de acá se nombra la lista en vez de enumerarla.
TOPE_PARA_ENUMERAR = 8

TIPO_EN_CASTELLANO = {
    "FECHA": "Fecha",
    "HORA": "Hora",
    "ENTERO": "Número entero",
    "DECIMAL": "Número con decimales",
    "TEXTO": "Texto",
}


def titulo_completo(campo) -> str:
    """El título tal como se lee, no el pedazo que quedó en la celda.

    Varias planillas ponen el principio de la pregunta en una celda combinada
    de arriba —«¿Cuenta con…»— y en cada columna sólo la continuación. Leídas
    sueltas quedan como «… reglamento de convivencia?». Se recompone juntando
    el grupo con el título.
    """
    titulo = (campo.get("titulo_esperado") or "").strip()
    grupo = (campo.get("grupo") or "").strip()
    if not grupo or not titulo.startswith(("...", "…")):
        return titulo
    resto = titulo.lstrip(".… ").strip()
    return f"{grupo.rstrip('. ')}… {resto}"


def limite_numerico(campo) -> str:
    """El rango admitido, dicho con números y no con un mensaje de error.

    La pantalla mostraba «Es una cantidad inusualmente alta» y «Ese número no
    puede ser», que son lo que el sistema dirá si te equivocás — pero no dicen
    cuál es el número. Quien viene acá viene a saber qué puede poner.

    Cuando hay dos rangos —uno que avisa y otro que bloquea— manda el que
    bloquea para el tope, porque es el que decide si el archivo entra.
    """
    topes = [
        (
            json.loads(r["parametros"] or "{}")
            if isinstance(r["parametros"], str)
            else (r["parametros"] or {})
        )
        for r in campo.get("reglas") or []
        if r.get("tipo_regla") == "RANGO"
    ]
    if not topes:
        return ""
    minimos = [t["minimo"] for t in topes if t.get("minimo") is not None]
    # El tope que se muestra es el más exigente: es el primero que se va a
    # quejar, y por lo tanto el que hay que respetar.
    maximos = [t["maximo"] for t in topes if t.get("maximo") is not None]
    if minimos and maximos:
        return f", entre {max(minimos):g} y {min(maximos):g}"
    if maximos:
        return f", hasta {min(maximos):g}"
    if minimos:
        return f", desde {max(minimos):g}"
    return ""


def que_se_espera(campo) -> str:
    """El tipo de dato dicho en castellano, con su límite si lo tiene."""
    if campo.get("catalogo"):
        return "Una opción de la lista"
    tipo = TIPO_EN_CASTELLANO.get(campo.get("tipo_dato"), campo.get("tipo_dato") or "")
    largo = campo.get("longitud_maxima")
    if tipo == "Texto" and largo:
        return f"Texto, hasta {largo} caracteres"
    if campo.get("tipo_dato") in ("ENTERO", "DECIMAL"):
        return f"{tipo}{limite_numerico(campo)}"
    return tipo


def valores_admitidos(campo) -> dict:
    """Qué acepta la columna: el tipo de dato, o la lista si la tiene.

    Era dos columnas —«Qué se espera» y «Valores admitidos»— y para un campo con
    lista decían lo mismo dos veces: «Una opción de la lista» al lado de la
    lista. Ahora es una sola: o el tipo, o la lista.
    """
    if not campo.get("catalogo"):
        return {"texto": que_se_espera(campo), "detalle": ""}

    cuantos = campo.get("opciones") or 0
    valores = campo.get("valores") or ""
    if cuantos > TOPE_PARA_ENUMERAR:
        nombre = NOMBRE_DE_LISTA_LARGA.get(
            campo["catalogo"], campo.get("lista") or campo["catalogo"]
        )
        return {"texto": f"{nombre} ({cuantos})", "detalle": valores}
    return {"texto": f"Lista: {valores}" if valores else "Lista", "detalle": ""}


class ReglasView(SeccionPermitidaMixin, LoginRequiredMixin, TemplateView):
    """Una hoja por vez, con lo que se espera de cada columna.

    De sólo lectura para todos, **menos para el administrador nacional**: él
    puede cambiar la severidad de un control y los límites de un rango. Es lo
    que vuelve cierta, para quien usa el sistema, la promesa de que cambiar una
    regla es cambiar un dato.
    """

    seccion = "estructura"
    template_name = "runac/reglas.html"

    def post(self, request, *_args, **_kwargs):
        """Guardar un cambio de regla y volver a la misma hoja."""
        volver = (
            f'{reverse("runac:estructura")}?hoja={quote(request.POST.get("hoja", ""))}'
        )

        if not puede_administrar(request.user):
            messages.error(request, "Sólo el administrador puede cambiar las reglas.")
            return redirect(volver)

        try:
            accion = request.POST.get("accion")
            if accion == "rangos":
                self._guardar_rangos(request)
            elif accion == "obligatorio":
                self._guardar_obligatorio(request)
            else:
                self._guardar_severidad(request)
        except (ValueError, reglas_service.NoSePuede) as error:
            messages.error(request, str(error) or "No se indicó qué regla cambiar.")
        return redirect(volver)

    def _guardar_rangos(self, request):
        """Los dos techos de un campo: crea, cambia o quita, según qué se completó."""
        campo_id = int(request.POST.get("campo", ""))
        cambios = reglas_service.guardar_rangos(
            campo_id,
            (request.POST.get("avisa_min"), request.POST.get("avisa_max")),
            (request.POST.get("frena_min"), request.POST.get("frena_max")),
        )
        if not cambios["hubo"]:
            messages.info(
                request, "No había nada que cambiar: los límites quedaron igual."
            )
            return

        dicho = [
            f"{cambios[clave]} {palabra}"
            for clave, palabra in (
                ("creadas", "condición nueva"),
                ("cambiadas", "cambiada"),
                ("quitadas", "quitada"),
            )
            if cambios[clave]
        ]
        aviso = f'Listo: {", ".join(dicho)}.'
        if cambios["desprendidas"]:
            aviso += (
                " La condición que se cambió la compartían varios campos:"
                " el cambio vale sólo para éste."
            )
        messages.success(request, aviso)

    def _guardar_obligatorio(self, request):
        """Si la columna hay que completarla sí o sí. Cambia también la plantilla."""
        resultado = reglas_service.cambiar_obligatorio(
            int(request.POST.get("campo", "")),
            request.POST.get("obligatorio") == "1",
        )
        if not resultado["cambio"]:
            messages.info(request, "No había nada que cambiar.")
            return
        messages.success(
            request,
            (
                "Listo: la columna pasa a ser obligatoria."
                if resultado["obligatorio"]
                else "Listo: la columna deja de ser obligatoria."
            ),
        )

    def _guardar_severidad(self, request):
        """Si el control avisa o frena, para las condiciones que no son rangos."""
        aplicacion_id = int(request.POST.get("aplicacion", ""))
        resultado = reglas_service.cambiar_severidad(
            aplicacion_id, request.POST.get("severidad", "")
        )
        if not resultado["cambio"]:
            messages.info(
                request, "No había nada que cambiar: la condición quedó igual."
            )
        else:
            messages.success(request, "Listo: se cambió si la condición avisa o frena.")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        hojas = svc.hojas_disponibles()
        for h in hojas:
            h["clave"] = f'{h["archivo"]}|{h["hoja"]}'
            h["etiqueta"] = (
                h["hoja"]
                if h["hoja"].upper().replace(" ", "") in h["archivo"].replace("_", "")
                else f'{h["archivo"]} — {h["hoja"]}'
            )

        elegida = self.request.GET.get("hoja") or (hojas[0]["clave"] if hojas else "")
        archivo, _, nombre_hoja = elegida.partition("|")

        campos = []
        if archivo and nombre_hoja:
            for c in svc.reglas_de_hoja(archivo, nombre_hoja):
                reglas = [_para_editar(r) for r in c["reglas"]]
                campos.append(
                    {
                        **c,
                        "titulo": titulo_completo(c),
                        "valores": valores_admitidos(c),
                        "letra": _letra(c["orden"]),
                        "reglas": reglas,
                        # Los rangos van juntos en un renglón de cuatro
                        # casilleros; el resto, uno por condición.
                        "rangos": _dos_techos(reglas),
                        "otras": _las_demas(reglas, _dos_techos(reglas)),
                        "numerico": c.get("tipo_dato") in ("ENTERO", "DECIMAL"),
                    }
                )

        ctx.update(
            {
                "hojas": hojas,
                "hoja_elegida": elegida,
                "archivo": archivo,
                "nombre_hoja": nombre_hoja,
                "campos": campos,
                "obligatorios": sum(1 for c in campos if c["obligatorio"]),
                "con_regla": sum(1 for c in campos if c["reglas"]),
                # El nombre técnico sólo le sirve a quien va a programar contra
                # esto; al que carga la planilla lo distrae.
                "ver_tecnico": puede_administrar(self.request.user),
                # La definición se cambia antes de abrir el período, no con el
                # operativo en curso: con provincias cargando, mover una regla
                # significa que a dos que presentaron lo mismo les fue distinto.
                "periodo_abierto": reglas_service.periodo_abierto(),
                "puede_editar": (
                    puede_administrar(self.request.user)
                    and not reglas_service.periodo_abierto()
                ),
            }
        )
        return ctx


def _para_editar(regla: dict) -> dict:
    """Los límites a la vista, para que la pantalla pueda ofrecerlos en dos casilleros."""
    crudos = regla.get("parametros")
    par = json.loads(crudos) if isinstance(crudos, str) else (crudos or {})
    return {
        **regla,
        "minimo": par.get("minimo"),
        "maximo": par.get("maximo"),
        "es_rango": regla.get("tipo_regla") == "RANGO",
        "compartida": (regla.get("usos") or 1) > 1,
    }


def _dos_techos(reglas: list) -> dict:
    """Los rangos del campo, uno por severidad, para el renglón de cuatro casilleros.

    Si un campo tuviera dos rangos con la misma severidad —no pasa hoy, pero la
    base lo permite— se toma el primero y el otro queda listado aparte, sin
    editar. Antes perderlo en silencio que mostrarlo mal.
    """
    techos = {}
    for regla in reglas:
        if regla["es_rango"]:
            techos.setdefault(regla["severidad"], regla)
    return {
        "avisa": techos.get("ADVERTENCIA"),
        "frena": techos.get("BLOQUEANTE"),
        "hay": bool(techos),
    }


def _las_demas(reglas: list, techos: dict) -> list:
    """Todo lo que no entró en los cuatro casilleros, para no perder nada."""
    tomadas = {
        t["aplicacion_id"] for t in (techos["avisa"], techos["frena"]) if t is not None
    }
    return [r for r in reglas if r["aplicacion_id"] not in tomadas]


def _letra(orden: int) -> str:
    """El número de columna como lo muestra Excel: 1 -> A, 27 -> AA."""
    letras = ""
    while orden > 0:
        orden, resto = divmod(orden - 1, 26)
        letras = chr(65 + resto) + letras
    return letras
