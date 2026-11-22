# Auditoría cuantitativa del cierre de Fase 3

Los valores de esta página se generan de los resúmenes guardados, sin editar cifras a mano.
Barrido térmico: `f58f237895157d1b`. Estudio de P y coste: `study_closure.json`.

## Barrido térmico y normalización

| N | β | clases resueltas | máximo residuo resuelto | Z_MC/Z_ocup | residuo Z | ESS energía/s |
|---:|---:|---:|---:|---:|---:|---:|
| 3 | 0.1 | 2/3 | 0.20σ | 0.9982 | -0.17σ | 509.0 |
| 3 | 1 | 3/3 | 0.83σ | 1.0011 | +0.03σ | 499.7 |
| 3 | 10 | 3/3 | 0.13σ | 1.0001 | +0.00σ | 640.1 |
| 4 | 0.1 | 4/5 | 0.46σ | 1.0037 | +0.15σ | 429.5 |
| 4 | 1 | 5/5 | 0.73σ | 1.0036 | +0.05σ | 440.0 |
| 4 | 10 | 5/5 | 0.55σ | 0.9691 | -0.57σ | 480.9 |

En β=0.1, las clases de ciclo más largo no alcanzaron el umbral de 20 apariciones por réplica; sus puntos se muestran como exploratorios. La prueba independiente del factor 1/N! procede del producto de ocupaciones y de la suma directa de estados de Fock, no de la reconstrucción MC.

## Corrida de seguimiento para N=3, β=1

Una réplica corta mostró una diferencia de 3.67 errores entre mitades en el indicador del ciclo de longitud tres. Se repitió el punto con 12000 mediciones y 2000 barridos descartados por cada una de tres cadenas. El resultado fue p(3)=0.17894 ± 0.00540, frente a 0.18219 exacto. Z_MC/Z_ocup=0.9860. La mayor diferencia entre mitades en esta repetición fue 1.69 errores. Los errores de ambas comparaciones incluyen autocorrelación de cada mitad.

## Dependencia con P

| N | β | P | ciclo largo MC ± error | exacto | energía MC ± error | ESS energía/s |
|---:|---:|---:|---:|---:|---:|---:|
| 3 | 0.5 | 2 | 0.0820 ± 0.0044 | 0.0829 | 5.0729 ± 0.0589 | 290.1 |
| 3 | 0.5 | 4 | 0.0740 ± 0.0069 | 0.0829 | 5.1454 ± 0.0938 | 324.9 |
| 3 | 0.5 | 8 | 0.0776 ± 0.0071 | 0.0829 | 5.1926 ± 0.1048 | 304.2 |
| 3 | 0.5 | 16 | 0.0888 ± 0.0099 | 0.0829 | 4.9122 ± 0.1328 | 234.8 |
| 3 | 1 | 2 | 0.1805 ± 0.0065 | 0.1822 | 2.5472 ± 0.0361 | 459.4 |
| 3 | 1 | 4 | 0.1756 ± 0.0111 | 0.1822 | 2.6052 ± 0.0388 | 297.3 |
| 3 | 1 | 8 | 0.1791 ± 0.0097 | 0.1822 | 2.5491 ± 0.0496 | 363.7 |
| 3 | 1 | 16 | 0.1803 ± 0.0107 | 0.1822 | 2.5313 ± 0.0689 | 317.6 |
| 3 | 5 | 2 | 0.3356 ± 0.0056 | 0.3311 | 1.5081 ± 0.0014 | 808.4 |
| 3 | 5 | 4 | 0.3288 ± 0.0062 | 0.3311 | 1.5122 ± 0.0044 | 678.2 |
| 3 | 5 | 8 | 0.3299 ± 0.0109 | 0.3311 | 1.5137 ± 0.0095 | 549.9 |
| 3 | 5 | 16 | 0.3361 ± 0.0205 | 0.3311 | 1.5109 ± 0.0103 | 365.8 |
| 4 | 0.5 | 2 | 0.0497 ± 0.0044 | 0.0483 | 6.1174 ± 0.0829 | 378.3 |
| 4 | 0.5 | 4 | 0.0465 ± 0.0072 | 0.0483 | 6.1833 ± 0.1735 | 289.3 |
| 4 | 0.5 | 8 | 0.0476 ± 0.0062 | 0.0483 | 6.2890 ± 0.1168 | 283.1 |
| 4 | 0.5 | 16 | 0.0536 ± 0.0098 | 0.0483 | 6.2190 ± 0.1548 | 250.0 |
| 4 | 1 | 2 | 0.1300 ± 0.0065 | 0.1298 | 3.1547 ± 0.0304 | 421.6 |
| 4 | 1 | 4 | 0.1179 ± 0.0075 | 0.1298 | 3.1803 ± 0.0426 | 397.8 |
| 4 | 1 | 8 | 0.1273 ± 0.0088 | 0.1298 | 3.0696 ± 0.0576 | 352.2 |
| 4 | 1 | 16 | 0.1328 ± 0.0128 | 0.1298 | 3.0874 ± 0.1202 | 239.0 |
| 4 | 5 | 2 | 0.2508 ± 0.0068 | 0.2483 | 2.0101 ± 0.0015 | 744.1 |
| 4 | 5 | 4 | 0.2439 ± 0.0060 | 0.2483 | 2.0009 ± 0.0040 | 587.8 |
| 4 | 5 | 8 | 0.2481 ± 0.0079 | 0.2483 | 2.0097 ± 0.0071 | 440.8 |
| 4 | 5 | 16 | 0.2624 ± 0.0118 | 0.2483 | 1.9989 ± 0.0164 | 292.5 |

## Actualización global frente a local

| N | método | ciclo largo MC ± error | ESS energía/s | aceptación de permutación |
|---:|---|---:|---:|---:|
| 3 | global | 0.1756 ± 0.0111 | 297.3 | 0.404 |
| 3 | local | 0.1900 ± 0.0080 | 204.8 | 0.409 |
| 4 | global | 0.1179 ± 0.0075 | 397.8 | 0.406 |
| 4 | local | 0.1253 ± 0.0074 | 130.7 | 0.407 |
