#!/usr/bin/env python3
"""Video sin audio que demuestra el modelo y los resultados reales guardados."""

import hashlib
import json
import math
from pathlib import Path
import subprocess
import textwrap

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from ape07.comparacion import comparar


BASE = Path(__file__).resolve().parents[1]
DESTINO = BASE / "evidencias/APE07-demostracion.mp4"
ANCHO, ALTO, FPS = 1280, 720, 10
FUENTE = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


def fuente(tamano, mono=False):
    return ImageFont.truetype(MONO if mono else FUENTE, tamano)


def lienzo(titulo, subtitulo=""):
    imagen = Image.new("RGB", (ANCHO, ALTO), "#f4f3ed")
    dibujo = ImageDraw.Draw(imagen)
    dibujo.rectangle((0, 0, ANCHO, 110), fill="#193c4a")
    dibujo.text((45, 24), titulo, font=fuente(32), fill="white")
    dibujo.text((46, 73), subtitulo, font=fuente(18), fill="#d1e6e9")
    dibujo.text((45, 680), "APE 07 · Simulación · Anderson Mateo Coello Jaramillo", font=fuente(17), fill="#193c4a")
    return imagen


def parrafo(imagen, texto, posicion=(55, 145), ancho=88, tamano=24):
    dibujo = ImageDraw.Draw(imagen)
    contenido = "\n".join(textwrap.fill(linea, width=ancho) for linea in texto.split("\n"))
    dibujo.multiline_text(posicion, contenido, font=fuente(tamano), fill="#172f36", spacing=13)


def panel_imagen(imagen, ruta, caja=(40, 130, 1240, 650)):
    recurso = Image.open(ruta).convert("RGB")
    recurso.thumbnail((caja[2] - caja[0], caja[3] - caja[1]))
    imagen.paste(recurso, (caja[0] + (caja[2] - caja[0] - recurso.width) // 2,
                           caja[1] + (caja[3] - caja[1] - recurso.height) // 2))


def generar():
    tabla = comparar(BASE / "resultados/python", BASE / "resultados/java", BASE / "resultados/comparacion")
    qa = (BASE / "resultados/revision/qa.log").read_text()
    if "Ran 10 tests" not in qa or "\nOK\n" not in qa:
        raise ValueError("Primero ejecuta las diez campañas QA.")
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    temporal = DESTINO.with_name(".APE07-demostracion.tmp.mp4")
    comando = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-v", "error", "-f", "rawvideo", "-vcodec", "rawvideo",
               "-pix_fmt", "rgb24", "-s", f"{ANCHO}x{ALTO}", "-r", str(FPS), "-i", "-", "-an",
               "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-pix_fmt", "yuv420p",
               "-movflags", "+faststart", str(temporal)]
    proceso = subprocess.Popen(comando, stdin=subprocess.PIPE)
    fotogramas = 0

    def escena(imagen, segundos):
        nonlocal fotogramas
        contenido = imagen.tobytes()
        for _ in range(segundos * FPS):
            proceso.stdin.write(contenido)
            fotogramas += 1

    try:
        imagen = lienzo("Monte Carlo: estimación de π", "Guía firmada 007 · Python y Java · 12 y 13 de noviembre de 2026")
        parrafo(imagen, "Objetivo: aproximar π mediante puntos pseudoaleatorios.\n\n"
                "Comparo cuatro tamaños: 1 000, 10 000, 100 000 y 1 000 000.\n\n"
                "Este video usa los archivos de la ejecución real conservada.\n"
                "Es una demostración visual sin narración personal.\n\n"
                "Código, datos, informe y comandos están dentro de 07APE.")
        escena(imagen, 8)

        estados = np.fromfile(BASE / "resultados/python/secuencia.bin", dtype=">u4", count=4000)
        puntos = (2.0 * (estados.astype(np.float64) / 2147483647) - 1.0).reshape(-1, 2)
        for fotograma in range(12 * FPS):
            cantidad = max(1, len(puntos) * (fotograma + 1) // (12 * FPS))
            imagen = lienzo("1. Modelo: círculo inscrito en un cuadrado", "Animación de los primeros 2 000 puntos de la secuencia real")
            dibujo = ImageDraw.Draw(imagen)
            dibujo.rectangle((80, 150, 560, 630), fill="white", outline="#193c4a", width=2)
            dibujo.ellipse((80, 150, 560, 630), outline="#193c4a", width=2)
            interiores = 0
            for coordenada_x, coordenada_y in puntos[:cantidad]:
                dentro = coordenada_x * coordenada_x + coordenada_y * coordenada_y <= 1
                interiores += int(dentro)
                pixel_x, pixel_y = 320 + 240 * coordenada_x, 390 - 240 * coordenada_y
                dibujo.ellipse((pixel_x - 2, pixel_y - 2, pixel_x + 2, pixel_y + 2),
                                fill="#126d82" if dentro else "#b74834")
            parrafo(imagen, f"Área del cuadrado = 4\nÁrea del círculo = π\n\n"
                    f"Interior: x² + y² ≤ 1\nπ estimado = 4 × Nc / N\n\n"
                    f"N mostrado = {cantidad}\nNc = {interiores}\nπ estimado = {4 * interiores / cantidad:.6f}\n\n"
                    "Cada punto consume dos\nvalores consecutivos del LCG.", (650, 170), 39, 23)
            proceso.stdin.write(imagen.tobytes())
            fotogramas += 1

        imagen = lienzo("2. Código y arquitectura MVC + Strategy", "Fragmento del modelo Python; Java aplica las mismas operaciones")
        fuente_modelo = (BASE / "python/src/ape07/modelo.py").read_text()
        comienzo = fuente_modelo.index("        dentro = 0\n")
        fin = fuente_modelo.index("        return Resultado(puntos, dentro)", comienzo)
        lineas = fuente_modelo[comienzo:fin].splitlines()
        codigo = "\n".join(linea[8:] for linea in lineas)
        ImageDraw.Draw(imagen).multiline_text((50, 140), codigo, font=fuente(16, True), fill="#193c4a", spacing=7)
        parrafo(imagen, "Modelo: cálculo. Vista: consola y archivos. Controlador: coordinación.\n"
                "Strategy: el estimador recibe FuenteUniforme; QA inyecta casos controlados.", (50, 520), 91, 22)
        escena(imagen, 10)

        for lenguaje in ("python", "java"):
            imagen = lienzo(f"3. Ejecución real: {lenguaje.capitalize()}", "Salida capturada por scripts/ejecutar.sh; tiempos en segundos")
            registro = (BASE / f"resultados/revision/ejecucion_{lenguaje}.log").read_text()
            contenido = "\n".join(registro.splitlines()[:6])
            ImageDraw.Draw(imagen).multiline_text((45, 155), contenido, font=fuente(18, True), fill="#193c4a", spacing=22)
            parrafo(imagen, "Cinco mediciones por tamaño y tres calentamientos.\n"
                    "La mediana incluye generación y clasificación; excluye archivos y gráficas.\n\n"
                    "Ambos programas utilizan la misma semilla: 123457.", (50, 430), 85, 23)
            escena(imagen, 8)

        imagen = lienzo("4. Tabla solicitada en la guía", "Los números se leen del CSV consolidado y auditado")
        lineas = [f"{'N':>10} {'π estimado':>14} {'Error':>14} {'Python (s)':>14} {'Java (s)':>14}"]
        for fila in tabla.itertuples():
            lineas.append(f"{fila.N:10d} {fila.pi_estimado:14.8f} {fila.error_absoluto:14.8f} "
                          f"{fila.tiempo_python_s:14.8f} {fila.tiempo_java_s:14.8f}")
        ImageDraw.Draw(imagen).multiline_text((45, 160), "\n".join(lineas), font=fuente(20, True), fill="#193c4a", spacing=24)
        mejor = tabla.loc[tabla["error_absoluto"].idxmin()]
        parrafo(imagen, f"Mejor aproximación observada: N = {int(mejor['N']):,}.\n"
                "El error no disminuye en cada aumento de muestra.\n"
                "La tendencia ideal 1/√N no garantiza mejora monótona.", (50, 465), 85, 24)
        escena(imagen, 10)

        imagen = lienzo("5. Interpretación del error y los tiempos", "Gráficas calculadas a partir de los cuatro experimentos")
        panel_imagen(imagen, BASE / "resultados/comparacion/error_tiempos.png")
        escena(imagen, 10)

        imagen = lienzo("6. Verificación adversaria y conclusiones", "Diez campañas QA, diez pruebas JUnit y comparación completa")
        parrafo(imagen, "✓ 2 000 000 de estados comparados, uno por uno.\n"
                "✓ 1 000 000 de puntos; cuatro estimaciones idénticas.\n"
                "✓ Se detectaron estados alterados incluso con un hash actualizado.\n"
                "✓ Se rechazaron NaN, tamaños inválidos y resultados adulterados.\n\n"
                "Mismos parámetros y semilla: mismo resultado numérico.\n"
                "Más puntos aumentan el trabajo; el error puede oscilar.\n\n"
                "Demostración en vivo: bash scripts/ejecutar.sh\n"
                "Verificación: bash scripts/verificar.sh", tamano=23)
        escena(imagen, 10)
    finally:
        proceso.stdin.close()
        codigo_salida = proceso.wait()
    if codigo_salida:
        raise RuntimeError("Falló la codificación del video.")
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-i", str(temporal), "-f", "null", "-"],
                   check=True, timeout=120)
    temporal.replace(DESTINO)
    metadatos = {"duracion_segundos": fotogramas / FPS, "fotogramas": fotogramas,
                 "fps": FPS, "resolucion": [ANCHO, ALTO], "audio": False,
                 "contenido": "modelo animado con puntos reales; código, salidas capturadas, tablas y gráficas",
                 "sha256_video": hashlib.sha256(DESTINO.read_bytes()).hexdigest(),
                 "sha256_tabla": hashlib.sha256((BASE / "resultados/comparacion/tabla_guia.csv").read_bytes()).hexdigest()}
    (DESTINO.parent / "video.json").write_text(json.dumps(metadatos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Video generado y decodificado: {DESTINO}; {fotogramas / FPS:.0f} segundos.")


if __name__ == "__main__":
    generar()
