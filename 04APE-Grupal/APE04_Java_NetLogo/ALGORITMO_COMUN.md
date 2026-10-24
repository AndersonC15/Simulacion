# Algoritmo comun Java y NetLogo

```text
N = 100
infectados_iniciales = 5
beta = 0.30
gamma = 0.10
contactos_por_infectado = 1
tiempo_maximo = 100

Crear N individuos susceptibles
Seleccionar aleatoriamente 5 individuos distintos y marcarlos infectados
Registrar [0, 95, 5, 0]

Para tiempo = 1 hasta 100:
    Copiar los estados actuales como estados_previos
    Para cada individuo, en orden de identificador:
        Si su estado_previo es INFECTADO:
            Repetir una vez:
                Seleccionar un indice aleatorio de toda la poblacion
                Si el estado_previo del contacto es SUSCEPTIBLE:
                    Si uniforme(0, 1) < beta:
                        Marcar contacto como INFECTADO
            Si uniforme(0, 1) < gamma:
                Marcar individuo como RECUPERADO
    Contar susceptibles, infectados y recuperados
    Verificar S + I + R = N
    Registrar [tiempo, S, I, R]

Guardar los 101 registros y representar S/I/R
```

La seleccion de contactos permite repetidos y seleccionar al propio individuo. La copia impide que un recien infectado actue en el mismo paso. Los recuperados no vuelven a ser susceptibles.

Java ejecuta este algoritmo y escribe los datos. NetLogo solo lee y representa las filas CSV; no implementa este algoritmo.
