#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
mkdir -p out
fuentes=(src/sir/Main.java src/sir/model/*.java src/sir/view/*.java src/sir/controller/*.java src/sir/io/*.java)
if command -v javac >/dev/null 2>&1; then
  javac -encoding UTF-8 --release 17 -Xlint:all -d out "${fuentes[@]}"
else
  # Algunos entornos incluyen el compilador como modulo, sin el ejecutable javac.
  java -m jdk.compiler/com.sun.tools.javac.Main -encoding UTF-8 --release 17 -Xlint:all -d out "${fuentes[@]}"
fi
printf 'Compilacion terminada. Compatible con Java 17 y 21.\n'
