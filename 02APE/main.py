"""Vista de consola de APE02; los siguientes avances incorporan estrategias."""
from Modelo.datos import DATOS_OFICIALES
from Modelo.parametros import Parametros
from Modelo.estrategias import Deterministico


def main():
    print("APE02: comparación de modelos poblacionales")
    print("Observaciones:", DATOS_OFICIALES)
    print("Configuración inicial:", Parametros())
    print("Exponencial:", Deterministico().simular(Parametros()).poblaciones)


if __name__ == "__main__":
    main()
