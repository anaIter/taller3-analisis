# Punto 3.2 — ¿Ordenar o no ordenar? (n = 1.000.000)

Condición: conviene ordenar si `T_sort + k·t_bin < k·t_lin`, es decir `k > T_sort / (t_lin − t_bin)`.


## Java

1. Mejor algoritmo de ordenamiento (n = 1.000.000, aleatoria): **RadixSort** → T_sort = 79.745 ms (± 20.430 ms; measured).
2. Búsqueda lineal sobre el arreglo desordenado (claves mixtas): t_lin = 256.255 µs por búsqueda.
3. Búsqueda binaria tras ordenar (claves mixtas): t_bin = 148.1 ns por búsqueda.
4. Diferencia por búsqueda: t_lin − t_bin = 256.106 µs.
5. k* = T_sort / (t_lin − t_bin) = 79,744,820 ns / 256,106 ns = **311.37**.
6. Resultado: ordenar conviene a partir de **k = 312** búsquedas.

Sensibilidad al ruido (± 1 desviación estándar en T_sort y t_lin): k* entre 175 y 575.

Sensibilidad a la posición de las claves (t_lin según el escenario de la búsqueda lineal):

| Escenario de la clave | t_lin | k* | k mínimo |
|---|---:|---:|---:|
| Mixtas (500 presentes + 500 ausentes) | 256.255 µs | 311.37 | 312 |
| Siempre en el centro | 179.468 µs | 444.42 | 445 |
| Siempre al final / ausentes | 287.313 µs | 277.58 | 278 |


## Python

1. Mejor algoritmo de ordenamiento (n = 1.000.000, aleatoria): **DualPivotQuickSort** → T_sort = 4.699 s (± 321.494 ms; measured).
2. Búsqueda lineal sobre el arreglo desordenado (claves mixtas): t_lin = 31.019 ms por búsqueda.
3. Búsqueda binaria tras ordenar (claves mixtas): t_bin = 3.727 µs por búsqueda.
4. Diferencia por búsqueda: t_lin − t_bin = 31.016 ms.
5. k* = T_sort / (t_lin − t_bin) = 4,699,294,420 ns / 31,015,725 ns = **151.51**.
6. Resultado: ordenar conviene a partir de **k = 152** búsquedas.

Sensibilidad al ruido (± 1 desviación estándar en T_sort y t_lin): k* entre 129 y 179.

Sensibilidad a la posición de las claves (t_lin según el escenario de la búsqueda lineal):

| Escenario de la clave | t_lin | k* | k mínimo |
|---|---:|---:|---:|
| Mixtas (500 presentes + 500 ausentes) | 31.019 ms | 151.51 | 152 |
| Siempre en el centro | 20.674 ms | 227.32 | 228 |
| Siempre al final / ausentes | 41.942 ms | 112.05 | 113 |

