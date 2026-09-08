"""Tests de la importación: orden de carga y convención de tablas receptoras.

Son las dos reglas que el documento funcional pone del lado del sistema y no del
operador: el orden lo controla el sistema, y el nombre de la tabla receptora se
deduce en vez de guardarse.
"""

import sys
from pathlib import Path

import pytest

from runac.services import importacion_service as svc

# El motor corre también fuera de Django, así que se importa por ruta.
_MOTOR = Path(__file__).resolve().parents[1] / "services" / "motor"
if str(_MOTOR) not in sys.path:
    sys.path.insert(0, str(_MOTOR))

from comun import (
    nombre_tabla_receptora,
)  # noqa: E402  # pylint: disable=wrong-import-position


ARCHIVOS = [
    {
        "codigo": "DISP_PENAL",
        "orden_importacion": 1,
        "obligatorio": 1,
        "importada": False,
    },
    {
        "codigo": "DISP_SCP",
        "orden_importacion": 2,
        "obligatorio": 1,
        "importada": False,
    },
    {"codigo": "MPI", "orden_importacion": 3, "obligatorio": 1, "importada": False},
    {"codigo": "MPE", "orden_importacion": 4, "obligatorio": 1, "importada": False},
    {"codigo": "MPJ_DAE", "orden_importacion": 5, "obligatorio": 1, "importada": False},
]


def _estado(importados=()):
    archivos = [{**a, "importada": a["codigo"] in importados} for a in ARCHIVOS]
    return {
        "presentacion": {"id": 1, "estado": "EN_CARGA"},
        "archivos": archivos,
        "listo": all(a["importada"] for a in archivos),
    }


@pytest.fixture(name="sin_base")
def _sin_base(monkeypatch):
    """Reemplaza la consulta a la base por un estado armado en memoria."""

    def fabricar(importados=()):
        monkeypatch.setattr(
            svc, "estado_de_la_presentacion", lambda *a, **k: _estado(importados)
        )

    return fabricar


# ---------------------------------------------------------------------------
# Orden de importación
# ---------------------------------------------------------------------------


def test_el_primer_archivo_no_tiene_dependencias(sin_base):
    sin_base()
    assert svc.dependencias_faltantes("DISP_PENAL", "Salta", "2026_T1") == []


def test_una_nomina_sin_dispositivos_no_se_puede_importar(sin_base):
    sin_base()
    faltan = svc.dependencias_faltantes("MPE", "Salta", "2026_T1")
    assert [f["codigo"] for f in faltan] == ["DISP_PENAL", "DISP_SCP", "MPI"]


def test_con_las_dependencias_cargadas_se_habilita(sin_base):
    sin_base(importados=("DISP_PENAL", "DISP_SCP", "MPI"))
    assert svc.dependencias_faltantes("MPE", "Salta", "2026_T1") == []


def test_un_archivo_que_no_existe_no_bloquea_nada(sin_base):
    sin_base()
    assert svc.dependencias_faltantes("INVENTADO", "Salta", "2026_T1") == []


# ---------------------------------------------------------------------------
# Convención de nombres de las tablas receptoras
#
# El nombre no se guarda en la base: lo deducen tanto el que crea las tablas
# (capa2.py) como el que inserta (importar.py). Si la convención cambia en un
# lado y no en el otro, la importación escribe en una tabla que no existe.
# ---------------------------------------------------------------------------


def test_archivo_de_una_sola_hoja():
    assert nombre_tabla_receptora("MPE", "MPE", False, 1) == "runac_c2_mpe_v1"


def test_archivo_de_varias_hojas_lleva_la_hoja_en_el_nombre():
    nombre = nombre_tabla_receptora("MPJ_DAE", "DAE", True, 1)
    assert nombre == "runac_c2_mpj_dae_v1_dae"


def test_la_version_forma_parte_del_nombre():
    """Cada versión de estructura tiene su propia tabla: los datos de un período
    conservan la forma que tenían cuando se cargaron."""
    v1 = nombre_tabla_receptora("MPI", "MPI", False, 1)
    v2 = nombre_tabla_receptora("MPI", "MPI", False, 2)
    assert v1 != v2
    assert v2.endswith("_v2")


def test_el_nombre_respeta_el_limite_de_mysql():
    largo = nombre_tabla_receptora("A" * 40, "B" * 40, True, 99)
    assert len(largo) <= 64


def test_el_nombre_no_tiene_caracteres_raros():
    nombre = nombre_tabla_receptora("MPJ DAE", "Guardia Comisaría", True, 1)
    assert nombre.replace("_", "").isalnum()
