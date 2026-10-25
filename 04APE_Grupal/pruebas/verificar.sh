#!/usr/bin/env bash
set -euo pipefail
proyecto_qa="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd -- "$proyecto_qa"
mkdir -p build
mapfile -d '' fuentes_qa < <(find src -name '*.java' -print0)
javac --release 17 -encoding UTF-8 -Xlint:all -d build "${fuentes_qa[@]}"
jar --create --file sir.jar --main-class sir.Main -C build sir/Main.class -C build sir/Opciones.class -C build sir/LanzadorNetLogo.class -C build sir/model -C build sir/controller -C build sir/io -C build sir/view
javac --release 17 -encoding UTF-8 -cp build -d build pruebas/PruebasQA.java pruebas/PruebasInterfaz.java
if [[ $# -eq 0 ]]; then
  java -cp build sir.pruebas.PruebasQA "$proyecto_qa"
  exit 0
fi
netlogo_qa="$(cd -- "$1" && pwd)"
if [[ ! -f "$netlogo_qa/lib/app/netlogo-7.0.4.jar" ]]; then
  printf '%s\n' 'No se encontro NetLogo 7.0.4 en esa carpeta.' >&2
  exit 1
fi
java -Dnetlogo.extensions.dir="$netlogo_qa/extensions" -cp "$proyecto_qa/build:$netlogo_qa/lib/app/*" sir.pruebas.PruebasQA "$proyecto_qa" netlogo
if [[ "${2:-}" == "--interfaz" ]]; then
  cd -- "$proyecto_qa/netlogo"
  java --add-exports=java.desktop/sun.awt=ALL-UNNAMED --add-exports=java.desktop/sun.java2d=ALL-UNNAMED -Dnetlogo.extensions.dir="$netlogo_qa/extensions" -cp "$proyecto_qa/build:$netlogo_qa/lib/app/*" sir.pruebas.PruebasInterfaz "$proyecto_qa"
fi
