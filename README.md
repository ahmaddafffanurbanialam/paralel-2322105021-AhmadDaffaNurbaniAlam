# Paralel Monte Carlo π — Pthreads vs OpenMP

**Nama:** Adam Arias Jauhari | **NIM:** 2322105018 | **Kelas:** 4TI01 | Universitas Cendekia Abditama

Estimasi nilai π dengan metode Monte Carlo (10⁹ titik) memakai tiga versi:
`pi_serial` (baseline), `pi_pthread` (POSIX Threads), `pi_openmp` (OpenMP).

## Struktur
| File | Fungsi |
|---|---|
| `common.h` | RNG xoshiro256** per-thread, `count_hits()`, pembagian workload, timer |
| `report.h` | Parsing argumen & format keluaran |
| `pi_serial.c` / `pi_pthread.c` / `pi_openmp.c` | Tiga implementasi |
| `verify.sh`, `bench.sh`, `plot.py` | Verifikasi, benchmark, grafik |

## Compile
```bash
make          # build semua
make clean
```
Kebutuhan: `gcc` (dengan dukungan OpenMP), `make`, Linux/WSL. Untuk grafik: `pip install pandas matplotlib`.

## Menjalankan
```bash
./pi_serial  [N]            # default N = 1000000000
./pi_pthread [N] [threads]
./pi_openmp  [N] [threads]
# tambahkan --csv untuk keluaran satu baris CSV
./pi_pthread 1000000000 4
```

## Verifikasi & Benchmark
```bash
make test                   # serial == pthread(T=1) == openmp(T=1); pthread == openmp tiap T
make bench                  # N=1e9, T=1,2,4,8, 5 ulangan -> results.csv
python3 plot.py             # summary.csv + speedup_efficiency.png
```
Variabel opsional: `N=100000000 REPS=3 make bench`.

## Desain Singkat
- **RNG**: xoshiro256** dengan state lokal; seed tiap thread = f(42, thread id) via splitmix64. Tidak ada RNG global.
- **Pthreads**: block partition, hasil per-thread di slot ber-padding (anti false sharing), reduction manual setelah `pthread_join`.
- **OpenMP**: `#pragma omp parallel` + `reduction(+:hits)`, `default(none)` agar scope variabel eksplisit.
- Pembagian workload & seed identik → hasil Pthreads = OpenMP untuk T yang sama, dan serial = T=1.
- Catatan: hasil (hits) bergantung pada jumlah thread karena aliran RNG berbeda, tetapi deterministik untuk T tertentu.

## Laporan
```bash
make bench && python3 plot.py     # hasil pengukuran -> summary.csv, speedup_efficiency.png
python3 build_report.py           # -> Laporan_Paralel_2322105018.pdf (tabel & grafik terisi otomatis)
```

## Windows (PowerShell + MinGW-w64)
```powershell
powershell -ExecutionPolicy Bypass -File .\bench.ps1   # compile, verifikasi, benchmark -> results.csv
python plot.py                                          # summary.csv + speedup_efficiency.png
```
