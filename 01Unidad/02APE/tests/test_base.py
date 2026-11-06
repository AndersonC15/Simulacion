from decimal import Decimal
import pytest
from Modelo.datos import DATOS_OFICIALES, parsear_arreglo
from Modelo.parametros import Parametros
from Modelo.numeros import ErrorValidacion, multiplicar


def test_datos_guia():
    assert DATOS_OFICIALES == tuple(map(Decimal, (1000, 1100, 1250, 1400, 1600, 1850, 2100)))


def test_entrada_decimal_conservada():
    assert parsear_arreglo("[1,2500; 2.123456789012345678901]")[1] == Decimal("2.123456789012345678901")


def test_operacion_exacta():
    assert multiplicar(Decimal("1.234567890123456789"), Decimal("0.1")) == Decimal("0.1234567890123456789")


@pytest.mark.parametrize("opciones", [{"dt": "0"}, {"sigma": "-1"}, {"p0": "NaN"}, {"semilla": -1}])
def test_parametros_invalidos(opciones):
    with pytest.raises(ErrorValidacion):
        Parametros(**opciones)
