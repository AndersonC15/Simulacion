#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
if [[ $# -ne 1 ]]; then printf 'Uso: bash pruebas_netlogo.sh "/ruta/NetLogo 7.0.4"\n'; exit 1; fi
netlogo_dir="$(cd -- "$1" && pwd)"
netlogo_jar="$netlogo_dir/lib/app/netlogo-7.0.4.jar"
mkdir -p out-pruebas
if command -v javac >/dev/null 2>&1; then
 javac -encoding UTF-8 --release 17 -cp "$netlogo_jar" -d out-pruebas pruebas/PruebasNetLogo.java
else
 java -m jdk.compiler/com.sun.tools.javac.Main -encoding UTF-8 --release 17 -cp "$netlogo_jar" -d out-pruebas pruebas/PruebasNetLogo.java
fi
java -Xmx1g -Djava.awt.headless=true "-Dnetlogo.extensions.dir=$netlogo_dir/extensions" -cp "out-pruebas:$netlogo_dir/lib/app/*" sir.pruebas.PruebasNetLogo "$PWD"
