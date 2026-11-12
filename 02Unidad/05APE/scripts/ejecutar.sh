#!/usr/bin/env bash
set -euo pipefail
RAIZ_APE05="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RAIZ_APE05"
if [[ ! -x .venv/bin/python || ! -f java/target/ape05-lcg-1.0.0.jar ]]; then
    echo "Primero ejecuta: bash scripts/preparar.sh" >&2
    exit 1
fi
# Recompila para que los resultados correspondan al código actual.
mvn -B -ntp -f java/pom.xml package -DskipTests
for semilla_ape05 in 12345 54321; do
    .venv/bin/python -m lcg_practica --semilla "$semilla_ape05" --salida resultados/python
    java -Djava.awt.headless=true -jar java/target/ape05-lcg-1.0.0.jar \
        --semilla "$semilla_ape05" --salida resultados/java
done
.venv/bin/python scripts/comparar.py

