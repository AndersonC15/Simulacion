#!/usr/bin/env bash
set -euo pipefail
RAIZ_APE05="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RAIZ_APE05"
.venv/bin/python -m unittest discover -s python/tests -v
mvn -B -ntp -f java/pom.xml verify
bash scripts/ejecutar.sh

