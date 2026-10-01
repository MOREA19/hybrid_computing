# Tabel B3

Median dan std dihitung dari lima pengulangan setelah satu warm-up. Speedup memakai baseline 1 rank untuk mode yang sama. Rasio process/thread adalah median process dibagi median thread; nilai di atas 1 berarti process lebih lambat.

| Mode | MPI ranks | Workers/rank | Median waktu maks (s) | Std (s) | Speedup vs 1 rank mode sama | Rasio process/thread |
|:---|---:|---:|---:|---:|---:|---:|
| process | 1 | 4 | 0.221649 | 0.004168 | 1.000 | 1.577 |
| thread | 1 | 4 | 0.140518 | 0.005777 | 1.000 | 1.577 |
| process | 2 | 4 | 0.238755 | 0.003166 | 0.928 | 2.953 |
| thread | 2 | 4 | 0.080853 | 0.002803 | 1.738 | 2.953 |
| process | 4 | 4 | 0.407472 | 0.018096 | 0.544 | 7.876 |
| thread | 4 | 4 | 0.051737 | 0.000884 | 2.716 | 7.876 |

![Perbandingan waktu B3 dengan simpangan baku](b3_compare.png)
