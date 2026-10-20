"""
Algoritmos de busqueda del Punto 2 (version Python). Misma implementacion que Searches.java.
Reciben una lista ordenada ascendentemente (la lineal no lo exige) y devuelven el indice de una
aparicion de la clave, o -1 si no esta.

Referencias: GeeksforGeeks (Linear, Binary, Ternary, Jump, Interpolation y Exponential Search);

"""
import math


def linear(a, key):
    for i in range(len(a)):
        if a[i] == key:
            return i
    return -1


def binary(a, key):
    return _binary_range(a, 0, len(a) - 1, key)


def _binary_range(a, lo, hi, key):
    while lo <= hi:
        mid = (lo + hi) >> 1
        v = a[mid]
        if v == key:
            return mid
        if v < key:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def ternary(a, key):
    lo, hi = 0, len(a) - 1
    while lo <= hi:
        third = (hi - lo) // 3
        m1, m2 = lo + third, hi - third
        if a[m1] == key:
            return m1
        if a[m2] == key:
            return m2
        if key < a[m1]:
            hi = m1 - 1
        elif key > a[m2]:
            lo = m2 + 1
        else:
            lo, hi = m1 + 1, m2 - 1
    return -1


def jump(a, key):
    n = len(a)
    if n == 0:
        return -1
    m = math.isqrt(n)                  # tamano del salto
    step, prev = m, 0
    while a[min(step, n) - 1] < key:
        prev = step
        step += m
        if prev >= n:
            return -1
    while a[prev] < key:
        prev += 1
        if prev == min(step, n):
            return -1
    return prev if a[prev] == key else -1


def interpolation(a, key):
    lo, hi = 0, len(a) - 1
    while lo <= hi and a[lo] <= key <= a[hi]:
        if a[hi] == a[lo]:             # evita division por cero
            return lo if a[lo] == key else -1
        pos = lo + ((key - a[lo]) * (hi - lo)) // (a[hi] - a[lo])
        if a[pos] == key:
            return pos
        if a[pos] < key:
            lo = pos + 1
        else:
            hi = pos - 1
    return -1


def exponential(a, key):
    n = len(a)
    if n == 0:
        return -1
    if a[0] == key:
        return 0
    i = 1
    while i < n and a[i] <= key:
        i *= 2
    return _binary_range(a, i // 2, min(i, n - 1), key)
