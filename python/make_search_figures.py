#!/usr/bin/env python3
"""
Genera las graficas y tablas del Punto 2 (busqueda).

Entradas : results/java_search.csv  y  results/python_search.csv
Salidas  : figures/search_growth_java.png, figures/search_growth_python.png,
           figures/search_compiled_vs_interpreted.png,
           results/search_position_java.csv, results/search_position_python.csv,
           results/search_position_tables.md  (tablas listas para pegar en el informe)

Todas las graficas usan escala logaritmica en el eje del tiempo (tiempo promedio por busqueda).

Uso (desde la raiz del proyecto):
  python python/make_search_figures.py [--java ...] [--python ...] [--out figures] [--tables results]
"""
import argparse
import csv
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

ALGOS = ["LinearSearch", "BinarySearch", "TernarySearch", "JumpSearch", "InterpolationSearch", "ExponentialSearch"]
COLORS = {"LinearSearch": "#d62728", "BinarySearch": "#1f77b4", "TernarySearch": "#2ca02c",
          "JumpSearch": "#ff7f0e", "InterpolationSearch": "#9467bd", "ExponentialSearch": "#8c564b"}
LANG_COLORS = {"Java": "#e76f51", "Python": "#2a9d8f"}
POSITIONS = [("start", "Inicio"), ("center", "Centro"), ("end", "Final")]


def load(path):
    """{(algoritmo, escenario, n): (media_ns, desviacion_ns)}"""
    d = {}
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            d[(r["algorithm"], r["scenario"], int(r["n"]))] = (float(r["mean_ns_per_search"]), float(r["std_ns_per_search"]))
    return d


def fmt_n(n):
    return f"{n:,}".replace(",", ".")


def fmt_ns(ns):
    if ns >= 1e6:
        return f"{ns / 1e6:.2f} ms"
    if ns >= 1e3:
        return f"{ns / 1e3:.1f} \u00b5s"
    return f"{ns:.1f} ns"


def growth_plot(data, lang, sizes, out):
    fig, ax = plt.subplots(figsize=(9, 6))
    for alg in ALGOS:
        xs = [n for n in sizes if (alg, "mixed", n) in data]
        ys = [data[(alg, "mixed", n)][0] for n in xs]
        ax.plot(xs, ys, marker="o", markersize=7, linewidth=1.8, color=COLORS[alg], label=alg)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xticks(sizes)
    ax.set_xticklabels([fmt_n(n) for n in sizes])
    ax.set_xlabel("n (n\u00famero de elementos)")
    ax.set_ylabel("Tiempo promedio por b\u00fasqueda (ns, escala log)")
    ax.set_title(f"Crecimiento del tiempo de b\u00fasqueda con n \u2014 {lang}")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def lang_plot(java, py, n, out):
    fig, ax = plt.subplots(figsize=(11, 6.5))
    width = 0.38
    for j, (lang, data) in enumerate([("Java", java), ("Python", py)]):
        for i, alg in enumerate(ALGOS):
            t = data[(alg, "mixed", n)][0]
            x = i + (j - 0.5) * width
            ax.bar(x, t, width, color=LANG_COLORS[lang])
            ax.text(x, t * 1.12, fmt_ns(t), ha="center", va="bottom", fontsize=8.5)
    ax.set_yscale("log")
    allt = [d[(a, "mixed", n)][0] for d in (java, py) for a in ALGOS]
    ax.set_ylim(min(allt) / 3, max(allt) * 8)
    ax.set_xticks(range(len(ALGOS)))
    ax.set_xticklabels(ALGOS, rotation=15)
    ax.set_ylabel("Tiempo promedio por b\u00fasqueda (ns, escala log)")
    ax.set_title(f"Compilado (Java) frente a interpretado (Python) \u2014 n = {fmt_n(n)}")
    ax.grid(True, axis="y", which="both", alpha=0.3)
    ax.legend(handles=[Patch(facecolor=LANG_COLORS[l], label=l) for l in LANG_COLORS], loc="upper right", fontsize=9)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def position_tables(java, py, n, tables_dir):
    md = [f"# Tiempo promedio por b\u00fasqueda seg\u00fan la posici\u00f3n de la clave (n = {fmt_n(n)})\n"]
    for lang, data in (("Java", java), ("Python", py)):
        path = os.path.join(tables_dir, f"search_position_{lang.lower()}.csv")
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["algorithm"] + [f"{k}_ns_per_search" for k, _ in POSITIONS])
            for alg in ALGOS:
                w.writerow([alg] + [f"{data[(alg, k, n)][0]:.2f}" for k, _ in POSITIONS])
        md.append(f"\n## {lang}\n")
        md.append("| Algoritmo | " + " | ".join(lbl for _, lbl in POSITIONS) + " |")
        md.append("|---|" + "---:|" * len(POSITIONS))
        for alg in ALGOS:
            md.append(f"| {alg} | " + " | ".join(fmt_ns(data[(alg, k, n)][0]) for k, _ in POSITIONS) + " |")
    with open(os.path.join(tables_dir, "search_position_tables.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--java", default="results/java_search.csv")
    ap.add_argument("--python", default="results/python_search.csv")
    ap.add_argument("--out", default="figures")
    ap.add_argument("--tables", default="results")
    args = ap.parse_args()

    java, py = load(args.java), load(args.python)
    sizes = sorted({k[2] for k in java})
    os.makedirs(args.out, exist_ok=True)
    os.makedirs(args.tables, exist_ok=True)
    growth_plot(java, "Java", sizes, os.path.join(args.out, "search_growth_java.png"))
    growth_plot(py, "Python", sizes, os.path.join(args.out, "search_growth_python.png"))
    lang_plot(java, py, 1_000_000, os.path.join(args.out, "search_compiled_vs_interpreted.png"))
    position_tables(java, py, 1_000_000, args.tables)
    print(f"Listo: 3 graficas en {args.out}/ y tablas en {args.tables}/")


if __name__ == "__main__":
    main()
