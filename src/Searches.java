/**
 * Algoritmos de busqueda del Punto 2 (version Java).
 * Todos reciben un arreglo ordenado ascendentemente (excepto la busqueda lineal, que no lo exige)
 * y devuelven el indice de una aparicion de la clave, o -1 si no esta.
 *
 * Referencias (implementaciones estandar; citar en el informe la pagina consultada de GeeksforGeeks):
 *  Linear Search, Binary Search, Ternary Search, Jump Search, Interpolation Search, Exponential Search.
 *
 * Complejidad teorica (n elementos):
 * | Algoritmo     | Mejor    | Promedio     | Peor         | Requiere ordenado |
 * |---------------|----------|--------------|--------------|-------------------|
 * | Lineal        | O(1)     | O(n)         | O(n)         | No                |
 * | Binaria       | O(1)     | O(log n)     | O(log n)     | Si                |
 * | Ternaria      | O(1)     | O(log3 n)    | O(log3 n)    | Si                |
 * | Saltos        | O(1)     | O(sqrt n)    | O(sqrt n)    | Si                |
 * | Interpolacion | O(1)     | O(log log n)*| O(n)         | Si                |
 * | Exponencial   | O(1)     | O(log i)     | O(log n)     | Si                |
 * (*) con datos distribuidos uniformemente. i = posicion de la clave.
 */
public final class Searches {
    private Searches() {}

    public static int linear(int[] a, int key) {
        for (int i = 0; i < a.length; i++) if (a[i] == key) return i;
        return -1;
    }

    public static int binary(int[] a, int key) {
        return binaryRange(a, 0, a.length - 1, key);
    }

    static int binaryRange(int[] a, int lo, int hi, int key) {
        while (lo <= hi) {
            int mid = (lo + hi) >>> 1;
            if (a[mid] == key) return mid;
            if (a[mid] < key) lo = mid + 1;
            else hi = mid - 1;
        }
        return -1;
    }

    public static int ternary(int[] a, int key) {
        int lo = 0, hi = a.length - 1;
        while (lo <= hi) {
            int third = (hi - lo) / 3;
            int m1 = lo + third, m2 = hi - third;
            if (a[m1] == key) return m1;
            if (a[m2] == key) return m2;
            if (key < a[m1]) hi = m1 - 1;
            else if (key > a[m2]) lo = m2 + 1;
            else { lo = m1 + 1; hi = m2 - 1; }
        }
        return -1;
    }

    public static int jump(int[] a, int key) {
        int n = a.length;
        if (n == 0) return -1;
        int m = (int) Math.sqrt(n);          // tamano del salto
        int step = m, prev = 0;
        while (a[Math.min(step, n) - 1] < key) {
            prev = step;
            step += m;
            if (prev >= n) return -1;
        }
        while (a[prev] < key) {
            prev++;
            if (prev == Math.min(step, n)) return -1;
        }
        return a[prev] == key ? prev : -1;
    }

    public static int interpolation(int[] a, int key) {
        int lo = 0, hi = a.length - 1;
        while (lo <= hi && key >= a[lo] && key <= a[hi]) {
            if (a[hi] == a[lo]) return a[lo] == key ? lo : -1;   // evita division por cero
            int pos = lo + (int) (((long) (key - a[lo]) * (hi - lo)) / (a[hi] - a[lo]));
            if (a[pos] == key) return pos;
            if (a[pos] < key) lo = pos + 1;
            else hi = pos - 1;
        }
        return -1;
    }

    public static int exponential(int[] a, int key) {
        int n = a.length;
        if (n == 0) return -1;
        if (a[0] == key) return 0;
        int i = 1;
        while (i < n && a[i] <= key) i *= 2;
        return binaryRange(a, i / 2, Math.min(i, n - 1), key);
    }
}
