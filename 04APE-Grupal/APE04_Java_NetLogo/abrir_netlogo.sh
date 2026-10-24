#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
modelo="$PWD/netlogo/modelo_sir_netlogo.nlogox"
if command -v netlogo >/dev/null 2>&1; then
  exec netlogo "$modelo"
elif command -v NetLogo >/dev/null 2>&1; then
  exec NetLogo "$modelo"
else
  printf 'Abre NetLogo y selecciona Archivo > Abrir > %s\n' "$modelo"
  exit 1
fi
