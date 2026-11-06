"""Simulación M/M/1 con SimPy — arquitectura MVC."""

from src.controllers.m_controller import simular_escenario
from src.models.m_model import ModeloMM1
from src.views.m_view import mostrar_resultados


def main() -> None:
    escenarios = ModeloMM1.construir_escenarios()

    print("Ejecutando simulaciones M/M/1 con SimPy...")
    print("Tiempo de simulación: 20000 unidades\n")

    resultados = []
    for esc in escenarios:
        if not esc.es_estable:
            print(f"Escenario λ={esc.lam}, μ={esc.mu}: el sistema no es estable")
            continue
        print(f"Simulando escenario λ={esc.lam}, μ={esc.mu} "
              f"({esc.condicion})...")
        resultados.append(simular_escenario(esc))

    mostrar_resultados(resultados)


if __name__ == "__main__":
    main()
