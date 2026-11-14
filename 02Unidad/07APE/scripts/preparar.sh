#!/usr/bin/env bash
set -euo pipefail
APE07_RAIZ="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$APE07_RAIZ"
for herramienta in python3 java javac mvn; do
    command -v "$herramienta" >/dev/null || { echo "Falta $herramienta" >&2; exit 2; }
done
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else "Se requiere Python >= 3.11")'
if [[ ! -x .venv/bin/python ]]; then
    python3 -m venv .venv
fi
.venv/bin/python -m pip install -r python/requirements.txt
.venv/bin/python -m pip install -e python
mvn -B -ntp -f java/pom.xml verify
echo 'Preparación terminada. Ejecuta: bash scripts/ejecutar.sh'
