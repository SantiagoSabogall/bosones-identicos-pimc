# Fase 2 corregida: dos bosones en trampa armónica 1D

Unidades: ħ=m=kB=1. Se admite cualquier ω>0, N=2 y P≥2.

## Ejecutar

```bash
python -m pip install -r requirements.txt
python -m pytest -q -p no:cacheprovider
python src/validate_phase2.py
```

El último comando es el punto de entrada recomendado. Genera un barrido de diez
β entre 0.1 y 10, tres semillas por temperatura, muestras crudas, diagnósticos y
figuras. `LATEST.txt` identifica la carpeta de datos. Opciones: `--omega 2`,
`--steps 24000`, `--burn 2000`, `--beads 8`, `--replicas 4`.
La caché depende de parámetros y del contenido de todos los archivos fuente.

## Algoritmo

Cada barrido aplica heat-bath local, desplazamientos colectivos de ciclos con
Metropolis, remuestreo gaussiano exacto de cada ciclo completo y un intento de
permutación mediante la razón de enlaces de cierre. El remuestreo global es
específico del oscilador ideal: se construye la matriz de precisión del producto
de propagadores de Mehler y se extrae una gaussiana multivariada. No se usa la
probabilidad exacta de intercambio para elegir sectores. Los factores de
covarianza se calculan una vez por longitud de ciclo.

El propagador es exacto: P cambia eficiencia y resolución visual, sin error de
Trotter. La aceptación uno del heat-bath local no implica mezcla rápida.
El parámetro delta controla ahora los desplazamientos colectivos.

## Validación estadística

Los contadores de termalización y medición están separados. Se guardan las series
de intercambio, energía, energía virial y ciclos. Se comparan errores con bloques
de 16, 64, 256 y 1024 muestras, cuando hay al menos ocho bloques. Se exigen 100
cambios de sector por réplica, ambas ocupaciones y estabilidad de los dos últimos
errores positivos dentro de un factor dos. Se comprueba acuerdo entre semillas
con un umbral operativo de cuatro errores combinados. Estos criterios son
heurísticos explícitos, no una demostración de independencia. Si fallan, aumentar
muestreo y examinar las series: el punto se conserva en JSON pero se omite de las
figuras. El error combinado usa el máximo entre dispersión entre semillas y
propagación de los errores internos conservadores.

Se reportan energía termodinámica y virial armónica, ambas válidas a P finito en
equilibrio con enlaces exactos. Las tres gráficas de sectores transforman la misma
fracción y no son tres controles estadísticos independientes.

Con a=βω: z=1/[2 sinh(a/2)], f=(1-exp(-a))/2, R=tanh(a/2).
Z₂ se reconstruye como z²/[2(1-f)]: la normalización absoluta viene del sector
identidad analítico. El factor 1/2! se incluye al reconstruir Z₂; se cancela en
las aceptaciones. El muestreo de frecuencias por sí solo no audita ese factor.

Los scripts heredados `run_phase2.py` y `mc_sweep.py` sirven como controles simples;
para réplicas, diagnósticos y caché utilice `validate_phase2.py`.
