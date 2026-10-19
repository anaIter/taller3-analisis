#!/usr/bin/env python3
"""
Harness del Punto 1 (Python). Equivalente a SortBenchmark.java.

Reglas aplicadas:
  - Los datos se leen de data/ ANTES de medir (la lectura no se cronometra).
  - Cada repeticion corre sobre una copia nueva (la copia no se cronometra).
  - Se cronometra solo el algoritmo con time.perf_counter_ns().
  - Tras cada ejecucion, fuera del tiempo, se verifica que el resultado sea igual al arreglo ascendente.
  - 5 repeticiones: promedio y desviacion estandar muestral.
  - Python no tiene compilacion JIT (CPython), por eso no hay ejecucion de calentamiento.
  - Si el tiempo previsto por ejecucion supera el limite (300 s), NO se ejecuta: se extrapola
    desde el tamano anterior con la complejidad teorica y se marca "estimated".
  - Si hay RecursionError (limite de recursion) se documenta en la nota del CSV y se estima.

Uso (desde la raiz del proyecto):
  python python/sort_benchmark.py [--data data] [--out results/python_sorting.csv]
         [--sizes 1000,10000,100000,1000000] [--algs InsertionSort,MergeSort]
         [--inputs random,asc,desc] [--limit 300] [--resume] [--recursion 1100000] [--stack 512]
  --recursion = limite de recursion de Python (por defecto de Python: 1000).
  --stack     = tamano de pila (MB) del hilo donde corre el benchmark.
  --resume    = conserva las filas ya existentes del CSV y agrega solo lo que falta.
"""
import argparse
import csv
import math
import os
import statistics
import sys
import threading
import time

import sorts

REPS = 5
LANG = "Python"

# (nombre, funcion, crecimiento con random, con asc, con desc)
ALGOS = [
    ("InsertionSort", sorts.insertion_sort, "QUAD", "LINEAR", "QUAD"),
    ("DualPivotQuickSort", sorts.dual_pivot_quicksort, "NLOGN", "QUAD", "QUAD"),
    ("MergeSort", sorts.merge_sort, "NLOGN", "NLOGN", "NLOGN"),
    ("HeapSort", sorts.heap_sort, "NLOGN", "NLOGN", "NLOGN"),
    ("RadixSort", sorts.radix_sort, "LINEAR", "LINEAR", "LINEAR"),
    ("BucketSort", sorts.bucket_sort, "LINEAR", "LINEAR", "N15"),
]
GROWTH_IDX = {"random": 2, "asc": 3, "desc": 4}


def predict(prev_mean, prev_n, n, growth):
    ratio = n / prev_n
    if growth == "LINEAR":
        return prev_mean * ratio
    if growth == "NLOGN":
        return prev_mean * ratio * (math.log(n) / math.log(prev_n))
    if growth == "N15":
        return prev_mean * ratio ** 1.5
    return prev_mean * ratio * ratio   # QUAD


def read_ints(path):
    with open(path) as f:
        return [int(line) for line in f if line.strip()]


def measure(fn, original, expected):
    times = []
    for _ in range(REPS):
        copy = original[:]                      # copia fuera del tiempo
        s = time.perf_counter_ns()
        fn(copy)
        e = time.perf_counter_ns()
        times.append(e - s)
        if copy != expected:                    # verificacion fuera del tiempo
            raise RuntimeError("Resultado incorrecto")
    return times


def fmt_row(alg, inp, n, times, mean, std, status, note):
    reps = [str(t) for t in times] if times else [""] * REPS
    mean_s = "" if mean is None or math.isnan(mean) else f"{mean:.1f}"
    std_s = "" if std is None else f"{std:.1f}"
    return [alg, LANG, inp, str(n)] + reps + [mean_s, std_s, status, note]


def run(args):
    sizes = sorted(int(s) for s in args.sizes.split(","))
    inputs = args.inputs.split(",")
    alg_filter = set(args.algs.split(",")) if args.algs else set()
    algos = [a for a in ALGOS if not alg_filter or a[0] in alg_filter]
    limit_ns = args.limit * 1e9
    sys.setrecursionlimit(args.recursion)

    # 1) Cargar los datos antes de medir
    data = {}
    for n in sizes:
        for inp in set(inputs) | {"asc"}:
            data[(inp, n)] = read_ints(os.path.join(args.data, f"{inp}_{n}.txt"))
    print("Datos cargados.")

    # 2) Reanudacion
    done = {}
    exists = args.resume and os.path.exists(args.out) and os.path.getsize(args.out) > 0
    if exists:
        with open(args.out, newline="", encoding="utf-8") as f:
            rd = csv.reader(f)
            next(rd, None)
            for row in rd:
                if len(row) >= 5 + REPS:
                    m = row[4 + REPS]
                    done[(row[0], row[2], row[3])] = float(m) if m else float("nan")
        print(f"Reanudando: {len(done)} filas ya existentes se conservan.")

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "a" if exists else "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        if not exists:
            w.writerow(["algorithm", "language", "input", "n"]
                       + [f"rep{r}_ns" for r in range(1, REPS + 1)]
                       + ["mean_ns", "std_ns", "status", "note"])
        for name, fn, *_ in algos:
            alg = next(a for a in ALGOS if a[0] == name)
            for inp in inputs:
                growth = alg[GROWTH_IDX[inp]]
                prev_n, prev_mean = None, float("nan")
                for n in sizes:
                    key = (name, inp, str(n))
                    if key in done:
                        print(f"{name:<20} {inp:<7} n={n:<8} (ya existe, se omite)")
                        if not math.isnan(done[key]):
                            prev_n, prev_mean = n, done[key]
                        continue
                    pred = float("nan") if prev_n is None else predict(prev_mean, prev_n, n, growth)
                    mean_for_next = float("nan")
                    if not math.isnan(pred) and pred > limit_ns:
                        row = fmt_row(name, inp, n, None, pred, None, "estimated",
                                      f"No se ejecuto: tiempo previsto > {args.limit:g} s; extrapolado desde n={prev_n}")
                        mean_for_next = pred
                    else:
                        try:
                            t = measure(fn, data[(inp, n)], data[("asc", n)])
                            mean = statistics.mean(t)
                            std = statistics.stdev(t)
                            row = fmt_row(name, inp, n, t, mean, std, "measured", "")
                            mean_for_next = mean
                        except RecursionError:
                            row = fmt_row(name, inp, n, None, pred, None, "estimated",
                                          f"RecursionError (limite de recursion = {args.recursion}); tiempo estimado por extrapolacion")
                            mean_for_next = pred
                            print(f"  !! RecursionError en {name} {inp} n={n}")
                    w.writerow(row)
                    f.flush()
                    m = row[4 + REPS]
                    ms = float(m) / 1e6 if m else float("nan")
                    print(f"{name:<20} {inp:<7} n={n:<8} {ms:>14.3f} ms  [{row[6 + REPS]}]")
                    if not math.isnan(mean_for_next):
                        prev_n, prev_mean = n, mean_for_next
    print(f"Listo. Resultados en {args.out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data")
    ap.add_argument("--out", default="results/python_sorting.csv")
    ap.add_argument("--sizes", default="1000,10000,100000,1000000")
    ap.add_argument("--algs", default="")
    ap.add_argument("--inputs", default="random,asc,desc")
    ap.add_argument("--limit", type=float, default=300.0, help="segundos por ejecucion para estimar")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--recursion", type=int, default=1_100_000)
    ap.add_argument("--stack", type=int, default=512, help="MB de pila del hilo")
    args = ap.parse_args()

    threading.stack_size(args.stack * 1024 * 1024)
    t = threading.Thread(target=run, args=(args,))
    t.start()
    t.join()


if __name__ == "__main__":
    main()
