"""El mensaje de un rango dice para qué lado se sale el valor.

Los mensajes configurados de los rangos están escritos para el máximo. Un 2 en
una columna que pide entre 10 y 200 salía como «cantidad de personal
inusualmente alta» (lo marcó el responsable funcional, 27-09-2026).
"""

import sys
from pathlib import Path

import pytest

_MOTOR = Path(__file__).resolve().parents[1] / "services" / "motor"
if str(_MOTOR) not in sys.path:
    sys.path.insert(0, str(_MOTOR))

from importar import aplicar_regla, mensaje_para_quien_carga  # noqa: E402

ALTA = "Es una cantidad de personal inusualmente alta. Conviene revisar el dato."


def _regla(severidad="ADVERTENCIA", configurado=ALTA, **parametros):
    return {
        "id": 1,
        "nombre": "rango_plantel",
        "tipo_regla": "RANGO",
        "severidad": severidad,
        "mensaje_configurado": configurado,
        "parametros": parametros or {"minimo": 10, "maximo": 200},
    }


def _mensaje(regla, valor):
    motor = aplicar_regla(regla, valor, {}, {})
    return motor and mensaje_para_quien_carga(regla, valor, motor)


def test_por_encima_del_maximo_vale_el_mensaje_configurado():
    assert _mensaje(_regla(), 208) == ALTA


def test_por_debajo_del_minimo_no_dice_alta():
    mensaje = _mensaje(_regla(), 2)
    assert "alta" not in mensaje
    assert "más bajo que el mínimo esperado (10)" in mensaje
    assert mensaje.endswith("Conviene revisar el dato.")


def test_un_bloqueante_por_debajo_pide_corregir():
    regla = _regla("BLOQUEANTE", "Esa edad no puede ser.", minimo=0, maximo=120)
    assert _mensaje(regla, -3).endswith("Hay que corregirlo en el Excel.")


def test_una_regla_solo_con_minimo_conserva_su_mensaje():
    regla = _regla(configurado="Un identificador empieza en uno.", minimo=1)
    assert _mensaje(regla, 0) == "Un identificador empieza en uno."


@pytest.mark.parametrize("valor", [10, 150, 200])
def test_dentro_del_rango_no_hay_mensaje(valor):
    assert _mensaje(_regla(), valor) is None


def test_sin_mensaje_configurado_queda_el_del_motor():
    regla = _regla(configurado=None)
    assert _mensaje(regla, 2) == "El valor 2 es menor que el mínimo esperado (10)."
