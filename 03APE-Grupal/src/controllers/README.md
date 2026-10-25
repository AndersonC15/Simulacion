# Simulación de APE03

`m_controller.py` crea `simpy.Environment` y un servidor
`simpy.Resource(capacity=1)`, genera llegadas y servicios exponenciales con
`random`, registra eventos y calcula las estimaciones. El horizonte programado
es 20000 y la semilla 42 se reinicia en cada escenario. El README principal
explica las limitaciones de W, L, ocupación, registro de la cola y ausencia de
calentamiento. Esta actualización documental conserva esos algoritmos.
