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

# Una opción más larga que esto ya no entra cómoda en una línea compartida.
LARGO_PARA_UNA_LINEA = 25

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


def tipo_solo(campo) -> str:
    """El tipo de dato, sin los límites: ahora se editan aparte, en casilleros.

    Se conserva aunque estén los casilleros al lado, porque **el tipo es parte
    de lo que la columna admite**: no es lo mismo un entero que un número con
    decimales, y el día que un campo sea un porcentaje o un monto la diferencia
    importa.
    """
    tipo = TIPO_EN_CASTELLANO.get(campo.get("tipo_dato"), campo.get("tipo_dato") or "")
    largo = campo.get("longitud_maxima")
    if tipo == "Texto" and largo:
        return f"Texto, hasta {largo} caracteres"
    return tipo


def valores_admitidos(campo) -> dict:
    """Qué acepta la columna: el tipo de dato, o la lista si la tiene.

    Era dos columnas —«Qué se espera» y «Valores admitidos»— y para un campo con
    lista decían lo mismo dos veces: «Una opción de la lista» al lado de la
    lista. Ahora es una sola: o el tipo, o la lista.
    """
    if not campo.get("catalogo"):
        return {"texto": tipo_solo(campo), "detalle": "", "opciones": []}

    cuantos = campo.get("opciones") or 0
    valores = campo.get("valores") or ""
    if cuantos > TOPE_PARA_ENUMERAR:
        nombre = NOMBRE_DE_LISTA_LARGA.get(
            campo["catalogo"], campo.get("lista") or campo["catalogo"]
        )
        return {"texto": f"{nombre} ({cuantos})", "detalle": valores, "opciones": []}

    opciones = [v.strip() for v in valores.split("·") if v.strip()]
    # En una línea sólo si se leen en una línea. Con opciones largas o con comas
    # adentro —«Sí, está actualizada pero no se aplica»— la fila se vuelve una
    # sopa y no se distingue dónde termina una y empieza la otra.
    apretadas = all(len(o) <= LARGO_PARA_UNA_LINEA and "," not in o for o in opciones)
    if opciones and apretadas:
        return {
            "texto": "Lista: " + " / ".join(opciones),
            "detalle": "",
            "opciones": [],
        }
    return {
        "texto": f"Lista de {cuantos} opciones:" if opciones else "Lista",
        "detalle": "",
        "opciones": opciones,
    }


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
            if request.POST.get("accion") == "severidad":
                self._guardar_severidad(request)
            else:
                self._guardar_hoja(request)
        except reglas_service.ErroresDeValidacion as problema:
            for error in problema.errores:
                messages.error(request, error)
            messages.warning(
                request, "No se guardó ningún cambio: corregí eso y volvé a guardar."
            )
        except (ValueError, reglas_service.NoSePuede) as error:
            messages.error(request, str(error) or "No se indicó qué cambiar.")
        return redirect(volver)

    def _guardar_hoja(self, request):
        """Todo lo que se tocó en la hoja, de una sola vez.

        Llegan sólo los campos modificados: la pantalla deja fuera los que
        quedaron como estaban, así el guardado no repasa sesenta columnas para
        cambiar dos.
        """
        cambios, severidades = _leer_cambios(request.POST)
        if not cambios and not severidades:
            messages.info(request, "No había nada que guardar.")
            return

        hecho = reglas_service.guardar_hoja(cambios, severidades)
        if not hecho["detalle"]:
            messages.info(request, "Los valores eran los mismos: no se cambió nada.")
            return
        messages.success(
            request,
            f'Guardado. {len(hecho["detalle"])} cambios: '
            + " · ".join(hecho["detalle"]),
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
                        # Sobre una lista cerrada un rango no significa nada,
                        # así que ahí no se ofrecen los casilleros.
                        "numerico": c.get("tipo_dato") in ("ENTERO", "DECIMAL")
                        and not c.get("catalogo"),
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


def _leer_cambios(datos):
    """Arma lo que la pantalla mandó: por campo, y las severidades sueltas.

    Los controles se llaman `oblig_12`, `amin_12`, `amax_12`, `bmin_12`,
    `bmax_12` y `sev_45` —este último por aplicación de regla, no por campo—.
    La pantalla manda **los cuatro límites de una fila o ninguno**: si sólo
    llegara el mínimo, el máximo ausente se leería como «vaciado» y borraría
    una condición que nadie tocó.
    """
    cambios: dict = {}
    severidades: dict = {}
    for clave in datos:
        pedazo, _, crudo = clave.partition("_")
        if not crudo.isdigit():
            continue
        numero = int(crudo)
        if pedazo == "sev":
            severidades[numero] = datos.get(clave)
        elif pedazo == "oblig":
            cambios.setdefault(numero, {})["obligatorio"] = datos.get(clave) == "1"
        elif pedazo == "amin":
            cambios.setdefault(numero, {})["advierte"] = (
                datos.get(f"amin_{numero}"),
                datos.get(f"amax_{numero}"),
            )
        elif pedazo == "bmin":
            cambios.setdefault(numero, {})["bloquea"] = (
                datos.get(f"bmin_{numero}"),
                datos.get(f"bmax_{numero}"),
            )
    return cambios, severidades


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
