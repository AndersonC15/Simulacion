import pytest
from Modelo.numeros import ErrorValidacion
from Modelo.parametros import Parametros
from Modelo.estrategias import Discreto


def test_presupuesto_acumulado_evade_lista_decimal_enorme():
    with pytest.raises(ErrorValidacion, match="2000000 dígitos"):
        Discreto().simular(Parametros(tasa="0.0000000001", horizonte="1000"))


def test_no_redondea_si_excede_precision_exacta():
    with pytest.raises(ErrorValidacion, match="10000 dígitos"):
        Discreto().simular(Parametros(tasa="0." + "1" * 80, horizonte="200"))
