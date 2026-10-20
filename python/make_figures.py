#!/usr/bin/env python3
"""
Genera las graficas y la tabla de factores de crecimiento del Punto 1 (ordenamiento).

Entradas : results/java_sorting.csv  y  results/python_sorting.csv
Salidas  : figures/*.png  y  results/growth_factors.csv

Graficas (todas con escala logaritmica en el eje del tiempo):
  1) growth_java.png, growth_python.png : n vs tiempo, entrada aleatoria, una linea por algoritmo,
                                           ejes log-log. Lo estimado va con linea punteada y marcador hueco.
  2) order_effect_1000.png, _10000.png, _100000.png : Java, 3 barras por algoritmo (aleatoria,
                                           ascendente, descendente). Lo estimado va con rayas.
  3) compiled_vs_interpreted.png : n = 1.000.000, entrada aleatoria, 2 barras por algoritmo.

Uso (desde la raiz del proyecto):
  pip install matplotlib
  python python/make_figures.py [--java results/java_sorting.csv] [--python results/python_sorting.csv]
                                [--out figures]
"""
import argparse
import csv
import math
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

ALGOS = ["InsertionSort", "DualPivotQuickSort", "MergeSort", "HeapSort", "RadixSort", "BucketSort"]
INPUTS = ["random", "asc", "desc"]
INPUT_LABEL = {"random": "Aleatoria", "asc": "Ascendente", "desc": "Descendente"}
COLORS = {"InsertionSort": "#d62728", "DualPivotQuickSort": "#1f77b4", "MergeSort": "#2ca02c",
          "HeapSort": "#ff7f0e", "RadixSort": "#9467bd", "BucketSort": "#8c564b"}
INPUT_COLORS = {"random": "#4c72b0", "asc": "#55a868", "desc": "#c44e52"}
LANG_COLORS = {"Java": "#e76f51", "Python": "#2a9d8f"}

# Crecimiento teorico por (algoritmo, entrada), igual que en los harness
GROWTH = {
    ("InsertionSort", "random"): "QUAD", ("InsertionSort", "asc"): "LINEAR", ("InsertionSort", "desc"): "QUAD",
    ("DualPivotQuickSort", "random"): "NLOGN", ("DualPivotQuickSort", "asc"): "QUAD", ("DualPivotQuickSort", "desc"): "QUAD",
    ("MergeSort", "random"): "NLOGN", ("MergeSort", "asc"): "NLOGN", ("MergeSort", "desc"): "NLOGN",
    ("HeapSort", "random"): "NLOGN", ("HeapSort", "asc"): "NLOGN", ("HeapSort", "desc"): "NLOGN",
    ("RadixSort", "random"): "LINEAR", ("RadixSort", "asc"): "LINEAR", ("RadixSort", "desc"): "LINEAR",
    ("BucketSort", "random"): "N15", ("BucketSort", "asc"): "LINEAR", ("BucketSort", "desc"): "N15",
}


def load(path):
    """Devuelve {(alg, input, n): (media_ms, estimado?)}"""
    d = {}
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if not r["mean_ns"]:
                continue
            d[(r["algorithm"], r["input"], int(r["n"]))] = (float(r["mean_ns"]) / 1e6, r["status"] == "estimated")
    return d


def fmt_n(n):
    return f"{n:,}".replace(",", ".")


def fmt_time(ms):
    if ms >= 60_000:
        return f"{ms / 60_000:.1f} min"
    if ms >= 1000:
        return f"{ms / 1000:.2f} s"
    if ms >= 1:
        return f"{ms:.1f} ms"
    return f"{ms * 1000:.0f} \u00b5s"


# ---------------------------------------------------------------- 1) crecimiento
def growth_plot(data, lang, sizes, out):
    fig, ax = plt.subplots(figsize=(9, 6))
    for alg in ALGOS:
        pts = [(n, *data[(alg, "random", n)]) for n in sizes if (alg, "random", n) in data]
        c = COLORS[alg]
        for (n1, t1, e1), (n2, t2, e2) in zip(pts, pts[1:]):
            ax.plot([n1, n2], [t1, t2], color=c, linestyle="--" if (e1 or e2) else "-", linewidth=1.8)
        for n, t, est in pts:
            ax.plot(n, t, marker="o", markersize=7, color=c, markerfacecolor="white" if est else c, linestyle="none")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xticks(sizes)
    ax.set_xticklabels([f"{n:,}".replace(",", ".") for n in sizes])
    ax.set_xlabel("n (n\u00famero de elementos)")
    ax.set_ylabel("Tiempo promedio (ms, escala log)")
    ax.set_title(f"Crecimiento del tiempo con n \u2014 {lang}, entrada aleatoria")
    ax.grid(True, which="both", alpha=0.3)
    handles = [Line2D([0], [0], color=COLORS[a], lw=2, label=a) for a in ALGOS]
    handles += [Line2D([0], [0], color="gray", lw=2, linestyle="-", marker="o", label="Medido"),
                Line2D([0], [0], color="gray", lw=2, linestyle="--", marker="o", markerfacecolor="white", label="Estimado")]
    ax.legend(handles=handles, loc="upper left", fontsize=9)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------- 2) efecto del orden
def order_plot(data, lang, n, out):
    fig, ax = plt.subplots(figsize=(12, 6.5))
    width = 0.26
    for j, inp in enumerate(INPUTS):
        for i, alg in enumerate(ALGOS):
            t, est = data[(alg, inp, n)]
            x = i + (j - 1) * width
            ax.bar(x, t, width, color=INPUT_COLORS[inp], hatch="///" if est else None,
                   edgecolor="black" if est else INPUT_COLORS[inp], linewidth=0.6)
            ax.text(x, t * 1.12, fmt_time(t) + ("*" if est else ""), ha="center", va="bottom",
                    fontsize=7.5, rotation=90)
    ax.set_yscale("log")
    lo = min(t for (a, i, nn), (t, _) in data.items() if nn == n)
    hi = max(t for (a, i, nn), (t, _) in data.items() if nn == n)
    ax.set_ylim(lo / 3, hi * 40)
    ax.set_xticks(range(len(ALGOS)))
    ax.set_xticklabels(ALGOS, rotation=15)
    ax.set_ylabel("Tiempo promedio (ms, escala log)")
    ax.set_title(f"Efecto del orden de entrada \u2014 {lang}, n = {fmt_n(n)}")
    ax.grid(True, axis="y", which="both", alpha=0.3)
    handles = [Patch(facecolor=INPUT_COLORS[i], label=INPUT_LABEL[i]) for i in INPUTS]
    if any(data[(a, i, n)][1] for a in ALGOS for i in INPUTS):
        handles.append(Patch(facecolor="white", edgecolor="black", hatch="///", label="Estimado (*)"))
    ax.legend(handles=handles, loc="upper right", fontsize=9)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------- 3) compilado vs interpretado
def lang_plot(java, py, n, out):
    fig, ax = plt.subplots(figsize=(11, 6.5))
    width = 0.38
    for j, (lang, data) in enumerate([("Java", java), ("Python", py)]):
        for i, alg in enumerate(ALGOS):
            t, est = data[(alg, "random", n)]
            x = i + (j - 0.5) * width
            ax.bar(x, t, width, color=LANG_COLORS[lang], hatch="///" if est else None,
                   edgecolor="black" if est else LANG_COLORS[lang], linewidth=0.6)
            ax.text(x, t * 1.12, fmt_time(t) + ("*" if est else ""), ha="center", va="bottom", fontsize=8.5)
    ax.set_yscale("log")
    allt = [d[(a, "random", n)][0] for d in (java, py) for a in ALGOS]
    ax.set_ylim(min(allt) / 3, max(allt) * 15)
    ax.set_xticks(range(len(ALGOS)))
    ax.set_xticklabels(ALGOS, rotation=15)
    ax.set_ylabel("Tiempo promedio (ms, escala log)")
    ax.set_title(f"Compilado (Java) frente a interpretado (Python) \u2014 n = {fmt_n(n)}, entrada aleatoria")
    ax.grid(True, axis="y", which="both", alpha=0.3)
    handles = [Patch(facecolor=LANG_COLORS[l], label=l) for l in LANG_COLORS]
    if any(d[(a, "random", n)][1] for d in (java, py) for a in ALGOS):
        handles.append(Patch(facecolor="white", edgecolor="black", hatch="///", label="Estimado (*)"))
    ax.legend(handles=handles, loc="upper left", fontsize=9)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------- tabla de factores de crecimiento
def expected_ratio(growth, n1, n2):
    r = n2 / n1
    return {"LINEAR": r, "NLOGN": r * math.log(n2) / math.log(n1), "N15": r ** 1.5, "QUAD": r * r}[growth]


def growth_table(java, py, sizes, out):
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["language", "algorithm", "input", "from_n", "to_n", "measured_factor",
                    "theoretical_factor", "involves_estimated"])
        for lang, data in (("Java", java), ("Python", py)):
            for alg in ALGOS:
                for inp in INPUTS:
                    for n1, n2 in zip(sizes, sizes[1:]):
                        a, b = data.get((alg, inp, n1)), data.get((alg, inp, n2))
                        if not a or not b:
                            continue
                        w.writerow([lang, alg, inp, n1, n2, f"{b[0] / a[0]:.2f}",
                                    f"{expected_ratio(GROWTH[(alg, inp)], n1, n2):.2f}", a[1] or b[1]])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--java", default="results/java_sorting.csv")
    ap.add_argument("--python", default="results/python_sorting.csv")
    ap.add_argument("--out", default="figures")
    ap.add_argument("--table", default="results/growth_factors.csv")
    args = ap.parse_args()

    java, py = load(args.java), load(args.python)
    sizes = sorted({k[2] for k in java})
    os.makedirs(args.out, exist_ok=True)

    growth_plot(java, "Java", sizes, os.path.join(args.out, "growth_java.png"))
    growth_plot(py, "Python", sizes, os.path.join(args.out, "growth_python.png"))
    for n in (1000, 10000, 100000):
        order_plot(java, "Java", n, os.path.join(args.out, f"order_effect_{n}.png"))
    lang_plot(java, py, 1_000_000, os.path.join(args.out, "compiled_vs_interpreted.png"))
    growth_table(java, py, sizes, args.table)
    print(f"Listo: 7 graficas en {args.out}/ y tabla en {args.table}")


if __name__ == "__main__":
    main()
