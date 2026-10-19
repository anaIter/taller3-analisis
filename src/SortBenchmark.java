import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.function.Consumer;

/**
 * Harness del Punto 1 (Java). Mide cada algoritmo con tres variantes de entrada
 * (random, asc, desc) y los tamanos pedidos.
 *
 * Reglas aplicadas:
 *  - Los datos se leen de data/ ANTES de medir (la lectura no se cronometra).
 *  - Cada repeticion corre sobre una copia nueva (la copia no se cronometra).
 *  - Se cronometra solo el algoritmo con System.nanoTime().
 *  - Tras cada ejecucion, fuera del tiempo, se verifica que el resultado sea igual al arreglo ascendente.
 *  - Calentamiento JIT: varias ejecuciones previas por algoritmo, mas una por celda (n <= 100.000).
 *  - 5 repeticiones: se reporta promedio y desviacion estandar muestral.
 *  - Si el tiempo previsto por ejecucion supera 300 s, NO se ejecuta: se extrapola desde el tamano
 *    anterior con la complejidad teorica y se marca como "estimated".
 *  - Si hay StackOverflowError se documenta (nota en el CSV) y se estima.
 *
 * Uso: java SortBenchmark [--data=data] [--out=results/java_sorting.csv]
 *                         [--sizes=1000,10000,100000,1000000] [--stack=512]
 *      --stack = tamano de pila (MB) del hilo donde corre el benchmark.
 */
public class SortBenchmark {
    static final int REPS = 5;
    static final double LIMIT_NS = 300e9;      // 5 minutos
    static final String LANG = "Java";
    static final String[] INPUTS = {"random", "asc", "desc"};

    enum Growth { LINEAR, NLOGN, N15, QUAD }

    record Algo(String name, Consumer<int[]> fn, Growth random, Growth asc, Growth desc) {
        Growth growth(String input) {
            return switch (input) { case "asc" -> asc; case "desc" -> desc; default -> random; };
        }
    }

    static final List<Algo> ALGOS = List.of(
        new Algo("InsertionSort", Sorts::insertionSort, Growth.QUAD, Growth.LINEAR, Growth.QUAD),
        new Algo("DualPivotQuickSort", Sorts::dualPivotQuickSort, Growth.NLOGN, Growth.QUAD, Growth.QUAD),
        new Algo("MergeSort", Sorts::mergeSort, Growth.NLOGN, Growth.NLOGN, Growth.NLOGN),
        new Algo("HeapSort", Sorts::heapSort, Growth.NLOGN, Growth.NLOGN, Growth.NLOGN),
        new Algo("RadixSort", Sorts::radixSort, Growth.LINEAR, Growth.LINEAR, Growth.LINEAR),
        new Algo("BucketSort", Sorts::bucketSort, Growth.LINEAR, Growth.LINEAR, Growth.N15)
    );

    public static void main(String[] args) throws Exception {
        Map<String, String> opt = new HashMap<>();
        for (String s : args) {
            if (s.startsWith("--") && s.contains("=")) opt.put(s.substring(2, s.indexOf('=')), s.substring(s.indexOf('=') + 1));
        }
        String dataDir = opt.getOrDefault("data", "data");
        String out = opt.getOrDefault("out", "results/java_sorting.csv");
        int stackMB = Integer.parseInt(opt.getOrDefault("stack", "512"));
        int[] sizes = Arrays.stream(opt.getOrDefault("sizes", "1000,10000,100000,1000000").split(","))
                .mapToInt(Integer::parseInt).sorted().toArray();

        Thread t = new Thread(null, () -> {
            try { run(dataDir, out, sizes); }
            catch (Exception e) { e.printStackTrace(); }
        }, "bench", stackMB * 1024L * 1024L);
        t.start();
        t.join();
    }

    static void run(String dataDir, String outFile, int[] sizes) throws IOException {
        // 1) Cargar todos los datos antes de medir
        Map<String, int[]> data = new HashMap<>();
        for (int n : sizes)
            for (String in : INPUTS) data.put(in + "_" + n, readInts(Paths.get(dataDir, in + "_" + n + ".txt")));
        System.out.println("Datos cargados. Calentando JIT...");

        // 2) Calentamiento global por algoritmo (datos pequenos)
        int[] warm = data.get("random_" + sizes[0]);
        for (Algo a : ALGOS)
            for (int i = 0; i < 20; i++) a.fn().accept(warm.clone());

        Path outPath = Paths.get(outFile);
        if (outPath.getParent() != null) Files.createDirectories(outPath.getParent());
        try (PrintWriter w = new PrintWriter(new BufferedWriter(new FileWriter(outFile)))) {
            StringBuilder h = new StringBuilder("algorithm,language,input,n");
            for (int r = 1; r <= REPS; r++) h.append(",rep").append(r).append("_ns");
            h.append(",mean_ns,std_ns,status,note");
            w.println(h);

            for (Algo a : ALGOS) {
                for (String in : INPUTS) {
                    int prevN = -1;
                    double prevMean = Double.NaN;
                    for (int n : sizes) {
                        int[] arr = data.get(in + "_" + n);
                        int[] expected = data.get("asc_" + n);
                        double pred = prevN < 0 ? Double.NaN : predict(prevMean, prevN, n, a.growth(in));
                        String line;
                        double meanForNext;
                        if (!Double.isNaN(pred) && pred > LIMIT_NS) {
                            line = estimatedRow(a, in, n, pred, "No se ejecuto: tiempo previsto > 300 s; extrapolado desde n=" + prevN);
                            meanForNext = pred;
                        } else {
                            try {
                                boolean warmCell = n <= 100_000 && (Double.isNaN(pred) || pred < 20e9);
                                long[] t = measure(a, arr, expected, warmCell);
                                double mean = mean(t), std = std(t, mean);
                                line = measuredRow(a, in, n, t, mean, std);
                                meanForNext = mean;
                            } catch (StackOverflowError so) {
                                line = estimatedRow(a, in, n, pred,
                                        "StackOverflowError (recursion demasiado profunda con pila de este hilo); tiempo estimado por extrapolacion");
                                meanForNext = pred;
                                System.out.println("  !! StackOverflowError en " + a.name() + " " + in + " n=" + n);
                            }
                        }
                        w.println(line);
                        w.flush();
                        System.out.printf(Locale.ROOT, "%-20s %-7s n=%-8d %s%n", a.name(), in, n, summary(line));
                        if (!Double.isNaN(meanForNext)) { prevN = n; prevMean = meanForNext; }
                    }
                }
            }
        }
        System.out.println("Listo. Resultados en " + outFile);
    }

    // ------------------------------------------------------------------ medicion
    static long[] measure(Algo a, int[] original, int[] expected, boolean warm) {
        if (warm) a.fn().accept(original.clone());
        long[] t = new long[REPS];
        for (int r = 0; r < REPS; r++) {
            int[] copy = original.clone();                // copia fuera del tiempo
            long s = System.nanoTime();
            a.fn().accept(copy);
            long e = System.nanoTime();
            t[r] = e - s;
            if (!Arrays.equals(copy, expected))           // verificacion fuera del tiempo
                throw new IllegalStateException("Resultado incorrecto en " + a.name());
        }
        return t;
    }

    static double predict(double prevMean, int prevN, int n, Growth g) {
        double ratio = (double) n / prevN;
        return switch (g) {
            case LINEAR -> prevMean * ratio;
            case NLOGN -> prevMean * ratio * (Math.log(n) / Math.log(prevN));
            case N15 -> prevMean * Math.pow(ratio, 1.5);
            case QUAD -> prevMean * ratio * ratio;
        };
    }

    static double mean(long[] t) {
        double s = 0;
        for (long v : t) s += v;
        return s / t.length;
    }

    static double std(long[] t, double mean) {        // desviacion estandar muestral (n-1)
        double s = 0;
        for (long v : t) s += (v - mean) * (v - mean);
        return Math.sqrt(s / (t.length - 1));
    }

    // ------------------------------------------------------------------ CSV
    static String measuredRow(Algo a, String in, int n, long[] t, double mean, double std) {
        StringBuilder sb = new StringBuilder(String.join(",", a.name(), LANG, in, Integer.toString(n)));
        for (long v : t) sb.append(',').append(v);
        sb.append(String.format(Locale.ROOT, ",%.1f,%.1f,measured,", mean, std));
        return sb.toString();
    }

    static String estimatedRow(Algo a, String in, int n, double est, String note) {
        StringBuilder sb = new StringBuilder(String.join(",", a.name(), LANG, in, Integer.toString(n)));
        for (int r = 0; r < REPS; r++) sb.append(',');
        sb.append(Double.isNaN(est) ? ",," : String.format(Locale.ROOT, ",%.1f,", est));
        sb.append(",estimated,\"").append(note.replace("\"", "'")).append('"');
        return sb.toString();
    }

    static String summary(String line) {
        String[] f = line.split(",", -1);
        double mean = f[4 + REPS].isEmpty() ? Double.NaN : Double.parseDouble(f[4 + REPS]);
        return String.format(Locale.ROOT, "%12.3f ms  [%s]", mean / 1e6, f[6 + REPS]);
    }

    // ------------------------------------------------------------------ E/S
    static int[] readInts(Path p) throws IOException {
        List<String> lines = Files.readAllLines(p);
        int[] a = new int[lines.size()];
        for (int i = 0; i < a.length; i++) a[i] = Integer.parseInt(lines.get(i).trim());
        return a;
    }
}
