#!/usr/bin/env bash
set -euo pipefail
APE07_RAIZ="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$APE07_RAIZ"
export MPLCONFIGDIR="$APE07_RAIZ/.cache/matplotlib"
mkdir -p resultados/revision
[[ -x .venv/bin/python ]] || { echo 'Ejecuta primero bash scripts/preparar.sh' >&2; exit 2; }
mvn -B -ntp -f java/pom.xml package -DskipTests > resultados/revision/compilacion.log 2>&1
.venv/bin/python -m ape07 | tee resultados/revision/ejecucion_python.log
java -jar java/target/ape07.jar | tee resultados/revision/ejecucion_java.log
.venv/bin/python scripts/entrega.py
echo 'Resultados y gráficas generados. Tras verificar, genera el informe académico y el video.'
