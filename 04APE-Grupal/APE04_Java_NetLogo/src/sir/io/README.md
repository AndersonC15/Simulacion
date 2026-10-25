# Exportación

`ExportadorResultados` es el contrato recibido por el controlador.
`ExportadorCsv` escribe UTF-8, crea los directorios de destino y utiliza el
encabezado `tiempo,susceptibles,infectados,recuperados`. El CSV es el puente
entre la simulación Java y el importador NetLogo. Volver a exportar a la misma
ruta reemplaza su contenido.
