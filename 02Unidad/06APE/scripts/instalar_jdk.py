#!/usr/bin/env python3
"""Usa un JDK compatible o prepara Temurin localmente desde la API oficial de Adoptium."""

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
import tempfile
import xml.etree.ElementTree as ET


def version_compilador(directorio: Path) -> int:
    compilador = directorio / "bin/javac"
    if not compilador.is_file():
        return 0
    resultado = subprocess.run([str(compilador), "-version"], capture_output=True, text=True)
    coincidencia = re.search(r"javac (\d+)", resultado.stdout + resultado.stderr)
    return int(coincidencia.group(1)) if coincidencia and resultado.returncode == 0 else 0


def main() -> None:
    base = Path(__file__).resolve().parents[1]
    ns = {"m": "http://maven.apache.org/POM/4.0.0"}
    release = int(ET.parse(base / "java/pom.xml").findtext("m:properties/m:maven.compiler.release", namespaces=ns))
    local = base / f".tools/jdk-{release}"
    if "APE_JDK" in os.environ:
        if version_compilador(Path(os.environ["APE_JDK"])) < release:
            raise SystemExit("APE_JDK no contiene un compilador compatible con pom.xml.")
        return
    candidatos = [local, Path(f"/usr/lib/jvm/java-{release}-openjdk-amd64")]
    javac = shutil.which("javac")
    if javac:
        candidatos.append(Path(javac).resolve().parents[1])
    if any(version_compilador(candidato) >= release for candidato in candidatos):
        return
    if os.uname().sysname != "Linux" or os.uname().machine != "x86_64":
        raise SystemExit("Instala el JDK requerido o define APE_JDK. La descarga automatica cubre Linux x86_64.")
    api = f"https://api.adoptium.net/v3/assets/latest/{release}/hotspot?architecture=x64&image_type=jdk&os=linux"
    if not shutil.which("curl"):
        raise SystemExit("Se necesita curl para descargar el JDK, o define APE_JDK con un JDK instalado.")
    activo = json.loads(subprocess.check_output(["curl", "-fsSL", "--retry", "3", api], text=True))[0]
    paquete = activo["binary"]["package"]
    herramientas = base / ".tools"
    herramientas.mkdir(exist_ok=True)
    print(f"Preparando JDK {activo['version']['semver']} local en {local}", flush=True)
    with tempfile.TemporaryDirectory(prefix="jdk-descarga-", dir=herramientas) as temporal:
        archivo = Path(temporal) / "jdk.tar.gz"
        sha = hashlib.sha256()
        subprocess.run(["curl", "-fL", "--retry", "3", "--connect-timeout", "30", "--output", str(archivo), paquete["link"]], check=True)
        with archivo.open("rb") as origen:
            while bloque := origen.read(1024*1024):
                sha.update(bloque)
        if sha.hexdigest() != paquete["checksum"]:
            raise SystemExit("La descarga del JDK no coincide con su SHA-256 publicado.")
        extraido = Path(temporal) / "extraido"
        extraido.mkdir()
        with tarfile.open(archivo) as tar:
            tar.extractall(extraido, filter="data")
        raices = [p for p in extraido.iterdir() if p.is_dir()]
        if len(raices) != 1 or version_compilador(raices[0]) < release:
            raise SystemExit("El archivo descargado no contiene el JDK esperado.")
        raices[0].rename(local)
    (herramientas / f"jdk-{release}-origen.json").write_text(json.dumps({
        "proveedor": "Eclipse Temurin / Adoptium", "version": activo["version"]["semver"],
        "api": api, "url": paquete["link"], "sha256": paquete["checksum"],
    }, indent=2) + "\n", encoding="utf-8")
    print("JDK local instalado; no se modifico el Java predeterminado del sistema.")


if __name__ == "__main__":
    main()
