"""Vista de consola de APE02; los siguientes avances incorporan estrategias."""
from Modelo.datos import DATOS_OFICIALES
from Modelo.parametros import Parametros


def main():
    print("APE02: comparación de modelos poblacionales")
    print("Observaciones:", DATOS_OFICIALES)
    print("Configuración inicial:", Parametros())


if __name__ == "__main__":
    main()
