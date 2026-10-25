# Gráficas de APE01

La opción 3 de `main.py` genera `variables_modelo.png` y
`comparacion_modelos.png` en esta carpeta. Son representaciones de los datos y
resultados calculados en `Modelo`; los cálculos no leen los PNG. Ejecutar de
nuevo reemplaza las imágenes. Para generar sin abrir ventanas, desde `01APE`:

```bash
printf '3\n0\n' | MPLBACKEND=Agg python main.py
```
