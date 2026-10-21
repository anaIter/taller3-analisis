# Taller 3 - Ordenamiento y Busqueda

Comparacion experimental de algoritmos de ordenamiento y busqueda en **Java** (compilado) y **Python** (interpretado).

- Ordenamiento: Insertion Sort, Dual-Pivot QuickSort, Merge Sort, Heap Sort, Radix Sort, Bucket Sort.
- Busqueda: lineal, binaria, ternaria, por saltos, por interpolacion, exponencial.
- Tamanos: 1.000, 10.000, 100.000 y 1.000.000 enteros aleatorios de 8 digitos (semilla fija 42).

Integrantes: _completar_

## Estructura

| Carpeta / archivo | Contenido |
|---|---|
| `src/` | Codigo Java: `DataGenerator`, `Sorts`, `SortBenchmark`, `Searches`, `SearchBenchmark` |
| `python/` | Codigo Python: `sorts.py`, `sort_benchmark.py`, `searches.py`, `search_benchmark.py`, `make_figures.py`, `make_search_figures.py`, `break_even.py` |
| `data/` | Datos de prueba (`random_n`, `asc_n`, `desc_n`, `keys_n`). Los de n = 1.000.000 no se suben: se regeneran con `DataGenerator` |
| `results/` | CSV con todas las mediciones, tablas de posicion de la clave, factores de crecimiento y calculo del punto de equilibrio |
| `figures/` | Graficas del informe |
| `requirements.txt` | Dependencias de Python (solo `matplotlib`) |

## Requisitos

- JDK 17 o superior (probado con Amazon Corretto 21).
- Python 3.10 o superior (probado con 3.11.9) y `pip install -r requirements.txt`.

## Como reproducir los resultados

Todos los comandos se ejecutan desde la raiz del proyecto. En IntelliJ IDEA, las clases Java se pueden ejecutar con el triangulo verde junto a `main`; los argumentos se escriben en *Run > Edit Configurations > Program arguments*.

**1. Generar los datos** (una sola vez; tarda pocos segundos)
```
javac -d out src/DataGenerator.java
java -cp out DataGenerator data
```

**2. Mediciones en Java**
```
javac -d out src/*.java
java -cp out SortBenchmark            # -> results/java_sorting.csv
java -cp out SearchBenchmark          # -> results/java_search.csv
```
Opciones de `SortBenchmark`: `--sizes=1000,10000`, `--algs=MergeSort,HeapSort`, `--inputs=random,asc`, `--limit=300` (segundos por ejecucion a partir de los cuales se estima), `--resume=true` (continua un CSV existente), `--stack=512` (pila en MB). Demostracion del `StackOverflowError`: `--sizes=10000,100000 --stack=1 --out=results/java_stackoverflow_demo.csv`.

**3. Mediciones en Python**
```
python python/sort_benchmark.py       # -> results/python_sorting.csv
python python/search_benchmark.py     # -> results/python_search.csv
```
Opciones de `sort_benchmark.py`: `--sizes`, `--algs`, `--inputs`, `--limit`, `--resume`, `--recursion`, `--stack`. Demostracion del `RecursionError`: `--algs DualPivotQuickSort --inputs asc --sizes 1000,10000 --recursion 1000 --out results/python_recursion_demo.csv`.

**4. Graficas, tablas y calculo del Punto 3.2**
```
python python/make_figures.py          # graficas de ordenamiento + results/growth_factors.csv
python python/make_search_figures.py   # graficas de busqueda + tablas de posicion de la clave
python python/break_even.py            # punto de equilibrio: results/break_even.md y figures/break_even.png
```

## Metodologia de medicion

- Solo se cronometra el algoritmo (`System.nanoTime()` en Java, `time.perf_counter_ns()` en Python); la lectura de archivos, la copia del arreglo y la verificacion quedan fuera.
- 5 repeticiones por medicion; se reportan promedio y desviacion estandar muestral. Calentamiento del JIT en Java.
- Cada repeticion de ordenamiento usa una copia nueva del arreglo y se verifica contra el arreglo ascendente de referencia.
- Si el tiempo previsto por ejecucion supera 300 s, el caso no se ejecuta: se extrapola desde el tamano anterior con la complejidad teorica y se marca como `estimated`.
- Formato de los CSV: algoritmo, lenguaje, entrada (o escenario), n, tiempo de cada repeticion, promedio, desviacion estandar, estado (`measured` / `estimated`) y nota.

## Equipo de medicion

Las mediciones se hicieron en: _completar CPU, RAM y sistema operativo_.
