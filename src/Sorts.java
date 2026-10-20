/**
 * Algoritmos de ordenamiento del Punto 1 (version Java).
 * Todos ordenan un int[] en orden ascendente, in situ desde el punto de vista de la API
 * (el resultado queda en el mismo arreglo recibido).
 *
 * Referencias (implementaciones estandar):
 *  - Insertion Sort, Merge Sort, Heap Sort, Radix Sort y Bucket Sort: GeeksforGeeks.
 *  - Dual-Pivot QuickSort: esquema de Yaroslavskiy (GeeksforGeeks "Dual pivot Quicksort"),
 *    con los pivotes tomados SIEMPRE del primer y del ultimo elemento del subarreglo.
 *
 * Complejidad teorica (n elementos, k = numero de cubetas, d = digitos, b = base):
 * | Algoritmo       | Mejor          | Promedio       | Peor           | Estable | In-place     |
 * |-----------------|----------------|----------------|----------------|---------|--------------|
 * | Insertion       | O(n)           | O(n^2)         | O(n^2)         | Si      | Si           |
 * | Dual-Pivot QS   | O(n log n)     | O(n log n)     | O(n^2)         | No      | Si (pila O(log n) a O(n)) |
 * | Merge           | O(n log n)     | O(n log n)     | O(n log n)     | Si      | No (O(n))    |
 * | Heap            | O(n log n)     | O(n log n)     | O(n log n)     | No      | Si           |
 * | Radix (LSD)     | O(d(n+b))      | O(d(n+b))      | O(d(n+b))      | Si      | No (O(n+b))  |
 * | Bucket          | O(n+k)         | O(n+k)         | O(n^2)         | Si*     | No (O(n+k))  |
 * (*) estable si el ordenamiento interno de cada cubeta es estable (aqui, insercion).
 */
public final class Sorts {
    private Sorts() {}

    // ---------------------------------------------------------------- Insertion Sort
    public static void insertionSort(int[] a) {
        for (int i = 1; i < a.length; i++) {
            int key = a[i];
            int j = i - 1;
            while (j >= 0 && a[j] > key) {
                a[j + 1] = a[j];
                j--;
            }
            a[j + 1] = key;
        }
    }

    // ---------------------------------------------------------------- Dual-Pivot QuickSort
    public static void dualPivotQuickSort(int[] a) {
        dualPivot(a, 0, a.length - 1);
    }

    private static void dualPivot(int[] a, int low, int high) {
        if (low >= high) return;
        if (a[low] > a[high]) swap(a, low, high);
        int p = a[low], q = a[high];          // pivotes: primer y ultimo elemento
        int lt = low + 1, gt = high - 1, i = low + 1;
        while (i <= gt) {
            if (a[i] < p) {
                swap(a, i, lt);
                lt++;
                i++;
            } else if (a[i] > q) {
                swap(a, i, gt);
                gt--;
            } else {
                i++;
            }
        }
        lt--;
        gt++;
        swap(a, low, lt);
        swap(a, high, gt);
        dualPivot(a, low, lt - 1);
        if (p < q) dualPivot(a, lt + 1, gt - 1);   // si p == q el centro es todo igual
        dualPivot(a, gt + 1, high);
    }

    private static void swap(int[] a, int i, int j) {
        int t = a[i];
        a[i] = a[j];
        a[j] = t;
    }

    // ---------------------------------------------------------------- Merge Sort
    public static void mergeSort(int[] a) {
        if (a.length < 2) return;
        int[] tmp = new int[a.length];
        mergeSort(a, tmp, 0, a.length - 1);
    }

    private static void mergeSort(int[] a, int[] tmp, int lo, int hi) {
        if (lo >= hi) return;
        int mid = (lo + hi) >>> 1;
        mergeSort(a, tmp, lo, mid);
        mergeSort(a, tmp, mid + 1, hi);
        System.arraycopy(a, lo, tmp, lo, hi - lo + 1);
        int i = lo, j = mid + 1, k = lo;
        while (i <= mid && j <= hi) {
            if (tmp[i] <= tmp[j]) a[k++] = tmp[i++];   // <= conserva la estabilidad
            else a[k++] = tmp[j++];
        }
        while (i <= mid) a[k++] = tmp[i++];
        while (j <= hi) a[k++] = tmp[j++];
    }

    // ---------------------------------------------------------------- Heap Sort
    public static void heapSort(int[] a) {
        int n = a.length;
        for (int i = n / 2 - 1; i >= 0; i--) siftDown(a, n, i);
        for (int end = n - 1; end > 0; end--) {
            swap(a, 0, end);
            siftDown(a, end, 0);
        }
    }

    private static void siftDown(int[] a, int n, int i) {
        while (true) {
            int largest = i, l = 2 * i + 1, r = l + 1;
            if (l < n && a[l] > a[largest]) largest = l;
            if (r < n && a[r] > a[largest]) largest = r;
            if (largest == i) return;
            swap(a, i, largest);
            i = largest;
        }
    }

    // ---------------------------------------------------------------- Radix Sort (LSD, base 10)
    public static void radixSort(int[] a) {
        if (a.length < 2) return;
        int max = a[0];
        for (int v : a) if (v > max) max = v;
        int[] out = new int[a.length];
        for (long exp = 1; max / exp > 0; exp *= 10) {
            int[] count = new int[10];
            for (int v : a) count[(int) ((v / exp) % 10)]++;
            for (int d = 1; d < 10; d++) count[d] += count[d - 1];
            for (int i = a.length - 1; i >= 0; i--) {          // de atras hacia adelante: estable
                int d = (int) ((a[i] / exp) % 10);
                out[--count[d]] = a[i];
            }
            System.arraycopy(out, 0, a, 0, a.length);
        }
    }

    // ---------------------------------------------------------------- Bucket Sort
    /** Rango de los datos del taller: enteros de 8 digitos. */
    static final int MIN_VALUE = 10_000_000;
    static final int RANGE = 90_000_000;   // 99.999.999 - 10.000.000 + 1

    /**
     * k = ceil(sqrt(n)) cubetas. El valor v va a la cubeta floor((v - MIN) * k / RANGE),
     * es decir, el rango [10.000.000, 99.999.999] se divide en k intervalos iguales.
     * Cada cubeta se ordena con Insertion Sort y luego se concatenan.
     */
    public static void bucketSort(int[] a) {
        int n = a.length;
        if (n < 2) return;
        int k = (int) Math.ceil(Math.sqrt(n));
        int[] count = new int[k];
        for (int v : a) count[bucketIndex(v, k)]++;
        int[][] buckets = new int[k][];
        for (int i = 0; i < k; i++) buckets[i] = new int[count[i]];
        int[] fill = new int[k];
        for (int v : a) {
            int b = bucketIndex(v, k);
            buckets[b][fill[b]++] = v;
        }
        int pos = 0;
        for (int i = 0; i < k; i++) {
            insertionSort(buckets[i]);
            for (int v : buckets[i]) a[pos++] = v;
        }
    }

    static int bucketIndex(int v, int k) {
        return (int) (((long) (v - MIN_VALUE) * k) / RANGE);
    }
}
