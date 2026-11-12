#!/usr/bin/env bash
set -euo pipefail
RAIZ_APE05="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RAIZ_APE05"
for herramienta in python3 java javac mvn; do
    if ! command -v "$herramienta" >/dev/null 2>&1; then
        echo "Falta $herramienta. Consulta los requisitos del README." >&2
        exit 1
    fi
done
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else "Se requiere Python 3.11 o superior.")'
if [[ ! -x .venv/bin/python ]]; then
    python3 -m venv .venv
fi
.venv/bin/python -m pip install -r python/requirements.txt
.venv/bin/python -m pip install --no-deps -e ./python
mvn -B -ntp -f java/pom.xml verify
echo "Entorno preparado. Ejecuta: bash scripts/ejecutar.sh"

