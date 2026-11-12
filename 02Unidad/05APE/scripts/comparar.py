"""Valida ambos programas y arma las tablas y el informe del APE 05."""

import argparse
import csv
import json
import math
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SEMILLAS = (12_345, 54_321)
CANTIDAD = 10_000
MODULO = 2**32


def leer_csv(ruta: Path, semilla: int) -> list[tuple[int, int, float]]:
    with ruta.open(encoding="utf-8", newline="") as archivo:
        lector = csv.DictReader(archivo)
        if lector.fieldnames != ["n", "x", "u"]:
            raise ValueError(f"Cabecera incorrecta: {ruta}")
        filas = [(int(fila["n"]), int(fila["x"]), float(fila["u"])) for fila in lector]
    if len(filas) != CANTIDAD:
        raise ValueError(f"Se esperaban {CANTIDAD} observaciones: {ruta}")
    anterior = semilla
    for esperado_n, (n, estado, valor) in enumerate(filas, start=1):
        esperado_x = (1_664_525 * anterior + 1_013_904_223) % MODULO
        if n != esperado_n or estado != esperado_x or valor != estado / MODULO:
            raise ValueError(f"Recurrencia, índice o normalización incorrectos: {ruta}, fila {n}")
        if not 0 <= estado < MODULO or not 0 <= valor < 1:
            raise ValueError(f"Valor fuera de rango: {ruta}, fila {n}")
        anterior = estado
    if len({estado for _, estado, _ in filas}) != CANTIDAD:
        raise ValueError(f"Estado repetido dentro de la muestra: {ruta}")
    return filas


def leer_resumen(ruta: Path, lenguaje: str, semilla: int, filas: list) -> dict:
    resumen = json.loads(ruta.read_text(encoding="utf-8"))
    parametros = {"a": 1_664_525, "c": 1_013_904_223, "m": MODULO, "semilla": semilla}
    if (resumen["parametros"] != parametros or resumen["cantidad"] != CANTIDAD
            or resumen["lenguaje"] != lenguaje):
        raise ValueError(f"Metadatos incorrectos: {ruta}")
    esperado = {
        "coprimos": True, "factores_dividen": True, "regla_cuatro": True,
        "periodo_teorico": MODULO, "preperiodo_observado": None, "periodo_observado": None,
    }
    if resumen["periodo"] != esperado:
        raise ValueError(f"Análisis del período incorrecto: {ruta}")
    valores = [fila[2] for fila in filas]
    media = math.fsum(valores) / CANTIDAD
    estadisticas = {
        "minimo": min(valores), "maximo": max(valores), "media": media,
        "varianza_poblacional": math.fsum((x - media) ** 2 for x in valores) / CANTIDAD,
    }
    for nombre, esperado_valor in estadisticas.items():
        if not math.isclose(resumen["estadisticas_descriptivas"][nombre], esperado_valor,
                            rel_tol=1e-12, abs_tol=1e-14):
            raise ValueError(f"Estadística {nombre} incorrecta: {ruta}")
    return resumen


def comparar(resultados: Path) -> None:
    tablas, resumenes = {}, {}
    for semilla in SEMILLAS:
        por_lenguaje = {}
        for carpeta, lenguaje in (("python", "Python"), ("java", "Java")):
            base = resultados / carpeta / f"semilla_{semilla}"
            filas = leer_csv(base.with_suffix(".csv"), semilla)
            resumenes[(carpeta, semilla)] = leer_resumen(base.with_suffix(".json"), lenguaje, semilla, filas)
            if not base.with_suffix(".png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n"):
                raise ValueError(f"Gráfica PNG inválida: {base}")
            por_lenguaje[carpeta] = filas
        if por_lenguaje["python"] != por_lenguaje["java"]:
            raise ValueError(f"Las secuencias difieren con semilla {semilla}")
        tablas[semilla] = por_lenguaje
        with (resultados / f"comparacion_20_semilla_{semilla}.csv").open(
            "w", encoding="utf-8", newline=""
        ) as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(("n", "x_python", "x_java", "u_python", "u_java", "coinciden"))
            for py, java in zip(por_lenguaje["python"][:20], por_lenguaje["java"][:20]):
                escritor.writerow((py[0], py[1], java[1], format(py[2], ".17g"),
                                    format(java[2], ".17g"), "si"))
    diferencias = sum(uno[1] != dos[1] for uno, dos in
                      zip(tablas[12_345]["python"], tablas[54_321]["python"]))
    if diferencias != CANTIDAD:
        raise ValueError("El cambio de semilla no produjo las diferencias esperadas.")
    escribir_informe(resultados, tablas, resumenes, diferencias)
    print("Comparación correcta: 20 000 pares Python/Java idénticos (dos semillas).")
    print(f"Informe y tablas: {resultados}")


def escribir_informe(resultados: Path, tablas: dict, resumenes: dict, diferencias: int) -> None:
    lineas = [
        "# Informe de resultados — APE 05: Generador Congruencial Lineal", "",
        "Informe construido a partir de las salidas ejecutadas de Python y Java.", "",
        "## Objetivo y método", "",
        "Se implementó `X(n+1) = (a·X(n)+c) mod m`, con `Un = Xn/m`.",
        "Parámetros: `a=1664525`, `c=1013904223`, `m=4294967296`; 10 000 salidas por lenguaje y semilla.",
        "`X0` es la semilla; las salidas comienzan en `X1`. La segunda semilla `54321` es una elección del experimento; la guía solo solicita cambiarla.", "",
        "## Comparación de las primeras 20 observaciones", "",
        "Se verificó igualdad numérica exacta de enteros y normalizados en las 10 000 posiciones de cada semilla. Las tablas presentan las primeras 20 requeridas.",
        "Aquí se muestran 12 decimales; los CSV conservan precisión de ida y vuelta.", "",
    ]
    for semilla in SEMILLAS:
        lineas.extend([f"### Semilla {semilla}", "",
                       "| n | Xn Python | Xn Java | Un Python | Un Java | Coinciden |",
                       "|---:|---:|---:|---:|---:|:---:|"])
        for py, java in zip(tablas[semilla]["python"][:20], tablas[semilla]["java"][:20]):
            lineas.append(f"| {py[0]} | {py[1]} | {java[1]} | {py[2]:.12f} | {java[2]:.12f} | Sí |")
        lineas.extend(["", f"![Secuencia Python, semilla {semilla}](python/semilla_{semilla}.png)", "",
                       f"![Secuencia Java, semilla {semilla}](java/semilla_{semilla}.png)", ""])
    lineas.extend(["## Estadísticas descriptivas", "",
                   "| Lenguaje | Semilla | Mínimo | Máximo | Media | Varianza poblacional |",
                   "|:---|---:|---:|---:|---:|---:|"])
    for (lenguaje, semilla), resumen in resumenes.items():
        s = resumen["estadisticas_descriptivas"]
        lineas.append(f"| {lenguaje.title()} | {semilla} | {s['minimo']:.10f} | {s['maximo']:.10f} | {s['media']:.10f} | {s['varianza_poblacional']:.10f} |")
    lineas.extend(["", "Estas medidas describen la muestra; no constituyen pruebas de uniformidad ni de independencia.", "",
                   "## Cambio de semilla y observaciones", "",
                   f"Cambiar de 12345 a 54321 modificó las {diferencias} observaciones en la misma posición. Python y Java continuaron coincidiendo exactamente.",
                   "Cada PNG muestra la secuencia completa, las primeras 200 salidas y los pares consecutivos `(Un, Un+1)` tratados en las diapositivas.",
                   "Los valores oscilan dentro de `[0,1)`. La dispersión visual de los pares no demuestra independencia; un período largo tampoco elimina las limitaciones del LCG.", "",
                   (RAIZ / "docs/fundamento.md").read_text(encoding="utf-8"), ""])
    (resultados / "informe.md").write_text("\n".join(lineas), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resultados", type=Path, default=RAIZ / "resultados")
    args = parser.parse_args()
    try:
        comparar(args.resultados)
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f"Comparación fallida: {error}\n")


if __name__ == "__main__":
    main()

