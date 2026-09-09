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

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from runac.permissions import SeccionPermitidaMixin, puede_administrar
from runac.services import importacion_service as svc

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


def que_se_espera(campo) -> str:
    """El tipo de dato dicho en castellano."""
    if campo.get("catalogo"):
        return "Una opción de la lista"
    tipo = TIPO_EN_CASTELLANO.get(campo.get("tipo_dato"), campo.get("tipo_dato") or "")
    largo = campo.get("longitud_maxima")
    if tipo == "Texto" and largo:
        return f"Texto, hasta {largo} caracteres"
    return tipo


def valores_admitidos(campo) -> dict:
    """Qué valores acepta la columna: la lista, o el nombre de la lista."""
    if not campo.get("catalogo"):
        return {"texto": "", "detalle": ""}
    cuantos = campo.get("opciones") or 0
    valores = campo.get("valores") or ""
    if cuantos > TOPE_PARA_ENUMERAR:
        nombre = NOMBRE_DE_LISTA_LARGA.get(
            campo["catalogo"], campo.get("lista") or campo["catalogo"]
        )
        return {"texto": f"{nombre} ({cuantos})", "detalle": valores}
    return {"texto": valores, "detalle": ""}


class ReglasView(SeccionPermitidaMixin, LoginRequiredMixin, TemplateView):
    """Una hoja por vez, con lo que se espera de cada columna."""

    seccion = "estructura"
    template_name = "runac/reglas.html"

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
                campos.append(
                    {
                        **c,
                        "titulo": titulo_completo(c),
                        "espera": que_se_espera(c),
                        "valores": valores_admitidos(c),
                        "letra": _letra(c["orden"]),
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
            }
        )
        return ctx


def _letra(orden: int) -> str:
    """El número de columna como lo muestra Excel: 1 -> A, 27 -> AA."""
    letras = ""
    while orden > 0:
        orden, resto = divmod(orden - 1, 26)
        letras = chr(65 + resto) + letras
    return letras
