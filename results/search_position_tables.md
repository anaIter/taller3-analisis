# Tiempo promedio por búsqueda según la posición de la clave (n = 1.000.000)


## Java

| Algoritmo | Inicio | Centro | Final |
|---|---:|---:|---:|
| LinearSearch | 2.7 ns | 179.5 µs | 287.3 µs |
| BinarySearch | 58.3 ns | 31.4 ns | 31.8 ns |
| TernarySearch | 33.7 ns | 34.0 ns | 35.5 ns |
| JumpSearch | 7.3 ns | 498.8 ns | 1.5 µs |
| InterpolationSearch | 5.3 ns | 15.9 ns | 5.9 ns |
| ExponentialSearch | 4.8 ns | 57.8 ns | 60.9 ns |

## Python

| Algoritmo | Inicio | Centro | Final |
|---|---:|---:|---:|
| LinearSearch | 351.1 ns | 20.67 ms | 41.94 ms |
| BinarySearch | 1.5 µs | 1.6 µs | 2.4 µs |
| TernarySearch | 3.1 µs | 2.3 µs | 2.0 µs |
| JumpSearch | 258.8 ns | 86.8 µs | 318.0 µs |
| InterpolationSearch | 330.2 ns | 1.5 µs | 442.6 ns |
| ExponentialSearch | 110.2 ns | 3.0 µs | 5.0 µs |
