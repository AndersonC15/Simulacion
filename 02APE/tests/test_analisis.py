from dataclasses import replace
from decimal import Decimal
import pytest

from Modelo.analisis import analizar_ruido
from Modelo.parametros import Parametros
from Modelo.numeros import ErrorValidacion


def test_dispersion_con_semillas_compartidas_y_sin_recorte():
    parametros = Parametros(p0="1000000", tasa="0", sigma="10", horizonte="4")
    cero, base, doble = analizar_ruido(parametros)
    assert cero.desviacion == 0
    assert base.semillas == doble.semillas == cero.semillas
    assert len(base.finales) == 30
    assert doble.desviacion == 2 * base.desviacion or abs(doble.desviacion - 2 * base.desviacion) < Decimal("1e-25")
    assert analizar_ruido(parametros) == (cero, base, doble)


@pytest.mark.parametrize("replicas", [0, 1, 101, True, "30"])
def test_replicas_acotadas(replicas):
    with pytest.raises(ErrorValidacion):
        analizar_ruido(Parametros(), replicas)


def test_analisis_tiempo_acotado():
    with pytest.raises(ErrorValidacion):
        analizar_ruido(Parametros(horizonte="101"))


def test_sigma_cero_no_inventa_dispersion_al_centrar():
    from Modelo.estimacion import estimar
    from Modelo.datos import DATOS_OFICIALES
    cero = analizar_ruido(estimar(DATOS_OFICIALES))[0]
    assert len(set(cero.finales)) == 1
    assert cero.desviacion == 0
