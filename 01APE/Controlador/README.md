# Controlador

`ControladorLluvia` recibe por su constructor un modelo, una vista de consola,
una operación de generación gráfica y los registros. Coordina las cinco
opciones del menú sin implementar fórmulas ni dibujar.

Solicita las tablas y el caso manual al modelo y entrega sus resultados a la
vista. Maneja EOF y Ctrl+C para salir limpiamente. Si fallan directorios,
escritura o inicio gráfico, informa del problema y permite continuar; anuncia
éxito solamente cuando recibe la entrega de ambas imágenes.

La inyección permite probar la coordinación con entradas y salidas simuladas
sin añadir jerarquías o interfaces vacías. `main.py` construye y conecta los
objetos y llama a `ejecutar`.
