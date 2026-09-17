"""Tests de la importación: dependencias entre archivos y tablas receptoras.

Son las dos reglas que el documento funcional pone del lado del sistema y no del
operador: qué archivo necesita a cuál lo dice la configuración, y el nombre de
la tabla receptora se deduce en vez de guardarse.
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
    """Reemplaza las consultas a la base por una configuración en memoria.

    «referencias» es lo que la Capa 1 declara: qué archivos nombra cada uno.
    """

    def fabricar(importados=(), referencias=None):
        referencias = referencias or {}
        monkeypatch.setattr(
            svc, "estado_de_la_presentacion", lambda *a, **k: _estado(importados)
        )
        monkeypatch.setattr(svc, "archivos_esperados", lambda periodo: list(ARCHIVOS))
        monkeypatch.setattr(
            svc,
            "archivos_referenciados",
            lambda codigo, periodo: referencias.get(codigo, []),
        )

    return fabricar


# ---------------------------------------------------------------------------
# Dependencias entre archivos
#
# Traban dos cosas distintas y las dos hacen falta:
#
#   La POLÍTICA: las nóminas van después de los dispositivos. Una nómina dice
#   dónde está alojado un chico; si el dispositivo no se declaró, habla de algo
#   que para el sistema no existe.
#
#   La REFERENCIA declarada en la Capa 1: además, un archivo espera a los que
#   nombra campo a campo, y eso verifica que cada valor exista.
#
# Un tiempo estuvo sólo la segunda y quedó floja: como la referencia del MPE no
# estaba declarada, se podía importar antes que los dispositivos.
# ---------------------------------------------------------------------------

DISPOSITIVOS = ["DISP_PENAL", "DISP_SCP"]
REFERENCIAS = {"MPJ_DAE": ["DISP_PENAL"], "MPE": ["DISP_SCP"]}


def test_un_archivo_de_dispositivos_no_espera_a_nadie(sin_base):
    sin_base(referencias=REFERENCIAS)
    assert svc.dependencias_faltantes("DISP_PENAL", "Salta", "2026_T1") == []
    assert svc.dependencias_faltantes("DISP_SCP", "Salta", "2026_T1") == []


def test_ninguna_nomina_entra_antes_que_los_dispositivos(sin_base):
    """Vale incluso para la que no tiene ninguna referencia declarada."""
    sin_base(referencias=REFERENCIAS)
    faltan = [
        f["codigo"] for f in svc.dependencias_faltantes("MPI", "Salta", "2026_T1")
    ]
    assert sorted(faltan) == sorted(DISPOSITIVOS)


def test_con_los_dispositivos_cargados_la_nomina_se_habilita(sin_base):
    sin_base(importados=tuple(DISPOSITIVOS), referencias=REFERENCIAS)
    assert svc.dependencias_faltantes("MPI", "Salta", "2026_T1") == []


def test_la_referencia_declarada_se_suma_a_la_politica(sin_base):
    """MPJ_DAE nombra a DISP_PENAL, y además espera a los dos por política."""
    sin_base(importados=("DISP_SCP",), referencias=REFERENCIAS)
    faltan = [
        f["codigo"] for f in svc.dependencias_faltantes("MPJ_DAE", "Salta", "2026_T1")
    ]
    assert faltan == ["DISP_PENAL"]


def test_una_nomina_no_espera_a_otra_nomina(sin_base):
    """MPI y MPE van antes que la penal en el orden, y no tienen nada que ver."""
    sin_base(importados=tuple(DISPOSITIVOS), referencias=REFERENCIAS)
    faltan = [
        f["codigo"] for f in svc.dependencias_faltantes("MPJ_DAE", "Salta", "2026_T1")
    ]
    assert "MPI" not in faltan and "MPE" not in faltan


def test_un_archivo_que_no_existe_espera_igual_a_los_dispositivos(sin_base):
    """No se conoce, así que no se lo exime: la política se aplica por descarte."""
    sin_base(importados=tuple(DISPOSITIVOS), referencias=REFERENCIAS)
    assert svc.dependencias_faltantes("INVENTADO", "Salta", "2026_T1") == []


# ---------------------------------------------------------------------------
# Convención de nombres de las tablas receptoras
#
# El nombre no se guarda en la base: lo deducen tanto el que crea las tablas
# (capa2.py) como el que inserta (importar.py). Si la convención cambia en un
# lado y no en el otro, la importación escribe en una tabla que no existe.
# ---------------------------------------------------------------------------


def test_archivo_de_una_sola_hoja():
    assert nombre_tabla_receptora("MPE", "MPE", False, 1) == "mir_c2_mpe_v1"


def test_archivo_de_varias_hojas_lleva_la_hoja_en_el_nombre():
    nombre = nombre_tabla_receptora("MPJ_DAE", "DAE", True, 1)
    assert nombre == "mir_c2_mpj_dae_v1_dae"


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
