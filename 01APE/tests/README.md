# Pruebas de APE01

Desde `01APE`, usando su entorno virtual:

```bash
python -m unittest discover -s tests -v
```

`test_modelo.py` contrasta fórmulas, categorías y precisión decimal;
`test_entradas.py` prueba captura, límites y salida; `test_mvc.py` comprueba
coordinación y separación; `test_graficas.py` genera PNG con Agg y comprueba
figuras y fallos de escritura. Pillow se utiliza para inspeccionar las imágenes.
La suite usa `unittest` de Python y no requiere pytest. Los casos con backends
simulados no constituyen una comprobación de ventanas reales.
