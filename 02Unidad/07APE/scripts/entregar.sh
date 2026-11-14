#!/usr/bin/env bash
set -euo pipefail
APE07_RAIZ="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$APE07_RAIZ"
export MPLCONFIGDIR="$APE07_RAIZ/.cache/matplotlib"
bash scripts/preparar.sh
bash scripts/ejecutar.sh
bash scripts/verificar.sh
.venv/bin/python scripts/generar_informe.py
.venv/bin/python scripts/generar_video.py
.venv/bin/python scripts/auditar_entrega.py
