#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
bash compilar.sh
mkdir -p resultados
java -cp out sir.Main "$@" | tee resultados/ultima_ejecucion_java.txt
