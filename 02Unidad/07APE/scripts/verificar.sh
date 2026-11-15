#!/usr/bin/env bash
set -euo pipefail
APE07_RAIZ="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$APE07_RAIZ"
export MPLCONFIGDIR="$APE07_RAIZ/.cache/matplotlib"
mkdir -p resultados/revision
[[ -x .venv/bin/python ]] || { echo 'Ejecuta primero bash scripts/preparar.sh' >&2; exit 2; }
mvn -B -ntp -f java/pom.xml verify 2>&1 | tee resultados/revision/java.log
.venv/bin/python -m unittest discover -s python/tests -v 2>&1 | tee resultados/revision/qa.log
.venv/bin/python scripts/entrega.py
