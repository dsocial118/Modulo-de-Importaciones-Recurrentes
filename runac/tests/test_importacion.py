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
    {
        "codigo": "LEGAJO_NYA",
        "orden_importacion": 3,
        "obligatorio": 1,
        "importada": False,
    },
    {"codigo": "MPI", "orden_importacion": 4, "obligatorio": 1, "importada": False},
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
# Traba UNA sola cosa: la referencia declarada en la Capa 1. Un archivo espera
# a los que nombra campo a campo, y a nadie más.
#
# Hasta el 22-09-2026 había además una política escrita en el código —«las
# nóminas van después de TODOS los dispositivos»— que sobre-trababa: con ella,
# el MPJ no se podía importar hasta que estuviera también el archivo de
# hogares, que no nombra. Estos tests son los que dejan eso clavado.
# ---------------------------------------------------------------------------

DISPOSITIVOS = ["DISP_PENAL", "DISP_SCP"]
REFERENCIAS = {
    "MPJ_DAE": ["DISP_PENAL", "LEGAJO_NYA"],
    "MPE": ["DISP_SCP", "LEGAJO_NYA"],
    "MPI": ["LEGAJO_NYA"],
}


def test_un_archivo_que_no_nombra_a_nadie_no_espera_a_nadie(sin_base):
    sin_base(referencias=REFERENCIAS)
    assert svc.dependencias_faltantes("DISP_PENAL", "Salta", "2026_T1") == []
    assert svc.dependencias_faltantes("DISP_SCP", "Salta", "2026_T1") == []
    assert svc.dependencias_faltantes("LEGAJO_NYA", "Salta", "2026_T1") == []


def test_la_nomina_penal_no_espera_al_archivo_de_hogares(sin_base):
    """El caso que planteó el responsable funcional el 22-09-2026.

    El MPJ nombra dispositivos penales y el legajo. Con los dos importados
    tiene que poder entrar, aunque el archivo de hogares no esté: no lo nombra
    en ningún campo, así que no hay nada que verificar contra él.
    """
    sin_base(importados=("DISP_PENAL", "LEGAJO_NYA"), referencias=REFERENCIAS)
    assert svc.dependencias_faltantes("MPJ_DAE", "Salta", "2026_T1") == []


def test_espera_solo_a_los_que_nombra(sin_base):
    sin_base(importados=("DISP_SCP", "LEGAJO_NYA"), referencias=REFERENCIAS)
    faltan = [
        f["codigo"] for f in svc.dependencias_faltantes("MPJ_DAE", "Salta", "2026_T1")
    ]
    assert faltan == ["DISP_PENAL"]


def test_una_nomina_no_espera_a_otra_nomina(sin_base):
    sin_base(importados=tuple(DISPOSITIVOS) + ("LEGAJO_NYA",), referencias=REFERENCIAS)
    faltan = [
        f["codigo"] for f in svc.dependencias_faltantes("MPJ_DAE", "Salta", "2026_T1")
    ]
    assert "MPI" not in faltan and "MPE" not in faltan


def test_las_tres_nominas_esperan_al_legajo(sin_base):
    """El legajo manda sobre los datos del chico: las tres lo nombran."""
    sin_base(importados=tuple(DISPOSITIVOS), referencias=REFERENCIAS)
    for codigo in ("MPI", "MPE", "MPJ_DAE"):
        faltan = [
            f["codigo"] for f in svc.dependencias_faltantes(codigo, "Salta", "2026_T1")
        ]
        assert faltan == ["LEGAJO_NYA"], codigo


def test_un_archivo_que_no_existe_no_espera_a_nadie(sin_base):
    """Sin referencias declaradas no hay nada que esperar, y no se inventa."""
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


# ---------------------------------------------------------------------------
# Qué se anuncia al terminar de importar
#
# El 26-09-2026 un legajo con errores se rechazó (FALLIDA, 18 bloqueantes) y la
# pantalla anunció «Los registros se incorporaron. Quedan 8 advertencias»: el
# resultado de la importación ANTERIOR, que seguía vigente. Se leía la vigente
# en vez de la última que se intentó.
# ---------------------------------------------------------------------------


def _con_importaciones(monkeypatch, importaciones):
    monkeypatch.setattr(svc, "presentacion_de", lambda *a: {"id": 1})
    monkeypatch.setattr(svc, "archivos_esperados", lambda periodo: list(ARCHIVOS))
    # Como la consulta real: la más reciente primero.
    monkeypatch.setattr(svc, "importaciones_de", lambda pid: list(importaciones))


def test_si_la_nueva_falla_la_ultima_es_la_nueva_y_la_vigente_la_anterior(
    monkeypatch,
):
    fallida = {"id": 14, "archivo_codigo": "LEGAJO_NYA", "estado": "FALLIDA"}
    anterior = {"id": 10, "archivo_codigo": "LEGAJO_NYA", "estado": "VALIDA"}
    _con_importaciones(monkeypatch, [fallida, anterior])

    fila = next(
        f
        for f in svc.estado_de_la_presentacion("Chubut", "2026_T1")["archivos"]
        if f["codigo"] == "LEGAJO_NYA"
    )

    assert fila["ultima"]["id"] == 14, "se anuncia la que se acaba de intentar"
    assert fila["importacion"]["id"] == 10, "los datos siguen siendo los anteriores"
    assert fila["importada"]


def test_el_aviso_de_la_pantalla_actual_lee_la_ultima():
    from runac.views.carga import _ultima_importacion

    filas = [
        {
            "codigo": "LEGAJO_NYA",
            "importacion": {"id": 10, "estado": "VALIDA", "advertencias": 8},
            "ultima": {"id": 14, "estado": "FALLIDA", "bloqueantes": 18},
        }
    ]
    aviso = _ultima_importacion(filas, "LEGAJO_NYA")

    assert aviso["recien_estado"] == "FALLIDA"
    assert aviso["recien_bloqueantes"] == 18
    assert aviso["recien_importacion_id"] == 14


def test_la_demostracion_encuentra_todos_sus_archivos(monkeypatch):
    """El botón «Armar demostración» usaba una copia propia de los archivos, que
    quedó de la definición anterior y se rechazaba (pendiente #84). Ahora usa
    los archivos de prueba del repositorio, y cada archivo del período tiene
    que estar ahí."""
    from runac.services import demo_service

    monkeypatch.setattr(svc, "archivos_esperados", lambda periodo: list(ARCHIVOS))
    plan = demo_service.plan()

    assert [codigo for codigo, _ in plan] == [a["codigo"] for a in ARCHIVOS]
    for _, nombre in plan:
        assert (demo_service.ARCHIVOS / nombre).exists(), nombre
