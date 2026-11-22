# Auditoría adicional de las cadenas de la Fase 3

Se calcularon las transiciones a partir de `class_ids` guardados en cada
archivo `.npz`. Una transición es un cambio efectivo de clase entre dos
mediciones sucesivas. Las permanencias cuentan barridos consecutivos
en la misma clase. La discrepancia entre mitades usa errores de
autocorrelación de cada mitad; es un diagnóstico, no una prueba formal
de estacionariedad. Los ciclos muy raros pueden carecer de resolución.

## Corrida `f58f237895157d1b`

| N | β | mínimo de salidas por clase y réplica | permanencia máxima | diferencia máxima entre mitades | τ energía entre réplicas | corr(Etermo,Evirial) |
|---:|---:|---|---:|---:|---:|---:|
| 3 | 0.1 | [98, 104, 6] | 175 | 1.35σ | 0.55 ± 0.05 | 0.490 |
| 3 | 1 | [369, 758, 388] | 27 | 3.67σ | 0.58 ± 0.04 | 0.407 |
| 3 | 10 | [604, 1899, 1255] | 4 | 1.33σ | 0.51 ± 0.01 | 0.004 |
| 4 | 0.1 | [76, 101, 19, 7, 2] | 214 | 2.48σ | 0.60 ± 0.07 | 0.508 |
| 4 | 1 | [144, 538, 507, 141, 270] | 24 | 1.66σ | 0.64 ± 0.04 | 0.391 |
| 4 | 10 | [145, 945, 1242, 464, 916] | 4 | 1.54σ | 0.51 ± 0.01 | 0.008 |

## Corrida `7837d0146dbd1097`

| N | β | mínimo de salidas por clase y réplica | permanencia máxima | diferencia máxima entre mitades | τ energía entre réplicas | corr(Etermo,Evirial) |
|---:|---:|---|---:|---:|---:|---:|
| 3 | 1 | [1171, 2392, 1195] | 24 | 1.69σ | 0.63 ± 0.02 | 0.407 |

La dispersión de τ entre tres réplicas es descriptiva; no constituye
un intervalo de confianza preciso. Las energías termodinámica y
virial se miden en las mismas configuraciones, por lo que su
correlación impide contarlas como controles estadísticos independientes.
