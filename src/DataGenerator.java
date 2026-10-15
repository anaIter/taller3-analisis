import java.io.*;
import java.util.*;

/**
 * Genera una sola vez todos los datos de prueba del taller (semilla fija => reproducible).
 * Por cada n produce en data/:
 *   random_n.txt  : n enteros aleatorios de 8 digitos [10.000.000, 99.999.999]
 *   asc_n.txt     : los mismos datos ordenados ascendentemente
 *   desc_n.txt    : los mismos datos ordenados descendentemente
 *   keys_n.txt    : 1.000 claves de busqueda (500 presentes + 500 ausentes, mezcladas),
 *                   calculadas sobre asc_n
 * Uso: java DataGenerator [directorioSalida]
 */
public class DataGenerator {
    static final long SEED = 42L;
    static final int[] SIZES = {1_000, 10_000, 100_000, 1_000_000};
    static final int MIN = 10_000_000, MAX = 99_999_999; // 8 digitos
    static final int KEYS_PRESENT = 500, KEYS_ABSENT = 500;

    public static void main(String[] args) throws IOException {
        File dir = new File(args.length > 0 ? args[0] : "data");
        dir.mkdirs();
        Random rnd = new Random(SEED);

        for (int n : SIZES) {
            int[] a = new int[n];
            for (int i = 0; i < n; i++) a[i] = MIN + rnd.nextInt(MAX - MIN + 1);

            int[] asc = a.clone();
            Arrays.sort(asc);
            int[] desc = new int[n];
            for (int i = 0; i < n; i++) desc[i] = asc[n - 1 - i];

            write(new File(dir, "random_" + n + ".txt"), a);
            write(new File(dir, "asc_" + n + ".txt"), asc);
            write(new File(dir, "desc_" + n + ".txt"), desc);
            write(new File(dir, "keys_" + n + ".txt"), makeKeys(asc, rnd));
            System.out.println("Generado n = " + n);
        }
    }

    /** 500 claves presentes (posiciones distintas) + 500 ausentes, mezcladas. */
    static int[] makeKeys(int[] asc, Random rnd) {
        int n = asc.length;
        List<Integer> keys = new ArrayList<>();

        Set<Integer> idx = new HashSet<>();
        while (idx.size() < KEYS_PRESENT) idx.add(rnd.nextInt(n));
        for (int i : idx) keys.add(asc[i]);

        Set<Integer> absent = new HashSet<>();
        while (absent.size() < KEYS_ABSENT) {
            int k = MIN + rnd.nextInt(MAX - MIN + 1);
            if (Arrays.binarySearch(asc, k) < 0) absent.add(k);
        }
        keys.addAll(absent);

        Collections.shuffle(keys, rnd);
        int[] r = new int[keys.size()];
        for (int i = 0; i < r.length; i++) r[i] = keys.get(i);
        return r;
    }

    static void write(File f, int[] a) throws IOException {
        try (BufferedWriter w = new BufferedWriter(new FileWriter(f))) {
            for (int v : a) { w.write(Integer.toString(v)); w.newLine(); }
        }
    }
}