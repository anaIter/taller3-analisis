"""
Algoritmos de ordenamiento del Punto 1 (version Python).
Misma implementacion que Sorts.java: todos ordenan una lista de enteros IN SITU
(el resultado queda en la misma lista) en orden ascendente.

Referencias (implementaciones estandar; citar en el informe la pagina consultada):
  - Insertion Sort, Merge Sort, Heap Sort, Radix Sort y Bucket Sort: GeeksforGeeks.
  - Dual-Pivot QuickSort: esquema de Yaroslavskiy (GeeksforGeeks "Dual pivot Quicksort"),
    con los pivotes tomados SIEMPRE del primer y del ultimo elemento del subarreglo.

Para la tabla de complejidad teorica (mejor / promedio / peor, estable, in-place)
ver el comentario inicial de Sorts.java.
"""
import math

MIN_VALUE = 10_000_000
RANGE = 90_000_000   # 99.999.999 - 10.000.000 + 1


# ------------------------------------------------------------------ Insertion Sort
def insertion_sort(a):
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key


# ------------------------------------------------------------------ Dual-Pivot QuickSort
def dual_pivot_quicksort(a):
    _dual_pivot(a, 0, len(a) - 1)


def _dual_pivot(a, low, high):
    if low >= high:
        return
    if a[low] > a[high]:
        a[low], a[high] = a[high], a[low]
    p, q = a[low], a[high]            # pivotes: primer y ultimo elemento
    lt, gt, i = low + 1, high - 1, low + 1
    while i <= gt:
        if a[i] < p:
            a[i], a[lt] = a[lt], a[i]
            lt += 1
            i += 1
        elif a[i] > q:
            a[i], a[gt] = a[gt], a[i]
            gt -= 1
        else:
            i += 1
    lt -= 1
    gt += 1
    a[low], a[lt] = a[lt], a[low]
    a[high], a[gt] = a[gt], a[high]
    _dual_pivot(a, low, lt - 1)
    if p < q:                          # si p == q el centro es todo igual
        _dual_pivot(a, lt + 1, gt - 1)
    _dual_pivot(a, gt + 1, high)


# ------------------------------------------------------------------ Merge Sort
def merge_sort(a):
    if len(a) < 2:
        return
    tmp = [0] * len(a)
    _merge_sort(a, tmp, 0, len(a) - 1)


def _merge_sort(a, tmp, lo, hi):
    if lo >= hi:
        return
    mid = (lo + hi) >> 1
    _merge_sort(a, tmp, lo, mid)
    _merge_sort(a, tmp, mid + 1, hi)
    tmp[lo:hi + 1] = a[lo:hi + 1]
    i, j, k = lo, mid + 1, lo
    while i <= mid and j <= hi:
        if tmp[i] <= tmp[j]:           # <= conserva la estabilidad
            a[k] = tmp[i]
            i += 1
        else:
            a[k] = tmp[j]
            j += 1
        k += 1
    while i <= mid:
        a[k] = tmp[i]
        i += 1
        k += 1
    while j <= hi:
        a[k] = tmp[j]
        j += 1
        k += 1


# ------------------------------------------------------------------ Heap Sort
def heap_sort(a):
    n = len(a)
    for i in range(n // 2 - 1, -1, -1):
        _sift_down(a, n, i)
    for end in range(n - 1, 0, -1):
        a[0], a[end] = a[end], a[0]
        _sift_down(a, end, 0)


def _sift_down(a, n, i):
    while True:
        largest = i
        l = 2 * i + 1
        r = l + 1
        if l < n and a[l] > a[largest]:
            largest = l
        if r < n and a[r] > a[largest]:
            largest = r
        if largest == i:
            return
        a[i], a[largest] = a[largest], a[i]
        i = largest


# ------------------------------------------------------------------ Radix Sort (LSD, base 10)
def radix_sort(a):
    n = len(a)
    if n < 2:
        return
    mx = max(a)
    out = [0] * n
    exp = 1
    while mx // exp > 0:
        count = [0] * 10
        for v in a:
            count[(v // exp) % 10] += 1
        for d in range(1, 10):
            count[d] += count[d - 1]
        for i in range(n - 1, -1, -1):          # de atras hacia adelante: estable
            d = (a[i] // exp) % 10
            count[d] -= 1
            out[count[d]] = a[i]
        a[:] = out
        exp *= 10


# ------------------------------------------------------------------ Bucket Sort
def bucket_sort(a):
    """
    k = ceil(sqrt(n)) cubetas. El valor v va a la cubeta floor((v - MIN) * k / RANGE),
    es decir, el rango [10.000.000, 99.999.999] se divide en k intervalos iguales.
    Cada cubeta se ordena con Insertion Sort y luego se concatenan.
    """
    n = len(a)
    if n < 2:
        return
    k = math.ceil(math.sqrt(n))
    count = [0] * k
    for v in a:
        count[((v - MIN_VALUE) * k) // RANGE] += 1
    buckets = [[0] * c for c in count]
    fill = [0] * k
    for v in a:
        b = ((v - MIN_VALUE) * k) // RANGE
        buckets[b][fill[b]] = v
        fill[b] += 1
    pos = 0
    for bucket in buckets:
        insertion_sort(bucket)
        for v in bucket:
            a[pos] = v
            pos += 1
