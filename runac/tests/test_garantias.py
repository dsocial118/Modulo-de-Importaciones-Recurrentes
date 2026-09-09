"""Tests de las garantías que el sistema promete.

Distintos de los demás: no verifican que una función haga lo suyo, sino que el
sistema cumpla lo que el análisis funcional afirma. Una auditoría no pregunta si
`convertir` convierte; pregunta si es verdad que un archivo con un error no
incorpora ninguna fila.

Cada test de acá nombra la promesa que protege. Si alguno falla, lo que se rompió
no es una función: es algo que está escrito en el documento y que dejó de ser
cierto.
"""

import sys
from pathlib import Path

import pytest

_MOTOR = Path(__file__).resolve().parents[1] / "services" / "motor"
if str(_MOTOR) not in sys.path:
    sys.path.insert(0, str(_MOTOR))

from importar import convertir, norm, texto_a_numero  # noqa: E402


# ---------------------------------------------------------------------------
# «Un cero informado es un dato»
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cero", [0, 0.0, "0", " 0 "])
def test_el_cero_no_es_ausencia_de_dato(cero):
    """Una capacidad de 0 plazas, o 0 agentes de salud, es una respuesta.

    En Python el cero es falso, así que `str(v or "")` lo convertía en vacío y
    el dato desaparecía. Si además el campo era obligatorio, daba un error que
    la provincia no podía entender.
    """
    assert norm(cero) != ""
    valor, error = convertir(cero, "ENTERO")
    assert error is None
    assert valor == 0


def test_el_vacio_sigue_siendo_vacio():
    """La corrección del cero no puede haber convertido el vacío en un dato."""
    for vacio in (None, "", "   "):
        assert norm(vacio) == ""
        assert convertir(vacio, "ENTERO") == (None, None)


# ---------------------------------------------------------------------------
# «Los números se interpretan siempre igual»
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "escrito,esperado",
    [
        ("1.250", 1250),  # punto de miles: tres dígitos detrás
        ("12", 12),
        ("1.250.000", 1250000),
    ],
)
def test_el_punto_separa_miles_cuando_le_siguen_tres_digitos(escrito, esperado):
    valor, error = convertir(escrito, "ENTERO")
    assert error is None
    assert valor == esperado


@pytest.mark.parametrize("escrito", ["1.5", "1,5", "0.75"])
def test_un_decimal_escrito_a_mano_no_se_vuelve_entero(escrito):
    """«1.5» valía 15: se borraba el punto por suponerlo separador de miles.

    Para un campo entero eso no es un valor distinto, es un valor diez veces
    más grande. Ahora se rechaza diciendo por qué.
    """
    valor, error = convertir(escrito, "ENTERO")
    assert valor is None
    assert "decimales" in error


@pytest.mark.parametrize(
    "escrito,esperado",
    [("1,5", 1.5), ("1.5", 1.5), ("1.250,75", 1250.75), ("1.250", 1250.0)],
)
def test_el_decimal_se_lee_igual_venga_con_coma_o_con_punto(escrito, esperado):
    valor, error = convertir(escrito, "DECIMAL")
    assert error is None
    assert valor == esperado


def test_la_interpretacion_numerica_esta_en_un_solo_lugar():
    """La pantalla de edición usa la misma función que la importación.

    Si cada una resolviera por su cuenta, un valor corregido a mano podría
    guardarse distinto del que entró por el archivo.
    """
    from runac.services import edicion_service

    assert edicion_service.texto_a_numero is texto_a_numero


# ---------------------------------------------------------------------------
# «Un error bloqueante impide que entre una sola fila del archivo»
# ---------------------------------------------------------------------------


def test_ninguna_operacion_del_circuito_queda_sin_control_de_seccion():
    """Pedir sesión no es controlar el acceso.

    Ocho vistas —las acciones del circuito, observar, responder, expediente,
    comprobante, las dos descargas y editar un campo— sólo verificaban que
    hubiera sesión iniciada. Cualquier usuario autenticado podía invocarlas
    escribiendo la dirección.
    """
    from runac.permissions import SeccionPermitidaMixin
    from runac.views import circuito, edicion

    for modulo in (circuito, edicion):
        for nombre in dir(modulo):
            clase = getattr(modulo, nombre)
            if not (isinstance(clase, type) and nombre.endswith("View")):
                continue
            if clase.__module__ != modulo.__name__:
                continue  # importada de otro lado
            assert issubclass(
                clase, SeccionPermitidaMixin
            ), f"{nombre} no declara control de sección"
            assert getattr(clase, "seccion", ""), (
                f"{nombre} tiene el control pero no declara a qué sección "
                "pertenece, de modo que no verifica nada"
            )


def test_la_completitud_no_puede_llegar_del_navegador():
    """La condición para cerrar la carga se calcula desde la presentación.

    Salía de la jurisdicción enviada en el formulario y, si el parámetro
    faltaba, el valor por defecto era «listo»: bastaba omitirlo para cerrar una
    carga incompleta.
    """
    import inspect

    from runac.services import importacion_service as svc
    from runac.views.circuito import AccionView

    cuerpo = inspect.getsource(AccionView.post)
    assert "presentacion_completa" in cuerpo
    assert 'get("listo", True)' not in cuerpo, "vuelve el valor por defecto permisivo"

    # Una presentación que no existe no puede estar completa. Es la trampa en la
    # que cae un COUNT sin filas: cero faltantes se lee como «está todo».
    fuente = inspect.getsource(svc.presentacion_completa)
    assert (
        "obligatorios > 0" in fuente
    ), "sin archivos obligatorios declarados no hay nada que dar por completo"


def test_la_hoja_prepara_su_insercion_pero_no_la_ejecuta():
    """Es lo que hace restrictiva a la importación en archivos de varias hojas.

    Si cada hoja insertara por su cuenta, un archivo podía quedar declarado
    fallido —con cero filas incorporadas en su cabecera— y conservar igual las
    filas de las hojas que no tenían errores. Afectaba a MPJ/DAE y a los
    dispositivos penales, que son los archivos con más de una hoja.

    Se verifica sobre el código porque la garantía es estructural: la hoja
    devuelve su inserción y quien decide ejecutarla es el archivo, después de
    sumar los bloqueantes de todas.
    """
    import inspect

    import importar

    cuerpo_hoja = inspect.getsource(importar.procesar_hoja)
    assert "executemany" not in cuerpo_hoja, (
        "procesar_hoja no debe insertar: debe devolver su inserción para que "
        "la decida el archivo completo"
    )
    assert '"insercion": insercion' in cuerpo_hoja

    # El recorrido de hojas vive en _ejecutar; procesar_carpeta es la envoltura
    # que arma los argumentos.
    cuerpo_archivo = inspect.getsource(importar._ejecutar)
    assert "if not bloqueantes:" in cuerpo_archivo, (
        "el archivo debe insertar sólo cuando ninguna de sus hojas tiene " "bloqueantes"
    )
    assert cuerpo_archivo.index("bloqueantes = sum(") < cuerpo_archivo.index(
        "if not bloqueantes:"
    ), "los bloqueantes de todas las hojas se suman ANTES de decidir la inserción"


def test_el_nombre_del_archivo_decide_si_entra():
    """Un archivo de otra provincia, otro trimestre u otra planilla no entra.

    Era una advertencia: el sistema avisaba «el nombre no se corresponde» y lo
    importaba igual, de modo que los datos de Chaco podían quedar dentro de la
    presentación de Chubut. Ahora la comprobación se hace antes de guardar el
    archivo y rechaza.

    Se admite lo que venga después del nombre esperado —el sufijo
    `_CON_ERRORES` de los archivos de prueba— porque eso no cambia de qué
    archivo, período ni jurisdicción se trata.
    """
    from runac.services.importacion_service import _nombre_corresponde

    def corresponde(nombre):
        return _nombre_corresponde(nombre, "MPI", "2026_T1", "Chaco")

    assert corresponde("MPI_2026_T1_Chaco.xlsx")
    assert corresponde("MPI_2026_T1_Chaco_CON_ERRORES.xlsx"), "sufijo admitido"
    assert not corresponde("MPI_2026_T1_Chubut.xlsx"), "otra jurisdicción"
    assert not corresponde("MPI_2025_T4_Chaco.xlsx"), "otro período"
    assert not corresponde("MPE_2026_T1_Chaco.xlsx"), "otra planilla"

    # Las tildes y los separadores no son el problema que se quiere detectar.
    assert _nombre_corresponde(
        "MPI_2026_T1_EntreRios.xlsx", "MPI", "2026_T1", "Entre Ríos"
    )


def test_al_corregir_se_vuelve_a_evaluar_la_fila_entera(monkeypatch):
    """Una advertencia se da por resuelta sólo si dejó de incumplirse.

    Antes bastaba con tocar el campo: la corrección marcaba resuelta cualquier
    advertencia de esa fila y ese campo sin volver a aplicar la regla. Un dato
    cambiado por otro igual de inválido quedaba «resuelto» y nadie lo miraba.

    Y se evalúa la fila entera, no la celda: hay reglas que preguntan por otro
    campo, así que corregir un dato puede resolver la advertencia de otro —o
    crearla—.
    """
    from runac.services import edicion_service as edicion

    identifica = {
        "id": 1,
        "nombre": "identifica",
        "titulo_esperado": "¿Se identifica con algún pueblo originario?",
        "tipo_dato": "TEXTO",
        "obligatorio": False,
        "longitud_maxima": None,
        "catalogo": None,
    }
    cual = {**identifica, "id": 2, "nombre": "cual", "titulo_esperado": "Cuál"}
    regla = {
        "id": 10,
        "nombre": "pueblo originario declarado",
        "tipo_regla": "OBLIGATORIO_SI",
        "severidad": "ADVERTENCIA",
        "mensaje_configurado": None,
        "parametros": {
            "campo_condicion": "identifica",
            "operador": "IGUAL",
            "valor_condicion": "Sí",
        },
    }
    monkeypatch.setattr(edicion, "reglas_de_los_campos", lambda campos: {2: [regla]})
    campos = [identifica, cual]

    def hallazgos(valores):
        return edicion.hallazgos_de_la_fila(campos, valores, "2026_T1")

    assert hallazgos({"identifica": "Sí", "cual": ""}), "declara y no dice cuál"
    assert not hallazgos({"identifica": "Sí", "cual": "Qom"}), "completó el dato"
    # Lo que la marca por campo no podía resolver: se corrigió el OTRO campo.
    assert not hallazgos({"identifica": "No", "cual": ""}), "ya no corresponde"


def test_la_advertencia_resuelta_se_busca_en_su_propia_hoja():
    """En un archivo de varias hojas, la fila 5 de una no es la fila 5 de otra.

    Sin el nombre de la hoja, corregir un dato de la nómina daba por resueltas
    las advertencias de la misma fila de la otra hoja del archivo. Afecta a
    MPJ/DAE y a los dispositivos penales.
    """
    import inspect

    from runac.services import edicion_service as edicion

    fuente = inspect.getsource(edicion._reconciliar_advertencias)
    assert "nombre_hoja = %s" in fuente
    assert "numero_fila = %s" in fuente


def test_una_regla_que_el_motor_no_sabe_evaluar_no_pasa_en_silencio():
    """Es la peor forma de fallar: la validación apagada sin que nadie se entere.

    Un tipo de regla mal escrito en la Capa 1, o un operador que no existe,
    devolvían «se cumple». El archivo entraba como si lo hubieran controlado.
    """
    import pytest as _pytest

    import importar

    with _pytest.raises(importar.ReglaInvalida):
        importar.aplicar_regla(
            {"tipo_regla": "LO_QUE_SEA", "parametros": {}}, "x", {}, {}
        )
    with _pytest.raises(importar.ReglaInvalida):
        importar.comparar("a", "PARECIDO_A", "b")
    with _pytest.raises(importar.ReglaInvalida):
        importar.aplicar_regla(
            {
                "tipo_regla": "EJECUTAR_FUNCION",
                "parametros": {"funcion": "validar_lo_que_sea"},
            },
            "x",
            {},
            {},
        )
