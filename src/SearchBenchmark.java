import java.io.*;
import java.nio.file.*;
import java.util.*;

/**
 * Harness del Punto 2 (Java): mide los 6 algoritmos de busqueda sobre los arreglos ASCENDENTES.
 *
 * Escenarios:
 *   mixed  : las 1.000 claves de data/keys_n.txt (500 presentes + 500 ausentes), cada una una vez.
 *   start  : 1.000 busquedas de la clave ubicada al inicio  (asc[0]).
 *   center : 1.000 busquedas de la clave ubicada al centro  (asc[n/2]).
 *   end    : 1.000 busquedas de la clave ubicada al final   (asc[n-1]).
 *
 * Se cronometra el tiempo TOTAL de las 1.000 busquedas (nanoTime) y se reporta el tiempo promedio POR
 * BUSQUEDA (total / 1.000). 5 repeticiones: promedio y desviacion estandar muestral.
 * Los datos se cargan antes de medir; la verificacion de resultados se hace fuera del tiempo medido.
 * Calentamiento JIT: 50 pasadas por algoritmo con el tamano menor, mas una ejecucion por celda.
 *
 * Uso: java SearchBenchmark [--data=data] [--out=results/java_search.csv]
 *                           [--sizes=1000,10000,100000,1000000] [--algs=BinarySearch,JumpSearch]
 */
public class SearchBenchmark {
    static final int REPS = 5;
    static final int NKEYS = 1000;
    static final String LANG = "Java";
    static final String[] SCENARIOS = {"mixed", "start", "center", "end"};

    interface Searcher { int search(int[] a, int key); }

    record Algo(String name, Searcher fn) {}

    static final List<Algo> ALGOS = List.of(
        new Algo("LinearSearch", Searches::linear),
        new Algo("BinarySearch", Searches::binary),
        new Algo("TernarySearch", Searches::ternary),
        new Algo("JumpSearch", Searches::jump),
        new Algo("InterpolationSearch", Searches::interpolation),
        new Algo("ExponentialSearch", Searches::exponential)
    );

    public static void main(String[] args) throws Exception {
        Map<String, String> opt = new HashMap<>();
        for (String s : args)
            if (s.startsWith("--") && s.contains("="))
                opt.put(s.substring(2, s.indexOf('=')), s.substring(s.indexOf('=') + 1));
        String dataDir = opt.getOrDefault("data", "data");
        String out = opt.getOrDefault("out", "results/java_search.csv");
        int[] sizes = Arrays.stream(opt.getOrDefault("sizes", "1000,10000,100000,1000000").split(","))
                .mapToInt(Integer::parseInt).sorted().toArray();
        Set<String> filter = new HashSet<>();
        if (opt.containsKey("algs")) filter.addAll(Arrays.asList(opt.get("algs").split(",")));
        List<Algo> algos = ALGOS.stream().filter(a -> filter.isEmpty() || filter.contains(a.name())).toList();

        // 1) Cargar datos antes de medir
        Map<Integer, int[]> arrays = new HashMap<>(), keysFile = new HashMap<>();
        for (int n : sizes) {
            arrays.put(n, readInts(Paths.get(dataDir, "asc_" + n + ".txt")));
            keysFile.put(n, readInts(Paths.get(dataDir, "keys_" + n + ".txt")));
        }
        System.out.println("Datos cargados. Calentando JIT...");

        // 2) Calentamiento global
        int n0 = sizes[0];
        int[] res0 = new int[NKEYS];
        for (Algo a : algos)
            for (int w = 0; w < 50; w++) runOnce(a, arrays.get(n0), keysFile.get(n0), res0);

        Path outPath = Paths.get(out);
        if (outPath.getParent() != null) Files.createDirectories(outPath.getParent());
        try (PrintWriter w = new PrintWriter(new BufferedWriter(new FileWriter(out)))) {
            StringBuilder h = new StringBuilder("algorithm,language,scenario,n");
            for (int r = 1; r <= REPS; r++) h.append(",rep").append(r).append("_ns_per_search");
            h.append(",mean_ns_per_search,std_ns_per_search,status,note");
            w.println(h);

            for (Algo a : algos) {
                for (String sc : SCENARIOS) {
                    for (int n : sizes) {
                        int[] arr = arrays.get(n);
                        int[] keys = keysFor(sc, arr, keysFile.get(n));
                        boolean[] present = new boolean[keys.length];
                        for (int i = 0; i < keys.length; i++) present[i] = Arrays.binarySearch(arr, keys[i]) >= 0;
                        int[] res = new int[keys.length];

                        runOnce(a, arr, keys, res);                       // calentamiento de la celda
                        double[] t = new double[REPS];
                        for (int r = 0; r < REPS; r++) {
                            long s = System.nanoTime();
                            runOnce(a, arr, keys, res);
                            long e = System.nanoTime();
                            t[r] = (double) (e - s) / keys.length;       // ns por busqueda
                            verify(a, arr, keys, present, res);          // fuera del tiempo
                        }
                        double mean = mean(t), std = std(t, mean);
                        StringBuilder sb = new StringBuilder(String.join(",", a.name(), LANG, sc, Integer.toString(n)));
                        for (double v : t) sb.append(String.format(Locale.ROOT, ",%.2f", v));
                        sb.append(String.format(Locale.ROOT, ",%.2f,%.2f,measured,", mean, std));
                        w.println(sb);
                        w.flush();
                        System.out.printf(Locale.ROOT, "%-20s %-7s n=%-8d %14.1f ns/busqueda%n", a.name(), sc, n, mean);
                    }
                }
            }
        }
        System.out.println("Listo. Resultados en " + out);
    }

    /** Ejecuta todas las busquedas del arreglo de claves guardando cada resultado. */
    static void runOnce(Algo a, int[] arr, int[] keys, int[] res) {
        Searcher f = a.fn();
        for (int i = 0; i < keys.length; i++) res[i] = f.search(arr, keys[i]);
    }

    static int[] keysFor(String sc, int[] arr, int[] mixed) {
        if (sc.equals("mixed")) return mixed;
        int key = switch (sc) {
            case "start" -> arr[0];
            case "center" -> arr[arr.length / 2];
            default -> arr[arr.length - 1];
        };
        int[] k = new int[NKEYS];
        Arrays.fill(k, key);
        return k;
    }

    static void verify(Algo a, int[] arr, int[] keys, boolean[] present, int[] res) {
        for (int i = 0; i < keys.length; i++) {
            boolean ok = present[i] ? (res[i] >= 0 && arr[res[i]] == keys[i]) : res[i] == -1;
            if (!ok) throw new IllegalStateException("Resultado incorrecto en " + a.name() + " clave=" + keys[i] + " res=" + res[i]);
        }
    }

    static double mean(double[] t) {
        double s = 0;
        for (double v : t) s += v;
        return s / t.length;
    }

    static double std(double[] t, double mean) {
        double s = 0;
        for (double v : t) s += (v - mean) * (v - mean);
        return Math.sqrt(s / (t.length - 1));
    }

    static int[] readInts(Path p) throws IOException {
        List<String> lines = Files.readAllLines(p);
        int[] a = new int[lines.size()];
        for (int i = 0; i < a.length; i++) a[i] = Integer.parseInt(lines.get(i).trim());
        return a;
    }
}
