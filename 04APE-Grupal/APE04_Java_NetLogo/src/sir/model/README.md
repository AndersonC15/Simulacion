# Modelo SIR

`ParametrosSIR` valida población, infectados iniciales, beta, gamma, horizonte
y contactos. `Estado` representa S/I/R e `Individuo` conserva el estado de
cada individuo. `SimulacionSIR` aplica los contactos y recuperaciones con
una copia de estados por paso; los recién infectados actúan desde el próximo
paso. `ResultadoPaso` conserva los conteos. Son reglas de Java, sin NetLogo
ni ventanas. Consulta `GUIA_CODIGO.md` en la raíz para el algoritmo completo.
