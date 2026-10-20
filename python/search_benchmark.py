#!/usr/bin/env python3
"""
Harness del Punto 2 (Python). Equivalente a SearchBenchmark.java.

Escenarios:
  mixed  : las 1.000 claves de data/keys_n.txt (500 presentes + 500 ausentes), cada una una vez.
  start  : 1.000 busquedas de la clave ubicada al inicio  (asc[0]).
  center : 1.000 busquedas de la clave ubicada al centro  (asc[n/2]).
  end    : 1.000 busquedas de la clave ubicada al final   (asc[n-1]).

Se cronometra el tiempo TOTAL de las 1.000 busquedas (time.perf_counter_ns) y se reporta el tiempo
promedio POR BUSQUEDA (total / 1.000). 5 repeticiones: promedio y desviacion estandar muestral.
Los datos se cargan antes de medir; la verificacion se hace fuera del tiempo. CPython no tiene JIT,
por eso no hay ejecucion de calentamiento.

Uso (desde la raiz del proyecto):
  python python/search_benchmark.py [--data data] [--out results/python_search.csv]
         [--sizes 1000,10000,100000,1000000] [--algs BinarySearch,JumpSearch]
"""
import argparse
import bisect
import csv
import os
import statistics
import time

import searches

REPS = 5
NKEYS = 1000
LANG = "Python"
SCENARIOS = ["mixed", "start", "center", "end"]
ALGOS = [
    ("LinearSearch", searches.linear),
    ("BinarySearch", searches.binary),
    ("TernarySearch", searches.ternary),
    ("JumpSearch", searches.jump),
    ("InterpolationSearch", searches.interpolation),
    ("ExponentialSearch", searches.exponential),
]


def read_ints(path):
    with open(path) as f:
        return [int(line) for line in f if line.strip()]


def keys_for(sc, arr, mixed):
    if sc == "mixed":
        return mixed
    key = {"start": arr[0], "center": arr[len(arr) // 2], "end": arr[-1]}[sc]
    return [key] * NKEYS


def verify(name, arr, keys, present, res):
    for k, p, r in zip(keys, present, res):
        ok = (r >= 0 and arr[r] == k) if p else r == -1
        if not ok:
            raise RuntimeError(f"Resultado incorrecto en {name}: clave={k} res={r}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data")
    ap.add_argument("--out", default="results/python_search.csv")
    ap.add_argument("--sizes", default="1000,10000,100000,1000000")
    ap.add_argument("--algs", default="")
    args = ap.parse_args()

    sizes = sorted(int(s) for s in args.sizes.split(","))
    wanted = set(args.algs.split(",")) if args.algs else set()
    algos = [a for a in ALGOS if not wanted or a[0] in wanted]

    arrays = {n: read_ints(os.path.join(args.data, f"asc_{n}.txt")) for n in sizes}
    keys_file = {n: read_ints(os.path.join(args.data, f"keys_{n}.txt")) for n in sizes}
    print("Datos cargados.")

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["algorithm", "language", "scenario", "n"]
                   + [f"rep{r}_ns_per_search" for r in range(1, REPS + 1)]
                   + ["mean_ns_per_search", "std_ns_per_search", "status", "note"])
        for name, fn in algos:
            for sc in SCENARIOS:
                for n in sizes:
                    arr = arrays[n]
                    keys = keys_for(sc, arr, keys_file[n])
                    present = [bisect.bisect_left(arr, k) < len(arr) and arr[bisect.bisect_left(arr, k)] == k
                               for k in keys]
                    times = []
                    for _ in range(REPS):
                        res = [0] * len(keys)
                        s = time.perf_counter_ns()
                        for i in range(len(keys)):
                            res[i] = fn(arr, keys[i])
                        e = time.perf_counter_ns()
                        times.append((e - s) / len(keys))          # ns por busqueda
                        verify(name, arr, keys, present, res)      # fuera del tiempo
                    mean, std = statistics.mean(times), statistics.stdev(times)
                    w.writerow([name, LANG, sc, n] + [f"{t:.2f}" for t in times]
                               + [f"{mean:.2f}", f"{std:.2f}", "measured", ""])
                    f.flush()
                    print(f"{name:<20} {sc:<7} n={n:<8} {mean:>14.1f} ns/busqueda")
    print(f"Listo. Resultados en {args.out}")


if __name__ == "__main__":
    main()
