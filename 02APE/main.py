"""Vista de consola de APE02; los siguientes avances incorporan estrategias."""
from Modelo.datos import DATOS_OFICIALES
from Modelo.parametros import Parametros
from Modelo.estrategias import Deterministico, Discreto, Estocastico, ContinuoEuler


def main():
    print("APE02: comparación de modelos poblacionales")
    print("Observaciones:", DATOS_OFICIALES)
    print("Configuración inicial:", Parametros())
    for modelo in (Deterministico(), Discreto(), Estocastico(), ContinuoEuler()):
        serie = modelo.simular(Parametros())
        print(serie.nombre, "población final:", serie.poblaciones[-1])


if __name__ == "__main__":
    main()
