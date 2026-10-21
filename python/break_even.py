#!/usr/bin/env python3
"""
Punto 3.2 - ¿Ordenar o no ordenar?

Dado un arreglo DESORDENADO de n = 1.000.000 elementos y k busquedas:
  Opcion A: k busquedas lineales sobre el arreglo desordenado     -> T_A(k) = k * t_lin
  Opcion B: ordenar una vez (mejor algoritmo medido) + k binarias -> T_B(k) = T_sort + k * t_bin
Conviene ordenar cuando T_B(k) < T_A(k)  <=>  k > T_sort / (t_lin - t_bin)

Datos (todos de las mediciones propias, n = 1.000.000):
  T_sort : menor tiempo medio entre los 6 algoritmos, entrada aleatoria (results/*_sorting.csv)
  t_lin, t_bin : tiempo medio por busqueda con las 1.000 claves mixtas (results/*_search.csv)

Salidas: results/break_even.md, results/break_even.csv, figures/break_even.png
Uso (raiz del proyecto): python python/break_even.py
"""
import csv
import math
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

N = 1_000_000


def fmt(ns):
    if ns >= 1e9:
        return f"{ns / 1e9:.3f} s"
    if ns >= 1e6:
        return f"{ns / 1e6:.3f} ms"
    if ns >= 1e3:
        return f"{ns / 1e3:.3f} \u00b5s"
    return f"{ns:.1f} ns"


def best_sort(path):
    best = None
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["input"] == "random" and int(r["n"]) == N and r["mean_ns"]:
                t = (float(r["mean_ns"]), float(r["std_ns"]) if r["std_ns"] else 0.0, r["algorithm"], r["status"])
                if best is None or t[0] < best[0]:
                    best = t
    return best


def search_times(path):
    d = {}
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if int(r["n"]) == N:
                d[(r["algorithm"], r["scenario"])] = (float(r["mean_ns_per_search"]), float(r["std_ns_per_search"]))
    return d


def k_min(T, t_lin, t_bin):
    """Menor k entero tal que k*t_lin > T + k*t_bin (None si nunca conviene)."""
    diff = t_lin - t_bin
    if diff <= 0:
        return None, None
    ks = T / diff
    return ks, math.floor(ks) + 1


def main():
    rows_csv, md = [], ["# Punto 3.2 \u2014 \u00bfOrdenar o no ordenar? (n = 1.000.000)\n",
                        "Condici\u00f3n: conviene ordenar si `T_sort + k\u00b7t_bin < k\u00b7t_lin`, es decir "
                        "`k > T_sort / (t_lin \u2212 t_bin)`.\n"]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
    for ax, lang in zip(axes, ("Java", "Python")):
        T, sT, alg, status = best_sort(f"results/{lang.lower()}_sorting.csv")
        s = search_times(f"results/{lang.lower()}_search.csv")
        t_lin, s_lin = s[("LinearSearch", "mixed")]
        t_bin, s_bin = s[("BinarySearch", "mixed")]
        ks, kint = k_min(T, t_lin, t_bin)

        md.append(f"\n## {lang}\n")
        md.append(f"1. Mejor algoritmo de ordenamiento (n = 1.000.000, aleatoria): **{alg}** \u2192 "
                  f"T_sort = {fmt(T)} (\u00b1 {fmt(sT)}; {status}).")
        md.append(f"2. B\u00fasqueda lineal sobre el arreglo desordenado (claves mixtas): t_lin = {fmt(t_lin)} por b\u00fasqueda.")
        md.append(f"3. B\u00fasqueda binaria tras ordenar (claves mixtas): t_bin = {fmt(t_bin)} por b\u00fasqueda.")
        md.append(f"4. Diferencia por b\u00fasqueda: t_lin \u2212 t_bin = {fmt(t_lin - t_bin)}.")
        md.append(f"5. k* = T_sort / (t_lin \u2212 t_bin) = {T:,.0f} ns / {t_lin - t_bin:,.0f} ns = **{ks:.2f}**.")
        md.append(f"6. Resultado: ordenar conviene a partir de **k = {kint}** b\u00fasquedas.\n")

        lo = (T - sT) / ((t_lin + s_lin) - t_bin)
        hi = (T + sT) / ((t_lin - s_lin) - t_bin)
        md.append(f"Sensibilidad al ruido (\u00b1 1 desviaci\u00f3n est\u00e1ndar en T_sort y t_lin): k* entre {lo:.0f} y {hi:.0f}.\n")
        md.append("Sensibilidad a la posici\u00f3n de las claves (t_lin seg\u00fan el escenario de la b\u00fasqueda lineal):\n")
        md.append("| Escenario de la clave | t_lin | k* | k m\u00ednimo |")
        md.append("|---|---:|---:|---:|")
        for sc, label in (("mixed", "Mixtas (500 presentes + 500 ausentes)"), ("center", "Siempre en el centro"),
                          ("end", "Siempre al final / ausentes")):
            tl = s[("LinearSearch", sc)][0]
            ks2, k2 = k_min(T, tl, s[("BinarySearch", sc)][0])
            md.append(f"| {label} | {fmt(tl)} | {ks2:.2f} | {k2} |")
            rows_csv.append([lang, alg, sc, f"{T:.1f}", f"{tl:.1f}", f"{s[('BinarySearch', sc)][0]:.1f}", f"{ks2:.2f}", k2])
        md.append("")

        ks_grid = [10 ** (i / 20) for i in range(0, 6 * 20 + 1)]
        ax.plot(ks_grid, [k * t_lin / 1e9 for k in ks_grid], color="#d62728", lw=2, label="k b\u00fasquedas lineales (sin ordenar)")
        ax.plot(ks_grid, [(T + k * t_bin) / 1e9 for k in ks_grid], color="#1f77b4", lw=2,
                label=f"Ordenar ({alg}) + k b\u00fasquedas binarias")
        ax.axvline(ks, color="gray", ls="--")
        ax.annotate(f"k* \u2248 {ks:.0f}", xy=(ks, T / 1e9), xytext=(ks * 2.5, T / 1e9 * 0.12),
                    arrowprops=dict(arrowstyle="->", color="gray"), fontsize=10)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("k (n\u00famero de b\u00fasquedas)")
        ax.set_ylabel("Tiempo total (s, escala log)")
        ax.set_title(f"{lang}: \u00bfordenar o no? (n = 1.000.000)")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend(fontsize=8.5, loc="upper left")
    fig.tight_layout()
    os.makedirs("figures", exist_ok=True)
    fig.savefig("figures/break_even.png", dpi=150)
    with open("results/break_even.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    with open("results/break_even.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["language", "best_sort", "key_scenario", "T_sort_ns", "t_lin_ns", "t_bin_ns", "k_star", "k_min"])
        w.writerows(rows_csv)
    print("Listo: results/break_even.md, results/break_even.csv, figures/break_even.png")


if __name__ == "__main__":
    main()
