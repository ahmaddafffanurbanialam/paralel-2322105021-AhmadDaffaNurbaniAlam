#!/usr/bin/env python3
"""build_report.py - Membangun Laporan PDF dari data hasil pengukuran.

Input (opsional; jika belum ada, bagian terkait diberi penanda kuning untuk diisi):
  results.csv, summary.csv, speedup_efficiency.png  <- dari `make bench && python3 plot.py`
  accuracy_vs_N.csv, accuracy_vs_T.csv              <- eksperimen akurasi
Pakai: python3 build_report.py   -> Laporan_Paralel_2322105018.pdf
"""
import os, math
import pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                                Table, TableStyle, Image, PageBreak, Preformatted, KeepTogether)

FD = "/usr/share/fonts/truetype/dejavu/"
for n, f in [("Serif","DejaVuSerif.ttf"),("Serif-B","DejaVuSerif-Bold.ttf"),
             ("Serif-I","DejaVuSerif-Italic.ttf"),("Serif-BI","DejaVuSerif-BoldItalic.ttf"),
             ("Mono","DejaVuSansMono.ttf")]:
    pdfmetrics.registerFont(TTFont(n, FD + f))
pdfmetrics.registerFontFamily("Serif", normal="Serif", bold="Serif-B", italic="Serif-I", boldItalic="Serif-BI")

NAMA, NIM, KELAS, ABSEN = "Adam Arias Jauhari", "2322105018", "4TI01", "16"
ANGGOTA = [("Adam Arias Jauhari","2322105018","16"),("Hafidh Tazakka","2322105006","06"),
           ("Ahmad Daffa Nurbani Alam","2322105021","18"),("Noval Abiludin","2322105013","12"),
           ("Muhammad Sayed Azis","2322105071","55")]
OUT = "Laporan_Paralel_2322105018.pdf"

# ---------- gaya ----------
body = ParagraphStyle("body", fontName="Serif", fontSize=10, leading=14.5, alignment=TA_JUSTIFY, spaceAfter=6)
h1 = ParagraphStyle("h1", fontName="Serif-B", fontSize=14, leading=18, spaceBefore=4, spaceAfter=8)
h2 = ParagraphStyle("h2", fontName="Serif-B", fontSize=11.5, leading=15, spaceBefore=8, spaceAfter=4)
h3 = ParagraphStyle("h3", fontName="Serif-BI", fontSize=10.5, leading=14, spaceBefore=4, spaceAfter=3)
bul = ParagraphStyle("bul", parent=body, leftIndent=16, bulletIndent=4, spaceAfter=3)
cap = ParagraphStyle("cap", fontName="Serif-I", fontSize=9, leading=12, alignment=TA_CENTER, spaceAfter=10)
cell = ParagraphStyle("cell", fontName="Serif", fontSize=8.8, leading=11.5)
cellb = ParagraphStyle("cellb", parent=cell, fontName="Serif-B")
code = ParagraphStyle("code", fontName="Mono", fontSize=7.6, leading=9.6, backColor=colors.HexColor("#F3F3F3"),
                      borderPadding=5, spaceBefore=4, spaceAfter=10, leftIndent=4)
TODO = lambda t: f'<font backColor="#FFF2A8">[ISI: {t}]</font>'

def P(t, s=body): return Paragraph(t, s)
def B(items): return [Paragraph(i, bul, bulletText="•") for i in items]
def C(t): return Preformatted(t.strip("\n"), code)

def table(rows, widths, header=True, align_center_from=None):
    data = [[Paragraph(str(c), cellb if (header and i == 0) else cell) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    st = [("GRID",(0,0),(-1,-1),0.4,colors.grey),("VALIGN",(0,0),(-1,-1),"TOP"),
          ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3)]
    if header: st.append(("BACKGROUND",(0,0),(-1,0),colors.HexColor("#DDE6F0")))
    t.setStyle(TableStyle(st)); return t

# ---------- data ----------
have_sum = os.path.exists("summary.csv")
if have_sum:
    summ = pd.read_csv("summary.csv")
    t_serial = summ[summ.impl == "serial"].time.iloc[0]
    summ = summ[summ.impl != "serial"]
NM = {"pthread": "Pthreads", "openmp": "OpenMP"}
accN = pd.read_csv("accuracy_vs_N.csv"); accT = pd.read_csv("accuracy_vs_T.csv")

# grafik akurasi vs N (data nyata) + garis galat standar teoretis
fig, ax = plt.subplots(figsize=(5.6, 3.3))
ax.loglog(accN.N, accN.error, "o-", label="Galat terukur |π̂ − π| (seed 42)")
xs = accN.N.values
ax.loglog(xs, 1.6422/xs**0.5, "k--", label="Galat standar teoretis 1,642/√N")
ax.set(xlabel="Jumlah sampel N", ylabel="Galat absolut"); ax.grid(alpha=.3, which="both"); ax.legend(fontsize=8)
plt.tight_layout(); plt.savefig("accuracy_vs_N.png", dpi=160); plt.close()

def fmt(x, d=4): return f"{x:.{d}f}"

# ---------- isi ----------
S = []
# Sampul
S += [Spacer(1, 2.6*cm), P("<b>LAPORAN TUGAS M6</b>", ParagraphStyle("t0", fontName="Serif-B", fontSize=13, alignment=TA_CENTER, spaceAfter=6)),
      P("<b>Komputasi Paralel</b>", ParagraphStyle("t1", fontName="Serif-B", fontSize=13, alignment=TA_CENTER, spaceAfter=24)),
      P("<b>Implementasi dan Analisis Komparatif POSIX Threads vs OpenMP<br/>pada Simulasi Monte Carlo Estimasi Nilai π</b>",
        ParagraphStyle("t2", fontName="Serif-B", fontSize=15, leading=21, alignment=TA_CENTER, spaceAfter=40)),
      P("Disusun oleh:", ParagraphStyle("c", fontName="Serif", fontSize=11, alignment=TA_CENTER, spaceAfter=8)),
      *[P(f"<b>{n}</b><br/>NIM {i} &nbsp;|&nbsp; No. Absen {a}",
          ParagraphStyle("c2", fontName="Serif", fontSize=11, leading=15.5, alignment=TA_CENTER, spaceAfter=9))
        for n, i, a in ANGGOTA],
      P(f"Kelas {KELAS}", ParagraphStyle("c2k", fontName="Serif", fontSize=11, alignment=TA_CENTER, spaceAfter=40)),
      P("<b>Program Studi Teknik Informatika<br/>Universitas Cendekia Abditama</b><br/>2026",
        ParagraphStyle("c3", fontName="Serif", fontSize=11.5, leading=17, alignment=TA_CENTER)),
      Spacer(1, 1.2*cm),
      P("Repository: github.com/AdamJauhari/Tugas_UTS_Komputer-Paralel", ParagraphStyle("c4", fontName="Mono", fontSize=8.5, alignment=TA_CENTER)),
      PageBreak()]

# 1. Pendahuluan
S += [P("1. PENDAHULUAN", h1), P("1.1 Latar Belakang Masalah", h2),
 P("Metode Monte Carlo menyelesaikan masalah numerik dengan pengambilan sampel acak berulang. Salah satu contoh klasiknya adalah estimasi nilai π: titik (x, y) diambil seragam acak pada kuadran satuan [0,1] × [0,1], lalu dihitung berapa banyak titik yang jatuh di dalam seperempat lingkaran satuan (x² + y² ≤ 1). Karena luas seperempat lingkaran adalah π/4 dan luas kuadran adalah 1, rasio titik di dalam lingkaran terhadap total titik menghampiri π/4, sehingga π ≈ 4 · (jumlah titik di dalam) / N."),
 P("Galat standar estimator ini menurun sebagai 1/√N, yaitu ≈ 1,642/√N. Untuk memperoleh satu digit desimal tambahan diperlukan sekitar 100 kali lebih banyak sampel. Konsekuensinya, estimasi yang akurat membutuhkan jumlah sampel sangat besar (pada tugas ini N = 10⁹) dan waktu komputasi serial menjadi signifikan. Di sisi lain, setiap sampel bersifat independen sehingga masalah ini tergolong <i>embarrassingly parallel</i>: tidak ada ketergantungan data antar iterasi selain penjumlahan akhir. Karakteristik ini menjadikannya kasus yang ideal untuk membandingkan dua pendekatan pemrograman paralel pada sistem <i>shared-memory</i>."),
 P("Meskipun mudah diparalelkan, kasus ini memuat tiga jebakan yang khas dalam pemrograman paralel: (1) <i>race condition</i> pada akumulator hasil, (2) penggunaan generator bilangan acak (RNG) global yang menjadi titik kontensi sekaligus merusak kualitas statistik, dan (3) <i>false sharing</i> pada variabel hasil per-thread yang berdekatan di memori. Ketiganya dibahas pada laporan ini."),
 P("1.2 Tujuan Implementasi", h2)]
S += B(["Mengimplementasikan estimasi π dengan Monte Carlo 10⁹ sampel dalam tiga versi: serial (baseline), POSIX Threads (Pthreads), dan OpenMP.",
        "Menjamin kebenaran hasil: tidak ada <i>race condition</i>, RNG privat per thread, dan hasil paralel dapat diverifikasi terhadap versi serial.",
        "Mengukur waktu eksekusi, <i>speedup</i>, dan <i>efficiency</i> untuk 1, 2, 4, dan 8 thread.",
        "Menganalisis secara kritis perbedaan kompleksitas kode, bottleneck (Hukum Amdahl), anomali pengukuran, serta <i>trade-off</i> antara kemudahan (OpenMP) dan kontrol (Pthreads).",
        "Menganalisis <i>trade-off</i> jumlah thread terhadap akurasi statistik."])
S.append(PageBreak())

# 2. Desain
S += [P("2. DESAIN IMPLEMENTASI", h1), P("2.1 Algoritma Serial (Baseline)", h2),
 P("Algoritma serial menggunakan satu RNG dan satu loop sepanjang N iterasi. Pseudocode-nya:"),
 C("""
hits <- 0
rng  <- seed(42)
untuk i = 1 .. N:
    x <- rng_double(rng)        // seragam di [0,1)
    y <- rng_double(rng)
    jika x*x + y*y <= 1:  hits <- hits + 1
pi_hat <- 4 * hits / N
"""),
 P("Kompleksitas waktu O(N) dengan memori O(1): seluruh state (4 × 64 bit RNG, <i>counter</i> hits, x, y) muat di register CPU sehingga loop tidak memproduksi lalu lintas memori yang berarti. Beban kerja ini murni <i>compute-bound</i>. Hal ini penting untuk analisis selanjutnya: kinerja paralel tidak dibatasi oleh <i>memory bandwidth</i>, melainkan oleh jumlah <i>core</i> fisik, frekuensi CPU, dan overhead paralelisasi."),
 P("<b>Generator bilangan acak.</b> Digunakan xoshiro256** (Blackman &amp; Vigna, 2021): generator modern dengan state 256 bit, periode 2²⁵⁶ − 1, lolos baterai uji statistik BigCrush, dan sangat cepat (hanya operasi geser, rotasi, XOR, dan perkalian). State diinisialisasi dari satu seed 64-bit menggunakan SplitMix64 (Steele dkk., 2014) agar bit-bit state terdistribusi baik. Bilangan <i>double</i> dibentuk dari 53 bit teratas keluaran 64-bit (dibagi 2⁵³) sehingga seragam di [0,1). Pemilihan ini menggantikan <font name='Mono'>rand()</font> yang memakai state global dan (pada glibc) dilindungi kunci; <font name='Mono'>rand_r()</font> sebenarnya thread-safe tetapi berkualitas statistik jauh lebih rendah dan <i>state</i>-nya hanya 32 bit."),
 P("2.2 Strategi Paralelisasi Pthreads", h2), P("Pembagian workload", h3),
 P("Digunakan <i>block partition</i> statis. Dengan T thread dan N sampel, thread ke-t menerima n<sub>t</sub> = ⌊N/T⌋ + [t &lt; (N mod T)] sampel; sisa pembagian disebar satu per satu ke thread berindeks kecil sehingga selisih beban antar thread paling banyak satu sampel. Karena setiap iterasi memiliki biaya hampir identik (tidak ada percabangan berat atau data-dependent cost), partisi statis sudah menghasilkan <i>load balance</i> yang baik dan tidak memerlukan penjadwalan dinamis. Setiap thread memanggil fungsi inti <font name='Mono'>count_hits(n, tid)</font> yang membuat RNG <b>lokal</b> pada <i>stack</i> thread itu, dengan seed turunan dari (42, tid). Tidak ada satu pun state RNG yang dibagi antar thread."),
 C("""
typedef struct {            // satu cache line (64 B) per thread
    int tid; uint64_t n; char pad0[48];
    uint64_t hits;          // hasil lokal thread
    char pad1[56];
} task_t;

static void *worker(void *arg) {
    task_t *t = (task_t *)arg;
    t->hits = count_hits(t->n, (uint64_t)t->tid);   // RNG lokal
    return NULL;
}
"""),
 P("Mekanisme sinkronisasi", h3),
 P("Pendekatan yang dipilih adalah <b>reduction manual tanpa kunci</b>. Setiap thread menulis hasilnya hanya ke slot <font name='Mono'>tasks[tid].hits</font> miliknya sendiri; tidak ada dua thread yang menulis lokasi memori yang sama sehingga <i>race condition</i> pada akumulator tidak mungkin terjadi. Thread utama memanggil <font name='Mono'>pthread_join()</font> untuk setiap thread (berfungsi sekaligus sebagai <i>barrier</i> dan menjamin <i>happens-before</i> antara penulisan hasil worker dan pembacaan oleh thread utama), kemudian menjumlahkan semua slot secara serial: sebuah penjumlahan T bilangan, yang biayanya dapat diabaikan."),
 P("Alternatif yang ditolak: (a) <font name='Mono'>pthread_mutex_lock</font> di dalam loop, yang akan men-serialisasi 10⁹ operasi dan menghancurkan <i>speedup</i>; (b) variabel global bersama dengan <font name='Mono'>__atomic_fetch_add</font> per iterasi, yang menyebabkan <i>cache-line bouncing</i> antar core; (c) satu kali <i>lock</i> di akhir tiap thread, yang benar namun tidak perlu karena <font name='Mono'>join</font> sudah cukup."),
 P("<b>False sharing.</b> Bila slot hasil disimpan dalam array <font name='Mono'>uint64_t hits[T]</font> yang rapat, beberapa slot berbagi satu <i>cache line</i> 64 byte. Penulisan oleh satu core meng-invalidate baris itu pada core lain walaupun variabelnya berbeda. Karena ditulis sekali di akhir, dampaknya pada program ini kecil, tetapi <i>padding</i> diterapkan sebagai praktik yang benar dan dapat dijelaskan secara eksplisit. Pada versi yang menaikkan <font name='Mono'>hits</font> langsung di slot array di dalam loop, <i>false sharing</i> dapat menurunkan kinerja berkali lipat."),
 P("2.3 Strategi Paralelisasi OpenMP", h2), P("Pemilihan pragma &amp; clause", h3),
 C("""
uint64_t hits = 0;
#pragma omp parallel num_threads(T) default(none) shared(N, T) reduction(+:hits)
{
    int      tid = omp_get_thread_num();       // private (dideklarasi di dalam region)
    uint64_t n   = chunk_size(N, T, tid);      // private
    hits += count_hits(n, (uint64_t)tid);      // RNG lokal di dalam count_hits
}
"""),
 P("Cukup satu direktif. Alasan pemilihan tiap bagian:"),
 table([["Direktif / clause","Fungsi","Alasan dipilih"],
  ["parallel","Membentuk tim T thread yang menjalankan blok yang sama (model SPMD).","Memungkinkan setiap thread membuat RNG sendiri dan memakai partisi eksplisit identik dengan Pthreads."],
  ["num_threads(T)","Menetapkan jumlah thread.","Variasi 1, 2, 4, 8 dikendalikan dari argumen program, bukan variabel lingkungan."],
  ["default(none)","Mewajibkan semua variabel dideklarasikan scope-nya.","Mencegah scope tersirat yang keliru (sumber bug umum); kompilator memaksa kita memikirkan setiap variabel."],
  ["shared(N, T)","N dan T dibagi antar thread.","Hanya dibaca, tidak ada penulisan sehingga aman tanpa sinkronisasi."],
  ["reduction(+:hits)","Tiap thread memperoleh salinan privat <i>hits</i> (inisial 0); saat region berakhir semua salinan dijumlahkan ke variabel asli.","Menghilangkan race condition pada akumulator secara otomatis dan tanpa kunci di dalam loop; setara dengan reduction manual pada Pthreads."]],
  [3.2*cm, 6.0*cm, 6.8*cm]),
 Spacer(1,8),
 P("<b>Mengapa bukan <font name='Mono'>#pragma omp parallel for</font>?</b> Bentuk <i>parallel for</i> dengan satu RNG per thread dan <font name='Mono'>schedule(static)</font> secara fungsional juga benar, tetapi pembagian iterasi dan seed-nya ditentukan runtime sehingga hasil numerik tidak otomatis identik dengan versi Pthreads. Dengan membentuk partisi dan seed secara eksplisit di dalam <font name='Mono'>parallel</font>, kedua implementasi menghasilkan <i>hits</i> yang <b>persis sama</b> untuk T yang sama, sehingga verifikasi correctness menjadi tepat (bit-per-bit), bukan sekadar statistik, dan perbandingan kinerja menjadi adil (kerja identik)."),
 P("Scope variabel (shared / private)", h3),
 table([["Variabel","Scope","Keterangan"],
  ["N, T","shared","Konstanta masukan; hanya dibaca."],
  ["tid, n","private","Dideklarasikan di dalam blok parallel sehingga otomatis privat per thread."],
  ["rng (di dalam count_hits)","private","Variabel lokal fungsi, berada pada stack tiap thread; tidak pernah dibagi."],
  ["hits","reduction (private selama region, digabung di akhir)","Salinan privat per thread, dijumlahkan oleh runtime saat <i>implicit barrier</i> di akhir region."]],
  [4.2*cm, 4.6*cm, 7.2*cm]),
 Spacer(1,6),
 P("2.4 Kebijakan RNG per Thread (Berlaku untuk Kedua Versi)", h2),
 P("Seed thread ke-t dihitung sebagai <font name='Mono'>seed = 42 XOR ((t+1) × 0xD1B54A32D192ED03)</font>, kemudian diperluas menjadi 4 × 64 bit state dengan SplitMix64. Konstanta pengali yang besar dan ganjil memastikan seed antar thread berbeda jauh dalam representasi bit, dan SplitMix64 (fungsi <i>mixing</i> yang kuat) menghilangkan korelasi di antara state awal. Dengan demikian aliran acak antar thread praktis independen. Perlu dicatat bahwa pendekatan seed-berbeda tidak menjamin secara matematis bahwa aliran tidak bertumpang tindih; pendekatan yang lebih ketat adalah memakai fungsi <i>jump()</i> pada xoshiro yang melompat 2¹²⁸ langkah. Untuk 10⁹ sampel dalam ruang periode 2²⁵⁶ kemungkinan tumpang tindih dapat diabaikan, dan trade-off ini dicatat sebagai keterbatasan."),
 PageBreak()]

# 3. Hasil
S += [P("3. HASIL PENGUJIAN", h1), P("3.1 Lingkungan Pengujian", h2),
 table([["Komponen","Spesifikasi"],
  ["Prosesor", "AMD Ryzen 5 7535HS with Radeon Graphics, 3,30 GHz (hingga 4,55 GHz)"],
  ["Core fisik / thread logis", "6 core fisik / 12 thread logis (SMT)"],
  ["RAM", "16 GB DDR5"],
  ["Sistem operasi", "Windows 11 Home (64-bit) + MSYS2 / MinGW-w64 (UCRT64)"],
  ["Kompilator", "gcc (Rev6, Built by MSYS2 project) 16.2.0; flag <font name='Mono'>-O2 -Wall -Wextra -std=c11 -D_GNU_SOURCE -fopenmp -pthread -lm</font>"],
  ["Parameter", "N = 10⁹ titik, seed dasar 42, T ∈ {1, 2, 4, 8}, tiap konfigurasi diulang 3 kali dan dirata-rata"]],
  [4.5*cm, 11.5*cm]),
 Spacer(1,8),
 P("Waktu diukur dengan timer monotonic (<font name='Mono'>clock_gettime(CLOCK_MONOTONIC)</font> pada Linux, <font name='Mono'>QueryPerformanceCounter</font> pada Windows) hanya di sekitar bagian komputasi (pembuatan thread hingga reduction selesai); pencetakan hasil tidak ikut diukur."),
 P("3.2 Verifikasi Correctness", h2),
 P("Verifikasi dilakukan dengan skrip <font name='Mono'>verify.sh</font> (N = 10⁷) yang membandingkan jumlah <i>hits</i> antar versi. Kriteria: (i) serial = Pthreads (T=1) = OpenMP (T=1); (ii) Pthreads = OpenMP untuk setiap T. Karena kerja dan seed identik, kesamaan harus persis, bukan hanya mendekati."),
 table([["Versi","Hits (N = 10⁷)","Status"],
  ["Serial","7.854.510","Baseline"],
  ["Pthreads / OpenMP, T=1","7.854.510 / 7.854.510","Sama dengan serial"],
  ["Pthreads / OpenMP, T=2","7.854.656 / 7.854.656","Pthreads = OpenMP"],
  ["Pthreads / OpenMP, T=4","7.852.181 / 7.852.181","Pthreads = OpenMP"],
  ["Pthreads / OpenMP, T=8","7.852.630 / 7.852.630","Pthreads = OpenMP"]],
  [5.2*cm, 6.0*cm, 4.8*cm]),
 P("Keluaran <font name='Mono'>verify.sh</font> (N = 10⁷) pada mesin pengujian (Windows 11, MinGW-w64):"),
 C("""
serial            hits=7854510
T=1 pthread=7854510 openmp=7854510 -> OK
T=2 pthread=7854656 openmp=7854656 -> OK
T=4 pthread=7852181 openmp=7852181 -> OK
T=8 pthread=7852630 openmp=7852630 -> OK
SEMUA TES LULUS
"""),
 P("Jumlah <i>hits</i> pada mesin pengujian <b>identik</b> dengan hasil pada Linux (tabel di atas), sehingga program bersifat deterministik dan portabel lintas sistem operasi dan kompilator."),
 P("Hasil <i>hits</i> untuk T &gt; 1 berbeda dari serial. Ini <b>bukan kesalahan</b>: dengan T thread, sampel berasal dari T aliran RNG berbeda, bukan satu aliran panjang. Hasilnya tetap deterministik dan dapat direproduksi untuk T tertentu, dan kebenarannya dinilai secara statistik (Subbab 3.5), bukan identitas bit terhadap serial. Estimasi π untuk semua baris di atas berkisar 3,1409–3,1419, konsisten dengan galat standar ≈ 5,2 × 10⁻⁴ pada N = 10⁷. Perlu diakui bahwa uji ini tidak dapat mendeteksi <i>race condition</i> yang bermanifestasi sebagai hasil acak berbeda tiap run; karena tidak ada variabel yang ditulis bersama, desainnya aman secara konstruksi, dan hasil identik antar run berulang menjadi bukti pendukung."),
 P("3.3 Tabel Pengukuran Waktu Eksekusi", h2)]

if have_sum:
    rows = [["Implementasi","Thread","Waktu rata-rata (s)","Std (s)","Speedup","Efficiency"]]
    rows.append(["Serial","1",fmt(t_serial),"-","1,00","1,00"])
    for _, r in summ.sort_values(["threads","impl"], ascending=[True, False]).iterrows():
        rows.append([NM[r.impl], int(r.threads), fmt(r.time), fmt(r["std"]) if pd.notna(r["std"]) else "-",
                     f"{r.speedup:.2f}".replace(".",","), f"{r.efficiency:.2f}".replace(".",",")])
else:
    rows = [["Implementasi","Thread","Waktu rata-rata (s)","Std (s)","Speedup","Efficiency"], ["Serial","1",TODO("detik"),"-","1,00","1,00"]]
    for T in (1,2,4,8):
        for im in ("Pthreads","OpenMP"):
            rows.append([im, T, TODO("detik"), TODO("std"), TODO("S"), TODO("E")])
S += [table(rows, [3.0*cm,1.8*cm,3.6*cm,2.2*cm,2.7*cm,2.7*cm]),
 P("Tabel 1. Waktu eksekusi N = 10⁹ (rata-rata 3 kali run). Speedup S(T) = T<sub>serial</sub> / T<sub>paralel</sub>(T); Efficiency E(T) = S(T) / T.", cap)]

S.append(P("3.4 Grafik Speedup &amp; Efficiency", h2))
if os.path.exists("speedup_efficiency.png"):
    S += [Image("speedup_efficiency.png", width=15.5*cm, height=15.5*cm*4/11),
          P("Gambar 1. Speedup (kiri, garis putus-putus = ideal) dan Efficiency (kanan) terhadap jumlah thread.", cap)]
else:
    S += [table([[TODO("sisipkan speedup_efficiency.png hasil <b>python3 plot.py</b> setelah <b>make bench</b>")]],[16*cm],header=False),
          P("Gambar 1. Speedup dan Efficiency terhadap jumlah thread.", cap)]
S += [P("3.5 Pengujian Variasi Thread dan Akurasi Statistik", h2),
 P("Selain waktu, dikaji hubungan antara jumlah sampel/thread dan akurasi. Eksperimen berikut dijalankan dengan seed tetap (42) dan ditampilkan apa adanya."),
 table([["N","Hits","π̂","Galat |π̂ − π|","Galat standar teoretis 1,642/√N"]] +
  [[f"{int(r.N):,}".replace(",","."), f"{int(r.hits):,}".replace(",","."), f"{r.pi:.6f}".replace(".",","), f"{r.error:.2e}".replace(".",","), f"{1.6422/math.sqrt(r.N):.2e}".replace(".",",")] for r in accN.itertuples()],
  [2.8*cm,3.0*cm,2.8*cm,3.0*cm,4.4*cm]),
 P("Tabel 2. Akurasi terhadap N (serial).", cap),
 Image("accuracy_vs_N.png", width=11*cm, height=11*cm*3.3/5.6), P("Gambar 2. Galat terukur terhadap galat standar teoretis (skala log-log).", cap),
 table([["Thread","Hits (N = 10⁸)","π̂","Galat |π̂ − π|"]] +
  [[str(int(r.threads)), f"{int(r.hits):,}".replace(",","."), f"{r.pi:.6f}".replace(".",","), f"{r.error:.2e}".replace(".",",")] for r in accT.itertuples()],
  [2.8*cm,4.5*cm,4.0*cm,4.0*cm]),
 P("Tabel 3. Akurasi terhadap jumlah thread pada total sampel tetap N = 10⁸ (Pthreads).", cap),
 P("<b>Pengamatan.</b> Galat terukur mengikuti tren penurunan 1/√N dan berada dalam kisaran beberapa kali galat standar teoretis pada semua N. Pada N = 10⁹ galat terukur 1,07 × 10⁻⁴ sekitar 2,1 kali galat standar (5,2 × 10⁻⁵); ini masih wajar secara statistik (kejadian dua sigma terjadi sekitar 4% dari run), tetapi karena hanya satu seed yang diuji, kesimpulan yang lebih kuat memerlukan pengulangan dengan beberapa seed. Pada Tabel 3, galat untuk T = 1, 2, 4, 8 bervariasi acak (2,1 × 10⁻⁵ hingga 2,3 × 10⁻⁴) tanpa tren monoton terhadap T. Ini sesuai teori: pada total sampel tetap, jumlah thread tidak mengubah galat standar; thread hanya mengubah <i>waktu</i>. Variasi antar baris adalah fluktuasi sampling dari aliran RNG yang berbeda."),
 PageBreak()]

# 4. Analisis Kritis
def kf(Sv, n): return (1/Sv - 1/n)/(1 - 1/n)
S += [P("4. ANALISIS KRITIS", h1), P("4.1 Perbandingan Kompleksitas Kode (LOC &amp; Maintenance)", h2),
 P("LOC dihitung dari baris kode efektif (tanpa baris kosong dan komentar) pada file utama tiap versi. File <font name='Mono'>common.h</font> (70 baris, termasuk blok kompatibilitas Windows) dan <font name='Mono'>report.h</font> (30 baris) dipakai bersama oleh semua versi sehingga tidak dihitung sebagai biaya paralelisasi."),
 table([["Versi","LOC efektif (file utama)","Tambahan vs serial","API / konsep yang harus dikelola"],
  ["Serial","11","-","-"],
  ["Pthreads","38","+27 (≈ 3,5 × serial)","pthread_t, pthread_create/join, struct argumen, padding cache line, alokasi array, penanganan error, reduction manual"],
  ["OpenMP","18","+7 (≈ 1,6 × serial)","satu pragma dengan clause; omp_get_thread_num"]],
  [2.4*cm,3.2*cm,3.4*cm,7.0*cm]),
 P("Tabel 4. Perbandingan LOC. Pthreads membutuhkan sekitar 3,9 kali tambahan kode dibanding OpenMP untuk fungsionalitas yang sama.", cap),
 P("Selisih ini kecil dalam angka absolut karena masalahnya sederhana, tetapi kualitatifnya penting. Pada Pthreads, programmer bertanggung jawab atas: membungkus argumen ke dalam struct dan <font name='Mono'>void*</font> (hilang <i>type safety</i>), siklus hidup thread (create/join dan kebocoran bila lupa join), pengecekan kegagalan <font name='Mono'>pthread_create</font>, alokasi dan pembebasan memori, serta reduction. Setiap bagian adalah titik potensi bug. Pada OpenMP, program serial tetap hampir utuh: bila direktif dihapus atau kompilator tidak mendukung OpenMP, program berjalan serial dengan hasil yang sama sehingga <b>jalur serial menjadi referensi uji bawaan</b>. Ini keunggulan <i>maintainability</i> yang nyata: pemeliharaan cukup membaca satu pragma, sedangkan versi Pthreads harus dibaca sebagai kode konkurensi penuh. Sebaliknya, kesederhanaan sintaks OpenMP menyembunyikan perilaku runtime (bagaimana reduction digabung, kapan thread dibuat, pengikatan thread ke core), sehingga bug scope atau sinkronisasi yang halus (mis. lupa <font name='Mono'>default(none)</font> dan variabel menjadi shared secara tersirat) dapat tidak terlihat."),
 P("4.2 Analisis Bottleneck (Hukum Amdahl)", h2),
 P("Hukum Amdahl menyatakan bahwa dengan fraksi paralel p, speedup maksimum pada n prosesor adalah S(n) = 1 / ((1 − p) + p/n). Pada program ini, bagian serial hanya: pembuatan/penggabungan thread, inisialisasi RNG, reduction T bilangan, dan pembacaan argumen. Biaya semuanya pada orde mikrodetik hingga milidetik, sedangkan loop utama 10⁹ iterasi berlangsung beberapa detik, sehingga p sangat dekat 1."),
 table([["p (fraksi paralel)","S(2)","S(4)","S(8)","S(∞)"]] +
  [[f"{p}"]+[f"{1/((1-p)+p/n):.2f}".replace(".",",") for n in (2,4,8)]+[f"{1/(1-p):,.0f}".replace(",",".")] for p in (0.9999, 0.999, 0.99)],
  [3.6*cm,2.6*cm,2.6*cm,2.6*cm,2.6*cm]),
 P("Tabel 5. Speedup teoretis Amdahl. Bahkan p = 0,99 (1% serial) hanya memberi S(8) ≈ 7,5, sehingga bila speedup terukur jauh di bawah ini, penyebabnya bukan fraksi serial program.", cap),
 P("Bila speedup terukur lebih rendah daripada ideal, <b>Hukum Amdahl bukan penjelasan utama</b> karena fraksi serial program ini hampir nol. Faktor pembatas yang lebih mungkin pada beban <i>compute-bound</i> seperti ini adalah:"),]
S += B(["<b>Jumlah core fisik vs thread logis.</b> Pada CPU dengan SMT/Hyper-Threading (mis. 4 core / 8 thread), dua thread berbagi satu core dan unit eksekusi yang sama. Loop xoshiro yang padat ALU hanya memperoleh tambahan throughput sekitar 10–30% dari thread SMT kedua, bukan 100%. Karena itu T = 8 pada mesin 4-core tidak akan mencapai speedup 8.",
        "<b>Frekuensi turbo yang turun.</b> Satu core aktif bisa berjalan pada frekuensi turbo tertinggi; semua core aktif memaksa frekuensi lebih rendah (dan <i>thermal throttling</i> pada laptop). Waktu serial pembanding menjadi 'lebih cepat per-core' daripada kondisi paralel penuh.",
        "<b>Gangguan sistem operasi dan proses latar.</b> Penjadwal dapat menempatkan dua thread pada core yang sama atau berbagi core dengan proses lain, terutama saat T sama dengan jumlah core logis.",
        "<b>Memory bandwidth bukan bottleneck.</b> Seluruh state berada di register dan L1, tidak ada lalu lintas memori yang berarti; ini diperkirakan membuat <i>scaling</i> lebih baik daripada program berbasis data besar seperti perkalian matriks."])
if have_sum:
    kfrows=[["Implementasi","T","Speedup","Efficiency","Karp-Flatt e"]]
    for _, r in summ.sort_values(["impl","threads"], ascending=[False, True]).iterrows():
        if r.threads>1 and r.speedup>=1: kfrows.append([NM[r.impl], int(r.threads), f"{r.speedup:.2f}".replace(".",","), f"{r.efficiency:.2f}".replace(".",","), f"{kf(r.speedup, r.threads):.4f}".replace(".",",")])
    S += [Spacer(1,4), P("Untuk mengukur fraksi serial <i>efektif</i> dari data nyata digunakan metrik Karp-Flatt: e = (1/S − 1/n) / (1 − 1/n). Nilai e yang kecil dan konstan terhadap n menandakan overhead kecil; e yang naik bersama n menandakan overhead yang tumbuh (kontensi, SMT, throttling)."),
          table(kfrows,[3.2*cm,1.6*cm,2.8*cm,2.8*cm,3.4*cm]), P("Tabel 6. Metrik Karp-Flatt (hanya konfigurasi dengan speedup ≥ 1).", cap),
          P("Nilai e berkisar 0,07–0,19 dan <b>tidak naik monoton</b> terhadap T: Pthreads 0,072 → 0,113 → 0,099, OpenMP 0,185 → 0,102 → 0,119. Jadi hilangnya efisiensi bukan akibat fraksi serial yang membesar bersama jumlah thread. Namun e ≈ 0,1 berarti 'serial efektif' sekitar 10%, jauh lebih besar daripada fraksi serial sebenarnya program ini (pembuatan thread dan reduction hanya mikro- hingga milidetik). Selisihnya berasal dari faktor non-algoritmik: derau pengukuran, frekuensi CPU pada laptop, dan SMT. Nilai e OpenMP pada T=2 (0,185) yang lebih tinggi daripada T=4 (0,102) bukan tanda overhead yang menurun, melainkan derau: waktu OpenMP T=2 (1,2225 s) memiliki simpangan baku 0,084 s dan baseline serial hanya diukur tiga kali.", body)]
else:
    S += [Spacer(1,4), P("Untuk mengukur fraksi serial <i>efektif</i> dari data nyata digunakan metrik Karp-Flatt: e = (1/S − 1/n) / (1 − 1/n). Nilai e yang kecil dan konstan terhadap n menandakan overhead kecil; e yang naik bersama n menandakan overhead yang tumbuh."),
          table([["Implementasi","T","Speedup","Efficiency","Karp-Flatt e"]]+[[im,T,TODO("S"),TODO("E"),TODO("e")] for im in ("Pthreads","OpenMP") for T in (2,4,8)],[3.2*cm,1.6*cm,2.8*cm,2.8*cm,3.4*cm]),
          P("Tabel 6. Metrik Karp-Flatt (hitung dari Tabel 1).", cap)]
S += [P("Perlu juga dicatat <b>Hukum Gustafson</b>: karena N dapat diperbesar mengikuti jumlah core (<i>scaled speedup</i>), masalah Monte Carlo hampir selalu <i>scalable</i>; yang dibatasi bukan paralelisme, tetapi perangkat keras. Tugas ini mengukur <i>strong scaling</i> (N tetap), yang lebih ketat dibanding weak scaling.", body),
 P("4.3 Pembahasan Anomali", h2),
 P("Bagian ini mencatat penyimpangan dari perilaku ideal pada data pengukuran, penyebab yang paling mungkin, dan cara memeriksanya."),
 P("<b>Anomali 1 – <i>Plateau</i> speedup pada T=8.</b> Speedup mencapai 4,72× (Pthreads) dan 4,37× (OpenMP) dari ideal 8×, dengan efficiency 0,59 dan 0,55; penskalaan dari T=1 ke T=4 jauh lebih baik (≈ 3×, efficiency 0,75–0,76). Prosesor memiliki 6 core fisik dan 12 thread logis, sehingga pada T=8 sebagian thread harus berbagi core fisik melalui SMT dan memperoleh throughput tambahan yang jauh di bawah satu core penuh, pada beban yang padat ALU seperti ini. Penurunan frekuensi turbo saat banyak core aktif pada laptop adalah faktor lain yang masuk akal. Kedua penjelasan ini <b>konsisten dengan data tetapi belum diisolasi</b> oleh pengukuran. Eksperimen pembuktian: ukur T=6 (jumlah core fisik) dan T=12 (jumlah thread logis), dan pantau frekuensi CPU selama benchmark."),
 P("<b>Anomali 2 – Simpangan pada T=1.</b> Pthreads T=1 (1,943 s) tampak 6% lebih cepat daripada serial (2,063 s), sedangkan OpenMP T=1 (2,294 s) 11% lebih lambat. Ini bukan <i>superlinear speedup</i>: pada satu thread tidak ada sumber percepatan. Selisih 0,12–0,23 s setara 1,5–3 kali simpangan baku (0,077 s) dan baseline serial hanya diukur tiga kali tanpa simpangan baku yang dilaporkan. Inisialisasi tim thread libgomp hanya berorde mikro- hingga milidetik sehingga tidak cukup untuk menjelaskan 0,23 s. Kandidat penyebab yang lebih masuk akal adalah derau dan keadaan termal/frekuensi laptop yang berbeda antar run, serta perbedaan kode mesin yang dihasilkan kompilator (loop pada fungsi serial vs fungsi <i>worker</i> vs region OpenMP). Pemeriksaan: ulangi minimal 10 kali dengan urutan acak, atur afinitas core, dan bandingkan assembly (<font name='Mono'>-S</font>)."),
 P("<b>Anomali 3 – Pthreads vs OpenMP tidak berbeda bermakna.</b> Selisih waktu keduanya (T=2: 1,105 vs 1,223 s; T=4: 0,690 vs 0,674 s; T=8: 0,437 vs 0,472 s) berada pada orde simpangan baku (0,004–0,084 s) dan arahnya berganti-ganti: Pthreads lebih cepat pada T=2 dan T=8, OpenMP pada T=4. Dengan tiga ulangan, selisih ini <b>tidak dapat disimpulkan</b> sebagai keunggulan salah satu pendekatan. Hasil ini sesuai ekspektasi, karena kedua versi menjalankan fungsi <font name='Mono'>count_hits()</font> yang sama dengan partisi dan seed yang sama, tanpa kontensi memori atau kunci di loop panas. Simpangan baku yang besar pada beberapa konfigurasi (mis. Pthreads T=4 0,004 s vs OpenMP T=4 0,054 s) menunjukkan derau penjadwalan di Windows pada laptop."),
 P("Daftar pemeriksaan umum untuk anomali sejenis:"),
 table([["Kemungkinan anomali","Penyebab","Cara memverifikasi"],
  ["Speedup T=8 jauh di bawah 8","Core fisik &lt; 8 (SMT), turbo turun, throttling.","<font name='Mono'>lscpu</font> (Core(s) per socket, Thread(s) per core); bandingkan T=4 dan T=8; pantau suhu/frekuensi."],
  ["Pthreads T=1 sedikit lebih lambat dari serial","Overhead create/join thread dan penyebaran data; juga optimasi kompilator berbeda pada loop dalam fungsi worker.","Bandingkan serial vs T=1; bandingkan hasil <font name='Mono'>-O2</font> vs <font name='Mono'>-O3</font>."],
  ["OpenMP T=1 berbeda dari serial","Inisialisasi runtime libgomp (pembuatan thread pool) dihitung pada run pertama.","Jalankan satu run <i>warm-up</i> yang dibuang."],
  ["Pthreads vs OpenMP selisih kecil (&lt; 2–3%)","Keduanya menjalankan loop yang sama; selisih mayoritas berasal dari derau pengukuran.","Periksa simpangan baku; bila selisih &lt; std maka tidak signifikan."],
  ["Std besar / satu run outlier","Proses latar, penjadwal, throttling.","Naikkan jumlah ulangan; laporkan median selain rata-rata."],
  ["Speedup &gt; T (superlinear)","Hampir tidak mungkin pada beban ini (tidak ada efek cache); biasanya artefak turbo/pengukuran serial yang lambat.","Ukur ulang serial setelah mesin dingin."]],
  [4.2*cm,5.6*cm,6.2*cm]),
 Spacer(1,6),
 P("Satu anomali lain dari eksperimen akurasi (Subbab 3.5): galat pada N = 10⁹ sekitar 2,1 kali galat standar teoretis. Secara statistik masih wajar (peluang ≈ 4% untuk |z| ≥ 2,1), tetapi hanya satu seed yang diuji sehingga dianjurkan mengulang dengan beberapa seed.", body),
 P("4.4 <i>Trade-off</i> Jumlah Thread vs Akurasi Statistik", h2),
 P("Galat standar estimator hanya bergantung pada N total: SE = 4√(p(1−p)/N) ≈ 1,642/√N dengan p = π/4. Jumlah thread <b>tidak</b> memperbaiki akurasi; ia hanya memperpendek waktu untuk mencapai akurasi tersebut. Dengan anggaran waktu tetap, T thread memungkinkan sekitar T × lebih banyak sampel sehingga galat turun sekitar 1/√T (Hukum Gustafson). Misalnya 8 thread dengan waktu sama menghasilkan galat ≈ 2,8 kali lebih kecil, bukan 8 kali. Trade-off lain muncul pada kualitas RNG: bila aliran antar thread berkorelasi (mis. seed berurutan pada generator lemah, atau RNG global yang dilock sehingga ada urutan non-deterministik), sampel efektif lebih sedikit daripada N dan galat nyata lebih besar dari 1/√N. Itu sebabnya RNG privat dengan seed terpisah dan pencampuran SplitMix64 dipakai di sini. Tabel 3 mendukung hal ini: galat pada N tetap bervariasi acak terhadap T tanpa tren monoton."),
 P("4.5 <i>Trade-off</i> Kemudahan vs Kontrol", h2),
 table([["Aspek","Pthreads","OpenMP"],
  ["Kemudahan menulis","Rendah: semua manajemen thread manual","Tinggi: 1 pragma, jalur serial tetap utuh"],
  ["Kontrol partisi &amp; scheduling","Penuh: bentuk apa pun (pool, work-stealing)","Terbatas pada schedule(static/dynamic/guided), task"],
  ["Sinkronisasi","Mutex, condvar, barrier, atomics, semaphore, bebas memilih","critical, atomic, barrier, reduction; lebih ringkas, kurang fleksibel"],
  ["Risiko bug","Tinggi (leak, deadlock, lupa join, salah pointer argumen)","Lebih rendah, tetapi scope tersirat dan data race tetap mungkin"],
  ["Portabilitas","POSIX (Linux/macOS; Windows lewat pustaka tambahan)","Lintas platform lewat kompilator yang mendukung OpenMP"],
  ["Kinerja (beban reguler)","Setara bila dirancang benar","Setara; runtime telah dioptimasi (thread pool)"],
  ["Cocok untuk","Struktur konkurensi tak beraturan, server, pipeline","Paralelisme data/loop pada komputasi numerik"]],
  [3.6*cm,6.2*cm,6.2*cm]),
 P("Tabel 7. Ringkasan trade-off.", cap),
 P("Untuk Monte Carlo, kontrol ekstra Pthreads tidak memberi keuntungan kinerja karena beban seragam dan pembagian statis sudah optimal. Satu-satunya keunggulan Pthreads di sini adalah transparansi: setiap detail (padding, join sebagai barrier, reduction) terlihat dan dapat dijelaskan, sehingga baik secara edukatif. Untuk rekayasa nyata, OpenMP memberikan hasil sama dengan usaha jauh lebih kecil."),
 PageBreak()]

# 5. Kesimpulan
S += [P("5. KESIMPULAN", h1), P("5.1 Rekomendasi Penggunaan Pthreads vs OpenMP", h2)]
S += B(["<b>Gunakan OpenMP</b> untuk paralelisme data berbasis loop pada komputasi numerik seperti Monte Carlo, perkalian matriks, dan konvolusi: kodenya lebih pendek (18 vs 38 LOC pada program ini), jalur serial tetap tersedia sebagai referensi uji, dan risiko bug kinerja lebih rendah. dan, pada pengukuran ini, kinerjanya setara dengan Pthreads (T=8: 0,47 s vs 0,44 s, selisih dalam kisaran simpangan baku).",
        "<b>Gunakan Pthreads</b> bila memerlukan kontrol penuh atas siklus hidup thread, pola sinkronisasi khusus (producer-consumer, pool, pipeline), prioritas atau afinitas, atau bila lingkungan tidak menyediakan kompilator OpenMP.",
        "Apa pun pendekatannya: gunakan RNG privat per thread dengan generator berkualitas, hindari kunci pada jalur panas, gunakan reduction, dan waspadai false sharing."])
S += [P("5.2 Pembelajaran yang Didapat", h2)]
S += B([ "Pengukuran jangka pendek pada laptop bersifat berderau: dengan tiga ulangan, selisih beberapa persen antar implementasi tidak dapat dibedakan dari derau, dan baseline serial perlu diulang lebih banyak (serta dilaporkan simpangan bakunya).",
        "Race condition pada akumulator dihilangkan dengan struktur data (hasil per thread + join/reduction), bukan dengan kunci di loop.",
        "Menyamakan partisi dan seed antar implementasi membuat verifikasi correctness bersifat tepat (bit-per-bit), sehingga perbandingan kinerja menjadi adil.",
        "Akurasi Monte Carlo ditentukan oleh N total (≈ 1/√N), bukan jumlah thread; paralelisasi memberi lebih banyak sampel per satuan waktu.",
        "Speedup nyata dibatasi perangkat keras (core fisik, SMT, turbo), bukan oleh fraksi serial program, karena p mendekati 1; metrik Karp-Flatt berguna untuk mendiagnosis hal ini.",
        "Kualitas RNG adalah bagian dari correctness program paralel: RNG global berkunci lambat dan mengganggu independensi sampel."])
S += [P("Keterbatasan: pengujian memakai satu seed dasar dan satu mesin; pembangkitan seed per thread tidak menjamin ketiadaan tumpang tindih aliran secara matematis (jump function xoshiro dapat dipakai); dan pengukuran bergantung pada kondisi termal serta beban sistem saat pengujian.", body), PageBreak()]

# 6. Pustaka
refs = [
 "Amdahl, G. M. (1967). Validity of the single processor approach to achieving large scale computing capabilities. <i>Proceedings of the AFIPS Spring Joint Computer Conference</i>, 30, 483–485.",
 "Blackman, D., &amp; Vigna, S. (2021). Scrambled linear pseudorandom number generators. <i>ACM Transactions on Mathematical Software</i>, 47(4), 1–32.",
 "Butenhof, D. R. (1997). <i>Programming with POSIX Threads</i>. Addison-Wesley.",
 "Chapman, B., Jost, G., &amp; van der Pas, R. (2008). <i>Using OpenMP: Portable Shared Memory Parallel Programming</i>. MIT Press.",
 "Gustafson, J. L. (1988). Reevaluating Amdahl's law. <i>Communications of the ACM</i>, 31(5), 532–533.",
 "Karp, A. H., &amp; Flatt, H. P. (1990). Measuring parallel processor performance. <i>Communications of the ACM</i>, 33(5), 539–543.",
 "Metropolis, N., &amp; Ulam, S. (1949). The Monte Carlo method. <i>Journal of the American Statistical Association</i>, 44(247), 335–341.",
 "OpenMP Architecture Review Board. (2021). <i>OpenMP Application Programming Interface, Version 5.2</i>. https://www.openmp.org",
 "Pacheco, P. S., &amp; Malensek, M. (2021). <i>An Introduction to Parallel Programming</i> (2nd ed.). Morgan Kaufmann.",
 "Steele, G. L., Lea, D., &amp; Flood, C. H. (2014). Fast splittable pseudorandom number generators. <i>Proceedings of OOPSLA 2014</i>, 453–472.",
 "The Open Group. (2018). <i>POSIX.1-2017 (IEEE Std 1003.1-2017): pthread.h</i>. https://pubs.opengroup.org/onlinepubs/9699919799/",
]
S += [P("6. DAFTAR PUSTAKA", h1)] + [Paragraph(f"[{i}] {r}", ParagraphStyle("ref", parent=body, leftIndent=22, firstLineIndent=-22, alignment=0)) for i, r in enumerate(refs, 1)]

# ---------- build ----------
def footer(c, d):
    c.saveState(); c.setFont("Serif", 8.5)
    if d.page > 1: c.drawCentredString(A4[0]/2, 1.3*cm, f"{d.page}")
    c.setFont("Serif-I", 8); 
    if d.page > 1: c.drawString(2.3*cm, A4[1]-1.5*cm, f"Komputasi Paralel – Tugas M6 | {NAMA} ({NIM})")
    c.restoreState()
doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=2.3*cm, rightMargin=2.3*cm, topMargin=2.2*cm, bottomMargin=2.0*cm,
                      title="Laporan Tugas M6 - Pthreads vs OpenMP Monte Carlo Pi", author=NAMA)
doc.addPageTemplates([PageTemplate(id="p", frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")], onPage=footer)])
doc.build(S); print("OK ->", OUT)
