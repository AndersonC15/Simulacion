#!/usr/bin/env bash
set -euo pipefail
APE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
APE_PYTHON="$APE_DIR/python/.venv/bin/python"
source "$APE_DIR/scripts/entorno_java.sh"
if [[ ! -x "$APE_PYTHON" || ! -f "$APE_DIR/java/target/ape06.jar" ]]; then
    echo 'Primero ejecuta ./scripts/preparar.sh' >&2
    exit 2
fi
cd "$APE_DIR"
"$APE_PYTHON" -m ape06 ejecutar --config config/generadores.csv --salida resultados/python
"$APE_JAVA" -jar java/target/ape06.jar ejecutar --config config/generadores.csv --salida resultados/java
"$APE_PYTHON" -m ape06 benchmark --config config/generadores.csv --salida resultados/python
"$APE_JAVA" -jar java/target/ape06.jar benchmark --config config/generadores.csv --salida resultados/java
"$APE_PYTHON" -m ape06.controlador.entrega
