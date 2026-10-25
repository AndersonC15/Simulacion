from dataclasses import replace
from decimal import Decimal
import pytest

from Controlador.simulacion import ControladorSimulacion
from Modelo.estimacion import estimar
from Modelo.numeros import ErrorValidacion


def test_estima_todos_los_datos():
    parametros = estimar(("100", "110", "132"))
    assert parametros.tasa == Decimal("0.15")
    assert parametros.horizonte == 2


def test_experimento_es_el_mismo_al_presentarlo():
    controlador = ControladorSimulacion()
    experimento = controlador.ejecutar()
    assert controlador.experimento_actual() is experimento
    controlador.configurar(replace(controlador.parametros, tasa="0"))
    assert controlador.ultimo is None


def test_arreglo_invalido_no_cambia_configuracion():
    controlador = ControladorSimulacion()
    anterior = controlador.parametros
    with pytest.raises(ErrorValidacion):
        controlador.cambiar_datos(("0", "10"))
    assert controlador.parametros is anterior
    controlador.cambiar_datos(("0", "10"), automatico=False)
    assert controlador.parametros.p0 == 0
