from decimal import Decimal, localcontext
from Modelo.parametros import Parametros
from Modelo.estrategias import Deterministico


def test_exponencial_referencia():
    resultado = Deterministico().simular(Parametros(horizonte="1")).poblaciones[-1]
    with localcontext() as contexto:
        contexto.prec = 100
        referencia = Decimal(1000) * Decimal("0.1").exp()
        assert abs(resultado - referencia) < Decimal("1e-45")


def test_exponencial_constante():
    assert set(Deterministico().simular(Parametros(tasa="0")).poblaciones) == {Decimal(1000)}
