# Taller 3 - Ordenamiento y Busqueda

Lenguajes: Java (compilado) y Python (interpretado).

## Estructura
- `src/`      implementaciones y harness de medicion en Java
- `python/`   implementaciones y harness de medicion en Python
- `data/`     datos de prueba (generados con semilla fija 42)
- `results/`  CSV con las mediciones
- `figures/`  graficas

## Reproducir
Desde la raiz del proyecto:

```
javac -d out src/DataGenerator.java
java -cp out DataGenerator data
```