# Mapa del código y flujo de datos

## Del modelo físico a una figura

```text
parámetros + semilla
       │
       ▼
sampler.py ──► observables.py ──► data/<ID>/*.npz (series)
       │                │
       ▼                ▼
sector/clase       data/<ID>/summary.json
                         │
                         ▼
              paper/generar_figuras.py
                         │
                         ▼
               paper/figuras/*.pdf
                         │
                         ▼
                  paper/paper.pdf
```

El archivo `.npz` contiene muestras y metadatos por réplica. El JSON
contiene medias, errores, diagnósticos y controles exactos. El generador
del artículo lee JSON y el resumen del estudio de `P`; no reejecuta el
muestreador. La figura esquemática de worldlines es determinista.

## Fase 2: dos bosones

| Archivo | Función |
|---|---|
| `phase2/src/params.py` | Valida los parámetros físicos y de Monte Carlo. |
| `phase2/src/propagador.py` | Núcleo exacto de Mehler para un enlace imaginario. |
| `phase2/src/sectors.py` | Identidad, transposición y cierre de trayectorias. |
| `phase2/src/sampler.py` | Actualizaciones de beads, ciclos y sector de permutación. |
| `phase2/src/analytic.py` | `z(β)`, `Z_2`, fracción exacta y energía de control. |
| `phase2/src/observables.py` | Energía, fracción intercambiada, bloques y diagnósticos. |
| `phase2/src/validate_phase2.py` | Barrido de 10 temperaturas con réplicas, huella y resultados guardados; entrada recomendada. |
| `phase2/src/figures_phase2.py` | Tres PNG históricos de control a partir del barrido. |
| `phase2/replot_saved.py` | Reproduce esos PNG desde `sweep.npz` sin PIMC. |
| `phase2/src/run_phase2.py`, `mc_sweep.py`, `plots.py` | Controles e ilustraciones anteriores; no alimentan los PDF del artículo. |
| `phase2/tests/` | Pruebas de propagador, exactitud, integración y pipeline. |

El estado del muestreador es `(x,σ)` con `x.shape=(2,P)` y
`x[i,P]=x[σ(i),0]`. La actualización de permutación cambia los enlaces de
cierre y usa Metropolis con propuesta simétrica. El factor `1/2!` se
incluye al reconstruir `Z_2`, y se cancela en la razón de aceptación.

## Fase 3: tres y cuatro bosones

| Archivo | Función |
|---|---|
| `phase3/src/params.py`, `propagador.py` | Parámetros y núcleo armónico. |
| `phase3/src/cycles.py` | Descompone permutaciones y enumera clases y multiplicidades. |
| `phase3/src/exact.py` | Pesos de ciclos, funciones canónicas y energías exactas. |
| `phase3/src/occupations.py` | Referencia independiente por ocupaciones bosónicas; audita `1/N!`. |
| `phase3/src/sampler.py` | PIMC generalizado para `N=2,3,4`, incluido heat-bath gaussiano de ciclo completo. |
| `phase3/src/observables.py` | Indicadores de clase, fracciones de partículas, energía y combinación de réplicas. |
| `phase3/src/diagnostics.py` | Autocorrelación integrada y tamaño efectivo de muestra. |
| `phase3/src/run_control.py` | Control rápido de una configuración. |
| `phase3/src/sweep_phase3.py` | Barrido con réplicas, series crudas, resumen JSON y huella de corrida. |
| `phase3/src/plot_phase3.py` | PNG históricos de clases, histogramas, energía y partición. |
| `phase3/replot_saved.py` | Reproduce los PNG históricos desde un resumen existente. |
| `phase3/study_closure.py` | 24 configuraciones de `P` más 2 locales para el estudio de coste; también genera PNG diagnósticos. |
| `phase3/audit_series.py`, `report_closure.py`, `manifest_closure.py` | Auditoría de series, informe numérico y manifiesto de corridas. |
| `phase3/tests/` | Pruebas de exactitud, clases, muestreador, observables y barrido. |

El muestreador usa un arreglo `(N,P)` y una permutación de `N` índices.
El lector de PNG históricos completa en memoria algunos campos derivados
ausentes en el JSON antiguo; nunca reescribe ese archivo.
Una transposición de dos imágenes conecta sectores. Para el potencial
armónico, la densidad conjunta de un ciclo es gaussiana; el heat-bath
global extrae el ciclo completo sin aproximación de Trotter. La cantidad
`q_ℓ=ℓ⟨n_ℓ⟩/N` pondera partículas y difiere de la probabilidad `p_λ`
de una clase entera.

## Artículo

| Archivo | Función |
|---|---|
| `paper/generar_figuras.py` | Lee resúmenes fijos, dibuja curvas exactas y puntos MC, guarda 12 PDF vectoriales; `--figure` permite elegir una. |
| `paper/figuras/*.pdf` | Cinco figuras principales y siete figuras de anexos. |
| `paper/paper.tex` | Manuscrito REVTeX en inglés; figuras citadas y pies detallados. |
| `paper/references.bib` | Bibliografía física y registro versionado del código. |
| `paper/build.sh` | Regenera las figuras y compila el PDF con `latexmk`. |
| `paper/vendor/revtex/` | Copia de REVTeX 4.2f para compilar en el entorno original. |

El estudio de `P` tiene una interpretación especial: con el núcleo de
Mehler, variar `P` comprueba muestreo y eficiencia, **no** extrapola un
error de Trotter. En un futuro potencial no armónico habría que separar
error de discretización y error Monte Carlo.
