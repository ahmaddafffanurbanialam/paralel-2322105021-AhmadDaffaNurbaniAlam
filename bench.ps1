# bench.ps1 - Compile + verifikasi + benchmark Monte Carlo pi (Windows / PowerShell, butuh gcc MinGW-w64)
# Jalankan: powershell -ExecutionPolicy Bypass -File .\bench.ps1
$N = 1000000000
$REPS = 3
gcc -O2 -std=gnu11 -o pi_serial.exe  pi_serial.c  -lm;          if ($LASTEXITCODE -ne 0) { throw "gagal compile serial" }
gcc -O2 -std=gnu11 -pthread -o pi_pthread.exe pi_pthread.c -lm; if ($LASTEXITCODE -ne 0) { throw "gagal compile pthread" }
gcc -O2 -std=gnu11 -fopenmp -o pi_openmp.exe  pi_openmp.c  -lm; if ($LASTEXITCODE -ne 0) { throw "gagal compile openmp" }

$V = 10000000
$s = (.\pi_serial.exe $V --csv).Split(",")[3]
Write-Host "serial hits=$s"
foreach ($T in 1,2,4,8) {
    $p = (.\pi_pthread.exe $V $T --csv).Split(",")[3]
    $o = (.\pi_openmp.exe  $V $T --csv).Split(",")[3]
    $ok = if ($p -eq $o) { "OK" } else { "BEDA" }
    if ($T -eq 1 -and $p -ne $s) { $ok = "BEDA-DARI-SERIAL" }
    Write-Host "T=$T pthread=$p openmp=$o -> $ok"
}

"impl,threads,N,hits,pi,error,time" | Out-File results.csv -Encoding ascii
for ($r = 1; $r -le $REPS; $r++) {
    Write-Host "Ulangan $r / $REPS"
    .\pi_serial.exe $N --csv | Add-Content results.csv -Encoding ascii
    foreach ($T in 1,2,4,8) {
        .\pi_pthread.exe $N $T --csv | Add-Content results.csv -Encoding ascii
        .\pi_openmp.exe  $N $T --csv | Add-Content results.csv -Encoding ascii
    }
}
Write-Host "Selesai -> results.csv"
