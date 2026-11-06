#!/usr/bin/env bash
set -euo pipefail
proyecto_qa="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd -- "$proyecto_qa"
if [[ $# -eq 0 ]]; then
  exec ./mvnw clean verify
fi
if [[ $# -gt 2 || ( $# -eq 2 && "$2" != "--interfaz" ) ]]; then
  printf '%s\n' 'Uso: verificar.sh ["/ruta/NetLogo 7.0.4" [--interfaz]]' >&2
  exit 1
fi
netlogo_qa="$(cd -- "$1" && pwd)"
if [[ ! -f "$netlogo_qa/lib/app/netlogo-7.0.4.jar" ]]; then
  printf '%s\n' 'No se encontró NetLogo 7.0.4 en esa carpeta.' >&2
  exit 1
fi
./mvnw -Pnetlogo "-Dnetlogo.home=$netlogo_qa" verify
if [[ "${2:-}" == "--interfaz" ]]; then
  ./mvnw -Pgui "-Dnetlogo.home=$netlogo_qa" verify
fi
