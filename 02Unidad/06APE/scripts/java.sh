#!/usr/bin/env bash
set -euo pipefail
source "$(dirname -- "${BASH_SOURCE[0]}")/entorno_java.sh"
if [[ ! -f "$APE_DIR/java/target/ape06.jar" ]]; then
    echo 'Primero ejecuta ./scripts/preparar.sh' >&2
    exit 2
fi
cd "$APE_DIR"
exec "$APE_JAVA" -jar "$APE_DIR/java/target/ape06.jar" "$@"
