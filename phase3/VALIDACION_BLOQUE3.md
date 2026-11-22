# Validación del bloque 3

Barrido `e81ec15bbc1df520`: N=3 y N=4, ω=1, P=4, siete valores de β entre 0.5 y 5; tres semillas por punto, 4000 mediciones y 500 barridos descartados por semilla.

| N | β | clases visitadas por réplica | mayor residuo de clase | válido |
|---:|---:|---|---:|---|
| 3 | 0.500 | [3, 3, 3] | 1.46 σ | sí |
| 3 | 0.734 | [3, 3, 3] | 0.36 σ | sí |
| 3 | 1.077 | [3, 3, 3] | 0.53 σ | sí |
| 3 | 1.581 | [3, 3, 3] | 0.97 σ | sí |
| 3 | 2.321 | [3, 3, 3] | 1.82 σ | sí |
| 3 | 3.406 | [3, 3, 3] | 1.34 σ | sí |
| 3 | 5.000 | [3, 3, 3] | 0.30 σ | sí |
| 4 | 0.500 | [5, 5, 5] | 2.49 σ | sí |
| 4 | 0.734 | [5, 5, 5] | 1.11 σ | sí |
| 4 | 1.077 | [5, 5, 5] | 0.54 σ | sí |
| 4 | 1.581 | [5, 5, 5] | 2.69 σ | sí |
| 4 | 2.321 | [5, 5, 5] | 1.51 σ | sí |
| 4 | 3.406 | [5, 5, 5] | 1.12 σ | sí |
| 4 | 5.000 | [5, 5, 5] | 0.94 σ | sí |

Las probabilidades de clases y de pertenencia de una partícula suman uno en cada temperatura (desviación numérica máxima menor que 2×10⁻¹⁴). Los residuos máximos de las clases son 1.82 σ para N=3 y 2.69 σ para N=4. Los residuos máximos de energía termodinámica son 2.55 σ y 1.56 σ, respectivamente.

Los criterios operativos del pipeline exigen cambios y visita de todas las clases por réplica, barras no nulas y acuerdo con el control exacto dentro de cuatro errores estimados. Esto comprueba el barrido realizado; no sustituye un estudio sistemático del tiempo de autocorrelación o del coste computacional.

Series crudas, parámetros y resultados: `data/e81ec15bbc1df520`. Gráficas: `plots/e81ec15bbc1df520`.
