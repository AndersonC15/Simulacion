import csv
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from ape06.infraestructura.archivos import RepositorioResultados, leer_parametros
from ape06.infraestructura.comparacion import comparar_analisis
from ape06.modelo.datos import ParametrosLCG
from ape06.modelo.experimentos import ServicioSimulacion
from ape06.modelo.pruebas import ChiCuadrado, KolmogorovSmirnov, Rachas


BASE = Path(__file__).resolve().parents[2]
JAR = BASE / "java/target/ape06.jar"
JAVA = os.environ.get("APE_JAVA", str(BASE / ".tools/jdk-25/bin/java") if (BASE / ".tools/jdk-25/bin/java").exists()
                      else "/usr/lib/jvm/default-java/bin/java" if Path("/usr/lib/jvm/default-java/bin/java").exists() else "java")


def test_configuracion_compartida_y_nombres_invalidos():
    configuraciones = leer_parametros(BASE / "config/generadores.csv", ("minstd", "glibc", "zx81"))
    assert [p.m for p in configuraciones] == [2**31-1, 2**32, 2**17+1]
    with pytest.raises(ValueError, match="desconocidos"):
        leer_parametros(BASE / "config/generadores.csv", ("desconocido",))
    with pytest.raises(ValueError, match="duplicados"):
        leer_parametros(BASE / "config/generadores.csv", ("minstd", "minstd"))


@pytest.mark.skipif(not JAR.exists() or not shutil.which("java"), reason="Construir Java con mvn verify para integracion")
def test_programas_reales_48_bits_y_comparacion_detecta_corrupcion(tmp_path):
    config = tmp_path / "config.csv"
    config.write_text('nombre,semilla,a,c,m,fuente\njava48,1,25214903917,11,281474976710656,"Semana 5, parametros de 48 bits"\n', encoding="utf-8")
    python, java, salida = (tmp_path / nombre for nombre in ("python", "java", "comparacion"))
    opciones = ["ejecutar", "--config", str(config), "--generadores", "java48", "--n", "100"]
    subprocess.run([sys.executable, "-m", "ape06", *opciones, "--salida", str(python)], check=True, capture_output=True, text=True)
    subprocess.run([JAVA, "-jar", str(JAR), *opciones, "--salida", str(java)], check=True, capture_output=True, text=True)
    resultados = comparar_analisis(python, java, salida)
    assert resultados[0]["n"] == 100
    with (salida / "secuencia_java48.csv").open(newline="") as archivo:
        assert len(list(csv.DictReader(archivo))) == 100
    archivo = java / "java48/secuencia.csv"
    filas = archivo.read_text(encoding="utf-8").splitlines()
    filas[1] = "1,0,0.0"
    archivo.write_text("\n".join(filas)+"\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Estado diferente"):
        comparar_analisis(python, java, salida)


@pytest.mark.parametrize("opciones", [["--n", "49"], ["--alfa", "nan"], ["--generadores", "inexistente"]])
def test_python_cli_rechaza_entrada_sin_escribir_resultados(tmp_path, opciones):
    salida = tmp_path / "no_crear"
    resultado = subprocess.run([sys.executable, "-m", "ape06", "ejecutar", "--config",
                                str(BASE / "config/generadores.csv"), "--salida", str(salida), *opciones],
                               capture_output=True, text=True)
    assert resultado.returncode == 2
    assert "Error" in resultado.stderr
    assert not salida.exists()


def test_exportacion_constante_no_inventa_p_ni_rompe_json(tmp_path):
    p = ParametrosLCG("constante", 1, 1, 0, 16)
    analisis = ServicioSimulacion((ChiCuadrado(), KolmogorovSmirnov(), Rachas())).analizar(p, 50, .05)
    carpeta = RepositorioResultados(tmp_path).guardar_analisis(analisis)
    datos = json.loads((carpeta / "analisis.json").read_text(encoding="utf-8"))
    rachas = next(r for r in datos["pruebas"] if r["nombre"] == "rachas")
    assert rachas["valor_p"] is None
    assert rachas["decision"] == "No aplicable"
