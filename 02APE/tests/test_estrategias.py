from decimal import Decimal, localcontext
from Modelo.parametros import Parametros
from Modelo.estrategias import Deterministico, Discreto, Estocastico
from Modelo.numeros import ErrorValidacion
import pytest


def test_exponencial_referencia():
    resultado = Deterministico().simular(Parametros(horizonte="1")).poblaciones[-1]
    with localcontext() as contexto:
        contexto.prec = 100
        referencia = Decimal(1000) * Decimal("0.1").exp()
        assert abs(resultado - referencia) < Decimal("1e-45")


def test_exponencial_constante():
    assert set(Deterministico().simular(Parametros(tasa="0")).poblaciones) == {Decimal(1000)}


def test_discreto_un_periodo():
    assert Discreto().simular(Parametros(horizonte="1")).poblaciones == (Decimal(1000), Decimal(1100))


def test_discreto_rechaza_negatividad():
    with pytest.raises(ErrorValidacion):
        Discreto().simular(Parametros(tasa="-1.1"))


def test_estocastico_ruido_controlado_y_recuperacion():
    valores = iter(("-1100", "10"))
    resultado = Estocastico(ruido=lambda: next(valores)).simular(Parametros(tasa="0", horizonte="2"))
    assert resultado.poblaciones == (Decimal(1000), Decimal(0), Decimal(10))


def test_semilla_reproducible():
    parametros = Parametros(sigma="10")
    assert Estocastico().simular(parametros) == Estocastico().simular(parametros)
