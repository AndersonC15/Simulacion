# Pruebas de APE 04

La cobertura ejecutable está en `src/test/java/sir/pruebas/` y utiliza JUnit Jupiter. Los antiguos programas `PruebasQA` y `PruebasInterfaz` se migraron; no hay copias de las mismas clases en `pruebas/`.

Desde la raíz:

```bash
./mvnw clean verify
./mvnw -Pnetlogo -Dnetlogo.home="/ruta/NetLogo 7.0.4" verify
./mvnw -Pgui -Dnetlogo.home="/ruta/NetLogo 7.0.4" verify
```

`mvn test` descubre pruebas reales por responsabilidad. `verify` comprueba también el JAR empaquetado. La integración NetLogo y las pruebas GUI son perfiles separados y requieren la instalación externa. GUI necesita una pantalla. Un requisito ausente se informa como omisión; no equivale a una prueba aprobada.

Los casos comprueban regresiones de semillas, conservación de población, copia defensiva, límites y precisión, CLI, contratos CSV, identidades y transiciones, igualdad de conteos, protección y fallos parciales, concurrencia, empaquetado y rutas. Los perfiles externos comprueban el modelo NetLogo y el componente integrado, colores, separación A/B, reproducción y cierre.

Los informes actuales se generan en `target/surefire-reports/` y `target/failsafe-reports/`. `VALIDACION_MAVEN.md` recoge la ejecución de esta revisión. `RESULTADOS_QA.md` y `RESULTADOS_INTERFAZ.md` son evidencias históricas conservadas, no resultados de Maven de esta versión. Los casos usan directorios temporales y no sustituyen los CSV/PNG del usuario.
