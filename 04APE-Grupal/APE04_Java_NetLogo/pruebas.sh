#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
bash compilar.sh
mkdir -p out-pruebas
if command -v javac >/dev/null 2>&1; then
  javac -encoding UTF-8 --release 17 -cp out -d out-pruebas pruebas/PruebasSIR.java
else
  java -m jdk.compiler/com.sun.tools.javac.Main -encoding UTF-8 --release 17 -cp out -d out-pruebas pruebas/PruebasSIR.java
fi
java -cp 'out:out-pruebas' sir.pruebas.PruebasSIR
