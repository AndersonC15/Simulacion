# Pruebas independientes de APE04

Desde la raíz del proyecto:

```bash
bash pruebas.sh
bash pruebas_netlogo.sh "/ruta/real/NetLogo 7.0.4"
```

`PruebasSIR.java` verifica conservación, estados iniciales, semillas de
referencia, casos extremos, validación de parámetros y contrato CSV. Usa
aserciones propias sin JUnit y escribe el CSV de prueba en un temporal.

`PruebasNetLogo.java` usa la API `HeadlessWorkspace` de una instalación externa
NetLogo 7.0.4 para abrir el modelo, comparar exactamente ambos CSV y reproducir
las 101 filas. El script requiere `lib/app/netlogo-7.0.4.jar` y las extensiones.

Los scripts compilan en `out/` y `out-pruebas/`. Las pruebas se ejecutan como
programas Java; **`mvn test` no ejecuta estas pruebas**. Para conservar los
resultados existentes al validar también la aplicación, utiliza una copia
temporal del proyecto. Consulta `VALIDACION_MAVEN.md` para lo verificado en
esta actualización.
