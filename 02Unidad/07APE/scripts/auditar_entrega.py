#!/usr/bin/env python3
"""Cuarta revisión: audita datos, requisitos documentales y video final."""

import ast
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

import imageio_ffmpeg

from ape07.comparacion import comparar, exigir


BASE = Path(__file__).resolve().parents[1]


def auditar():
    huella_guia = hashlib.sha256((BASE / "ape_guia simulacion semana 7-signed.pdf").read_bytes()).hexdigest()
    exigir(huella_guia == "649135d1d507ca217afb48b18f867169ba7ea254be0efa57446d484b2ce4137a", "Guía modificada.")
    with tempfile.TemporaryDirectory(prefix="ape07-final-") as carpeta:
        tabla = comparar(BASE / "resultados/python", BASE / "resultados/java", Path(carpeta))
    exigir(list(tabla["N"]) == [1000, 10000, 100000, 1000000], "Faltan tamaños de la guía.")
    pdf = BASE / "APE07-CoelloAnderson-U2-Simulacion.pdf"
    texto = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], check=True, capture_output=True, text=True).stdout
    paginas = texto.split("\f")
    exigir(len(paginas) == 10 and not paginas[-1].strip(), "El PDF debe tener nueve páginas completas.")
    coordenadas = subprocess.run(["pdftotext", "-bbox-layout", str(pdf), "-"],
                                 check=True, capture_output=True, text=True).stdout
    namespace = {"x": "http://www.w3.org/1999/xhtml"}
    for palabra in ET.fromstring(coordenadas).findall(".//x:word", namespace):
        exigir(53 <= float(palabra.attrib["xMin"]) <= float(palabra.attrib["xMax"]) <= 543
               and 20 <= float(palabra.attrib["yMin"]) <= float(palabra.attrib["yMax"]) <= 820,
               f"Texto fuera de los márgenes del PDF: {palabra.text}")
    for indice, pagina in enumerate(paginas[:-1], 1):
        exigir("FEIRNNR - Carrera de Computación" in pagina and
               bool(re.search(r"APE 07 · Simulación\s+" + str(indice) + r"\s*$", pagina)), "Encabezado o paginación incorrectos.")
    for fragmento in ("Anderson Mateo Coello Jaramillo", "12 de noviembre de 2026", "13 de noviembre de 2026",
                      "¿Qué es Monte Carlo?", "¿Por qué el error disminuye al aumentar las muestras?",
                      "¿Qué relación existe entre precisión y costo computacional?",
                      "¿Qué diferencias se observaron entre Python y Java?",
                      "¿En qué otros problemas puede utilizarse Monte Carlo?", "M/M/1",
                      "El docente confirmó que la práctica corresponde a Monte Carlo"):
        exigir(fragmento in texto, f"Falta un dato o respuesta: {fragmento}")
    for fila in tabla.itertuples():
        exigir(f"{fila.pi_estimado:.8f}" in paginas[3] and f"{fila.error_absoluto:.8f}" in paginas[3]
               and f"{fila.tiempo_python_s:.8f}" in paginas[3] and f"{fila.tiempo_java_s:.8f}" in paginas[3],
               "El PDF no coincide con la tabla real.")
    qa = (BASE / "resultados/revision/qa.log").read_text()
    java = (BASE / "resultados/revision/java.log").read_text()
    exigir("Ran 10 tests" in qa and "\nOK\n" in qa and "FAILED" not in qa, "QA no aprobada.")
    exigir("Tests run: 10, Failures: 0, Errors: 0, Skipped: 0" in java and "BUILD SUCCESS" in java, "JUnit no aprobado.")
    for nombre in ("ANALISIS_01_REQUISITOS.md", "ANALISIS_02_MODELO.md", "ANALISIS_03_QA.md", "ANALISIS_04_ENTREGA.md"):
        exigir((BASE / "docs" / nombre).is_file(), f"Falta {nombre}.")
    for ruta in list((BASE / "python").rglob("*.py")) + list((BASE / "scripts").glob("*.py")):
        ast.parse(ruta.read_text(encoding="utf-8"))
    video = BASE / "evidencias/APE07-demostracion.mp4"
    metadatos = json.loads((video.parent / "video.json").read_text())
    exigir(metadatos["duracion_segundos"] == 76 and metadatos["fotogramas"] == 760, "Duración de video incorrecta.")
    exigir(hashlib.sha256(video.read_bytes()).hexdigest() == metadatos["sha256_video"], "Video modificado.")
    exigir(hashlib.sha256((BASE / "resultados/comparacion/tabla_guia.csv").read_bytes()).hexdigest()
           == metadatos["sha256_tabla"], "El video corresponde a otra tabla.")
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-i", str(video), "-f", "null", "-"],
                   check=True, timeout=120)
    informe = {
        "fecha_verificacion": datetime.now(ZoneInfo("America/Guayaquil")).isoformat(),
        "correcto": True, "paginas_pdf": 9, "campanas_qa": 10, "pruebas_junit": 10,
        "estados_comparados": 2000000, "puntos_comparados": 1000000, "video_segundos": 76,
        "guia_intacta_sha256": huella_guia, "pdf_sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(),
        "aclaracion_rubrica": "El estudiante comunicó que el docente confirmó Monte Carlo; alcance aclarado",
        "fuentes_codigo_sha256": {
            str(ruta.relative_to(BASE)): hashlib.sha256(ruta.read_bytes()).hexdigest()
            for raiz in (BASE / "python/src", BASE / "python/tests", BASE / "java/src", BASE / "scripts")
            for ruta in sorted(raiz.rglob("*")) if ruta.suffix in (".py", ".java", ".sh")
        },
    }
    (BASE / "resultados/revision/auditoria_final.json").write_text(
        json.dumps(informe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Auditoría final correcta: datos completos, 9 páginas, 10 campañas QA, 10 JUnit y video decodificado de 76 s.")


if __name__ == "__main__":
    auditar()
