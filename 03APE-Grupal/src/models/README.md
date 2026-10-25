# Modelo M/M/1

`m_model.py` define escenarios y objetos de resultados; `ModeloMM1` calcula
ρ, L, Lq, W y Wq y construye los tres escenarios. El código actual utiliza
λ=2.0, 2.5 y 2.99999 con μ=3.0. Las fórmulas estacionarias requieren
0 < λ < μ. La validación actual solo rechaza λ ≥ μ; no sustituye una
validación general de entradas. Aquí no se ejecutan procesos SimPy.
