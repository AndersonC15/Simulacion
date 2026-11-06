#!/usr/bin/env bash
# Archivo compartido por los lanzadores; no cambia la configuracion global del equipo.
APE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
APE_RELEASE="$(python3 - "$APE_DIR/java/pom.xml" <<'PY'
import sys
import xml.etree.ElementTree as ET
ns = {'m': 'http://maven.apache.org/POM/4.0.0'}
print(ET.parse(sys.argv[1]).findtext('m:properties/m:maven.compiler.release', namespaces=ns))
PY
)"
if [[ -z "${APE_JDK:-}" ]]; then
    if [[ -x "$APE_DIR/.tools/jdk-$APE_RELEASE/bin/javac" ]]; then
        APE_JDK="$APE_DIR/.tools/jdk-$APE_RELEASE"
    elif [[ -x "/usr/lib/jvm/java-$APE_RELEASE-openjdk-amd64/bin/javac" ]]; then
        APE_JDK="/usr/lib/jvm/java-$APE_RELEASE-openjdk-amd64"
    else
        APE_JDK="$(dirname -- "$(dirname -- "$(readlink -f -- "$(command -v javac)")")")"
    fi
fi
APE_JAVA="$APE_JDK/bin/java"
if [[ ! -x "$APE_JAVA" || ! -x "$APE_JDK/bin/javac" ]]; then
    echo "Falta un JDK compatible con release=$APE_RELEASE. Ejecuta preparar.sh o define APE_JDK." >&2
    exit 2
fi
APE_JAVAC_VERSION="$("$APE_JDK/bin/javac" -version 2>&1)"
python3 - "$APE_JAVAC_VERSION" "$APE_RELEASE" <<'PY'
import re
import sys
version = re.search(r'javac (\d+)', sys.argv[1])
if version is None or int(version.group(1)) < int(sys.argv[2]):
    sys.exit('El JDK seleccionado no admite la version requerida por pom.xml.')
PY
export APE_JAVA
