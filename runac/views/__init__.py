"""Vistas del prototipo.

Son delgadas a propósito: reciben el pedido, llaman al servicio y arman el
contexto. **No deciden nada.** Es la forma que pide SISOC y la que permite que
esto se mude al repositorio sin reescribir la lógica.
"""

from .inicio import InicioView, EntrarView, salir
from .plantillas import PlantillasView, descargar_plantilla
from .carga import CargarView, CargarArchivoView, ResultadoView, DetalleView
from .estructura import EstructuraView, CamposView
from .edicion import EdicionView, EditarCampoView
from .circuito import (
    AccionView,
    ObservarView,
    ResponderView,
    ExpedienteView,
    ComprobanteView,
    RevisionView,
    PlanillaDeErroresView,
    ArchivoMarcadoView,
)

__all__ = [
    "InicioView",
    "EntrarView",
    "salir",
    "PlantillasView",
    "descargar_plantilla",
    "CargarView",
    "CargarArchivoView",
    "ResultadoView",
    "DetalleView",
    "EstructuraView",
    "CamposView",
    "EdicionView",
    "EditarCampoView",
    "AccionView",
    "ObservarView",
    "ResponderView",
    "ExpedienteView",
    "ComprobanteView",
    "RevisionView",
    "PlanillaDeErroresView",
    "ArchivoMarcadoView",
]
