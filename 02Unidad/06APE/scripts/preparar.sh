#!/usr/bin/env bash
set -euo pipefail
APE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
command -v python3 >/dev/null
command -v java >/dev/null
command -v mvn >/dev/null
python3 -c 'import sys; assert sys.version_info >= (3, 12), "Se requiere Python >= 3.12"'
python3 "$APE_DIR/scripts/instalar_jdk.py"
source "$APE_DIR/scripts/entorno_java.sh"
if [[ ! -x "$APE_DIR/python/.venv/bin/python" ]]; then
    python3 -m venv "$APE_DIR/python/.venv"
fi
"$APE_DIR/python/.venv/bin/python" -m pip install -r "$APE_DIR/python/requirements.txt"
"$APE_DIR/python/.venv/bin/python" -m pip install -e "$APE_DIR/python"
JAVA_HOME="$APE_JDK" mvn -B -ntp -f "$APE_DIR/java/pom.xml" verify
