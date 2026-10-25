import csv
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest
from Controlador.simulacion import ControladorSimulacion
from Vista.graficas import VistaGraficas
from Modelo.resultados import Serie
from Modelo.numeros import ErrorValidacion


def test_png_y_csv_reproducibles_en_ruta_con_espacios(tmp_path):
    controlador = ControladorSimulacion()
    experimento = controlador.ejecutar()
    carpeta = tmp_path / "ruta con espacios"
    png, tabla = VistaGraficas().guardar(experimento, carpeta)
    original = png.read_bytes()
    assert original.startswith(b"\x89PNG\r\n\x1a\n")
    with tabla.open() as archivo:
        filas = list(csv.reader(archivo))
    assert filas[1][2] == str(experimento.series[0].poblaciones[0])
    assert len(filas) == 1 + sum(len(s.tiempos) for s in experimento.series) + len(experimento.observaciones)
    VistaGraficas().guardar(experimento, carpeta, mostrar=True)
    assert png.read_bytes() == original
    assert controlador.experimento_actual() is experimento
    assert plt.get_fignums() == []


def test_fallo_escritura_cierra_figuras(tmp_path):
    (tmp_path / "comparacion.png").mkdir()
    with pytest.raises(OSError):
        VistaGraficas().guardar(ControladorSimulacion().ejecutar(), tmp_path)
    assert plt.get_fignums() == []


def test_salida_directorio_es_archivo(tmp_path):
    destino = tmp_path / "archivo"
    destino.write_text("conservar")
    with pytest.raises(OSError):
        VistaGraficas().guardar(ControladorSimulacion().ejecutar(), destino)
    assert destino.read_text() == "conservar"


def test_no_fusiona_tiempos_casi_iguales(tmp_path):
    experimento = ControladorSimulacion().ejecutar()
    serie = Serie("Prueba", tuple(map(Decimal, ("0", "1", "1.000000000000000000001"))),
                  tuple(map(Decimal, ("1", "2", "3"))))
    with pytest.raises(ErrorValidacion, match="fusionaría"):
        VistaGraficas().guardar(replace(experimento, series=(serie,)), tmp_path)
    assert plt.get_fignums() == []
