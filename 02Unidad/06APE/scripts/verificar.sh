#!/usr/bin/env bash
set -euo pipefail
APE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
source "$APE_DIR/scripts/entorno_java.sh"
mkdir -p "$APE_DIR/resultados/revision"
JAVA_HOME="$APE_JDK" mvn -B -ntp -f "$APE_DIR/java/pom.xml" verify 2>&1 | tee "$APE_DIR/resultados/revision/maven.log"
cd "$APE_DIR/python"
.venv/bin/python -m pytest -q 2>&1 | tee "$APE_DIR/resultados/revision/pytest.log"
cd "$APE_DIR"
python/.venv/bin/python -m ape06.controlador.entrega 2>&1 | tee "$APE_DIR/resultados/revision/comparacion.log"
