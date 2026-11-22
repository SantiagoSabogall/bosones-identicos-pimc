# Fase 3: muestreador, auditoría y estudios de cierre

Esta carpeta contiene el **control exacto** y el **muestreador generalizado** para N=2, 3 y 4 bosones ideales en un oscilador armónico unidimensional. Usa unidades ħ=m=kB=1. La versión de fase 2 está en otra carpeta y no se necesita para ejecutar esta base.

## Ejecutar

Se requiere Python con NumPy, Matplotlib y pytest para las pruebas y figuras.
Las versiones directas verificadas constan en `requirements-lock.txt`;
`REPRODUCIBILIDAD.md` registra el entorno y las corridas.

```bash
python -m pytest -q -p no:cacheprovider tests
python src/run_control.py --N 3 --beta 1 --steps 10000
python src/run_control.py --N 4 --beta 1 --steps 10000
python src/sweep_phase3.py --steps 4000 --burn 500 --replicas 3 --P 4
python src/sweep_phase3.py --N 3 4 --betas 0.1 1 10 --steps 4000 --burn 500 --replicas 3 --P 4
python study_closure.py
python report_closure.py
```

`run_control.py` es una comprobación rápida con una sola semilla. `sweep_phase3.py` genera el barrido con réplicas, series crudas, errores y figuras. La carpeta se registra en `LATEST.txt` y lleva una huella de parámetros y código.

`occupations.py` implementa una referencia canónica independiente: suma de
estados bosónicos ordenados y producto de ocupaciones, sin llamar al recuento
de ciclos. `diagnostics.py` estima autocorrelación integrada y muestras
efectivas. El barrido guarda tiempo de medición, aceptación de transposiciones,
ESS y reconstrucción de $Z_N$ mediante la fracción del sector identidad.
La columna `valid` se basa en movilidad y ESS internos; el acuerdo con la
solución exacta aparece aparte como `exact_within_4sigma`.

## Bloque 1: control exacto

Para una permutación σ con ciclos c, la integral de trayectorias factoriza:

    Z_N = (1/N!) Σ_{σ∈S_N} ∏_{c∈ciclos(σ)} z(|c|β)
    z(β) = 1/[2 sinh(βω/2)].

Una clase queda especificada por n_l ciclos de longitud l. Su multiplicidad es

    N! / ∏_l [l^(n_l) n_l!].

`cycles.py` genera particiones, descompone cualquier permutación y calcula sus multiplicidades. `exact.py` da pesos, probabilidades, Z_N y E_N. También implementa expresiones explícitas para auditar los factores:

    Z_3 = [z1³ + 3 z1 z2 + 2 z3]/6
    Z_4 = [z1⁴ + 6 z1² z2 + 3 z2² + 8 z1 z3 + 6 z4]/24,

con z_l=z(lβ). Las clases son:

| N | Clase | Multiplicidad |
|---|---|---:|
| 3 | (1,1,1), (1,2), (3) | 1, 3, 2 |
| 4 | (1,1,1,1), (1,1,2), (2,2), (1,3), (4) | 1, 6, 3, 8, 6 |

Cada probabilidad exacta es el peso de su clase dividido por la suma de pesos de todas las clases. La energía exacta se calcula como promedio de Σ_c |c| E_1(|c|β) con esas probabilidades.

## Bloque 2: muestreador

El estado es `(x, perm)` con `x.shape=(N,P)`. Cada último bead `x[i,P-1]` se conecta con `x[perm[i],0]`. Un barrido aplica N·P actualizaciones heat-bath de posiciones, desplazamientos colectivos de cada ciclo, extracción gaussiana exacta de cada ciclo completo y un intento de transposición de dos imágenes de `perm`.

La transposición elige un par uniforme y se acepta mediante Metropolis con la diferencia logarítmica de los enlaces de cierre. Es simétrica, reversible y los pares generan todo S_N. Las actualizaciones gaussianas preservan la distribución condicional de las posiciones en el sector actual; **no** eligen los sectores usando las probabilidades analíticas. El factor 1/N! es común a todas las permutaciones y se cancela en la aceptación. El propagador de Mehler es exacto para este oscilador; P no introduce error de Trotter.

## Bloque 3: estadística de ciclos y barrido térmico

`observables.py` registra por barrido:

- Tipo completo de ciclos, por ejemplo `(1,1,2)` frente a `(2,2)` para N=4.
- `n_cycles[:, l-1]`: número de ciclos de longitud l.
- `particle_fractions[:, l-1] = l*n_l/N`: fracción de partículas de esa muestra que pertenece a ciclos de longitud l. En toda muestra, Σ_l l*n_l=N y Σ_l particle_fractions_l=1.
- Energías termodinámica y virial como controles adicionales.

El barrido usa tres semillas independientes por cada N y β. Calcula errores conservadores como el mayor de la dispersión entre semillas y la propagación de errores de bloques internos (16, 64, 256 y, si alcanzan las muestras, 1024 barridos por bloque). Guarda los arrays crudos de cada réplica en `.npz` y un `summary.json` con medias, barras, referencias exactas y diagnóstico. El criterio operativo exige al menos 30 cambios de clase por réplica, visita de todas las clases, barras positivas y desviaciones respecto al control exacto menores que cuatro errores; los puntos que fallan se marcan `valid=false` y se representan con `x` en las figuras. Es un diagnóstico práctico, no una prueba rigurosa de ausencia de autocorrelación.

Las figuras muestran probabilidad de cada tipo de ciclo frente a T, pertenencia de una partícula a ciclos de cada longitud y un histograma de clases cerca de β=1 para N=3 y N=4. Cada curva exacta se obtiene de `exact.py`, no de ajustar los puntos Monte Carlo.

## Estudio de cierre

El barrido histórico `e81ec15bbc1df520` se conserva sin modificar. El nuevo
barrido térmico y el estudio de $P=2,4,8,16$ quedan en directorios de datos
con huellas propias. `study_closure.py` hace comparaciones en tres
temperaturas para $N=3,4$, cronometra el muestreo y evalúa una variante sin
heat-bath global. `report_closure.py` genera tablas directamente de los
resúmenes JSON. Los ciclos de alta temperatura que no alcanzan 20
apariciones por réplica se identifican como exploratorios.
