# Guía de todas las figuras

Todos los comandos de esta página se ejecutan desde la **raíz** del
repositorio, con el entorno Python activado. `paper/generar_figuras.py`
consulta únicamente los archivos guardados que se indican; no lanza PIMC.
El resultado se guarda en `paper/figuras/<nombre>.pdf`. Para una figura
cualquiera, la forma exacta es:

```bash
python paper/generar_figuras.py --figure NOMBRE.pdf
```

Con `python paper/generar_figuras.py` se generan las doce. Con `--list`
se imprimen los nombres admitidos. Seaborn usa contexto `paper`; Matplotlib
embebe fuentes TrueType en los PDF. Los paneles no contienen `plt.title()`:
el significado físico, las condiciones y las limitaciones están en los pies
de figura de `paper/paper.tex`.

## Figuras del artículo principal

| Nº | Nombre que se pasa a `--figure` | Qué representa | Datos Monte Carlo guardados |
|---:|---|---|---|
| 1 | `exchange_cycles.pdf` | Probabilidad del ciclo completo para `N=2,3,4` frente a `βħω`. Se omiten puntos de ciclos raros que no cumplen el umbral. | Fase 2 `7a2a04b53b62f674`; Fase 3 `e81ec15bbc1df520`, `f58f237895157d1b` y repetición larga `7837d0146dbd1097`. |
| 2 | `partition_check.pdf` | Cociente entre `Z_N` reconstruida desde la fracción del sector identidad y la referencia independiente de ocupaciones, para `N=3,4`. | Fase 3 `f58f237895157d1b` y repetición larga `7837d0146dbd1097`. |
| 3 | `energy_control.pdf` | Energía termodinámica para `N=3,4`, con curvas exactas de la base de ocupaciones. | Fase 3 `e81ec15bbc1df520`, `f58f237895157d1b`, `7837d0146dbd1097`. |
| 4 | `class_probabilities_N4.pdf` | Las cinco clases de permutación de cuatro bosones, curvas canónicas y puntos PIMC. | Los mismos tres resúmenes de Fase 3 de la figura 3. |
| 5 | `p_convergence.pdf` | Comparación de ciclos completos al variar `P=2,4,8,16` para tres temperaturas. El núcleo de Mehler evita sesgo de Trotter. | `phase3/study_closure.json`. |

## Figuras de los anexos del mismo PDF

| Nº | Nombre que se pasa a `--figure` | Qué representa | Datos o construcción |
|---:|---|---|---|
| 6 | `worldline_topology.pdf` | Esquema de cierre identidad y transposición; **no** son trayectorias medidas. | Dibujo determinista de `worldline_topology()`; no requiere resumen MC. |
| 7 | `phase2_partition_ratio.pdf` | `Z_2` reconstruida y razón intercambio/identidad `R`; ambos paneles derivan de la misma fracción y están correlacionados. | `phase2/data/7a2a04b53b62f674/summary.json`. |
| 8 | `phase2_energy.pdf` | Energía de dos bosones, PIMC y control exacto. | Mismo resumen de Fase 2. |
| 9 | `class_probabilities_N3.pdf` | Las tres clases de permutación de tres bosones. | Los tres resúmenes de Fase 3 de la figura 3. |
| 10 | `class_histograms.pdf` | Barras canónicas y puntos PIMC para `N=3,4` cerca de `βħω=1.077`. | Barrido histórico `e81ec15bbc1df520`. |
| 11 | `particle_cycle_fractions.pdf` | Probabilidad de que una partícula elegida al azar pertenezca a un ciclo de longitud `ℓ`, para `N=3,4`. | Los tres resúmenes de Fase 3 de la figura 3. |
| 12 | `sampling_cost.pdf` | Muestras efectivas de energía por segundo frente a `P` y frente al tipo de actualización. Es una comparación descriptiva dependiente del equipo. | `phase3/study_closure.json`. |

Ejemplo completo para regenerar solo las figuras 2 y 12:

```bash
python paper/generar_figuras.py --figure partition_check.pdf --figure sampling_cost.pdf
```

El código que asigna datos, curvas exactas, barras y estilos a cada figura
está en [`paper/generar_figuras.py`](../paper/generar_figuras.py). La función
`main()` vincula cada nombre a una función. Los pies originales y sus
referencias cruzadas están en [`paper/paper.tex`](../paper/paper.tex).

## PNG históricos de los informes de fase

Son figuras de diagnóstico y presentación anteriores al formato editorial
del artículo; se conservan para rastrear el desarrollo. No son los PDF
vectoriales del manuscrito.

### Fase 2

```bash
python phase2/replot_saved.py --run 7a2a04b53b62f674
```

Lee `phase2/data/<ID>/sweep.npz` y escribe tres archivos en
`phase2/plots/<ID>/`:

| Archivo | Función en `phase2/src/figures_phase2.py` | Contenido |
|---|---|---|
| `fig1_Z2_mc_vs_exact.png` | `figure_Z2()` | Función de partición de dos bosones y residuos. |
| `fig2_exchange_term_vs_T.png` | `figure_exchange_term()` | Razón de los pesos de intercambio e identidad. |
| `fig3_cycle_fraction_vs_T.png` | `figure_cycle_fraction()` | Frecuencia del sector intercambiado frente a temperatura. |

`phase2/src/plots.py` produce otros cuatro PNG ilustrativos al ejecutar su
entrada propia; incluye una visualización de worldlines. Esa entrada corre
una simulación nueva y **no** forma parte de la reproducción del artículo.

### Fase 3

```bash
python phase3/replot_saved.py --run e81ec15bbc1df520
```

Lee `phase3/data/<ID>/summary.json` y escribe, para cada `N=3,4`, cinco
archivos en `phase3/plots/<ID>/`: `N<N>_clases.png`,
`N<N>_particulas_en_ciclos.png`, `N<N>_histograma.png`,
`N<N>_energia.png` y `N<N>_particion.png`.
La función `phase3/src/plot_phase3.py:make_plots()` produce todos ellos.
Se puede repetir con `--run f58f237895157d1b` para el barrido de cierre.

`python phase3/study_closure.py` genera además
`phase3/plots/estudio_cierre/N3_P_y_coste.png` y
`N4_P_y_coste.png`, **pero primero recorre las 26 configuraciones** del
estudio. Para recuperar los resultados del artículo con rapidez, use los
PDF generados desde `study_closure.json` en lugar de repetir ese estudio.

## Lectura estadística

Las líneas exactas proceden de fórmulas canónicas o del producto de
ocupaciones. Las barras representan una desviación estándar estimada.
Varios paneles comparten los mismos datos: su acuerdo no cuenta como
controles estadísticos independientes. La aceptación de propuestas de
transposición no es una probabilidad de clase. Para ciclos raros a alta
temperatura, el generador editorial omite puntos que no superan el criterio
de resolución, aunque sigue mostrando la curva exacta.
