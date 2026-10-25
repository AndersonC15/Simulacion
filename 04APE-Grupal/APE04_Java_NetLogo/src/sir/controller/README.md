# Controlador SIR

`ControladorSIR` coordina simulación, tabla, resumen, exportación CSV y PNG.
Recibe el modelo, la vista y un `ExportadorResultados`, además de las rutas
y la opción de ventana. Los valores por defecto apuntan a `netlogo/` y
`resultados/` respecto al directorio de ejecución. No se inicia NetLogo desde
esta clase; el modelo NetLogo importa el CSV posteriormente.
