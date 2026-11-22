# Bosones idénticos y ciclos de intercambio: PIMC reproducible

Código, datos y figuras de las fases 2 y 3 del Proyecto 12. Se estudian
`N=2,3,4` bosones ideales sin espín en una trampa armónica unidimensional
mediante integrales de camino con cierres permutados. El propagador de Mehler
es exacto para esta trampa. **La fase 4 y un potencial externo diferente aún
no forman parte de estos resultados.**

El repositorio incluye las series Monte Carlo utilizadas, resúmenes JSON,
controles analíticos, pruebas, las doce figuras vectoriales del artículo y
su fuente REVTeX. Los resultados guardados permiten regenerar las figuras
sin esperar a que terminen nuevas simulaciones.

## Contenido

| Ruta | Propósito |
|---|---|
| [`phase2/`](phase2/) | Muestreador `N=2`, control de identidad/intercambio, datos y tres PNG históricos. |
| [`phase3/`](phase3/) | Muestreador `N=3,4`, clases de ciclos, referencia de ocupaciones, diagnósticos, estudio de `P` y coste. |
| [`paper/`](paper/) | Artículo REVTeX, PDF, doce figuras PDF y generador gráfico. |
| [`docs/FIGURAS.md`](docs/FIGURAS.md) | Tabla de las doce figuras del artículo, datos y comando individual; también explica los PNG históricos. |
| [`docs/CODIGO.md`](docs/CODIGO.md) | Función de cada módulo y relación entre simulación, resumen y gráfica. |
| [`docs/REPRODUCIBILIDAD.md`](docs/REPRODUCIBILIDAD.md) | Corridas, semillas, pruebas, parámetros, costes y verificaciones. |

## Requisitos

- Python **3.14.0** es el entorno verificado. Las dependencias directas
  comprobadas están fijadas en [`requirements.txt`](requirements.txt):
  NumPy, SciPy, Matplotlib, Seaborn y pytest. En otra versión de Python,
  compruebe la disponibilidad de esas versiones antes de instalar.
- Para compilar el artículo: `latexmk`, `pdflatex` y `bibtex`. El árbol
  `paper/vendor/revtex/` incluye REVTeX 4.2f para el entorno donde se produjo
  el PDF. Los PDF vectoriales pueden generarse sin instalar LaTeX.
- Un sistema Unix con terminal `bash` para ejecutar `paper/build.sh`.

## Inicio rápido desde la raíz del repositorio

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
bash scripts/test_all.sh
python paper/generar_figuras.py
```

La última orden **solo lee datos guardados** y escribe doce archivos PDF en
`paper/figuras/`. Para generar una sola figura:

```bash
python paper/generar_figuras.py --list
python paper/generar_figuras.py --figure exchange_cycles.pdf
```

Se pueden repetir `--figure` para elegir varias. El nombre debe incluir
`.pdf`; la tabla completa está en [`docs/FIGURAS.md`](docs/FIGURAS.md).
Para comprobar que los archivos de datos publicados no cambiaron:

```bash
sha256sum -c data_checksums.sha256
```

Para compilar el manuscrito, después de generar las figuras:

```bash
bash paper/build.sh
```

El resultado es `paper/paper.pdf`. El texto principal ocupa cuatro páginas
incluida la bibliografía; siguen cuatro páginas de anexos. En el artículo
se describe la disponibilidad de código y datos en un párrafo breve antes
de la bibliografía. El repositorio contiene las instrucciones extensas.

## Regenerar las figuras históricas sin simular

```bash
python phase2/replot_saved.py
python phase3/replot_saved.py --run e81ec15bbc1df520
```

Estas órdenes producen PNG en `phase2/plots/<ID>/` y
`phase3/plots/<ID>/`. Los PNG conservan el formato de los informes de fase;
las figuras del artículo se generan de manera independiente, en PDF y sin
títulos dentro de los ejes.

## Ejecutar una simulación nueva

```bash
python phase2/src/validate_phase2.py --steps 8000 --burn 500 --replicas 3 --beads 4
python phase3/src/run_control.py --N 3 --beta 1 --steps 10000
python phase3/src/sweep_phase3.py --N 3 4 --betas 0.1 1 10 --steps 4000 --burn 500 --replicas 3 --P 4
```

Las simulaciones pueden tardar bastante más que la regeneración de figuras.
Cada barrido escribe `data/<ID>/summary.json` y series `.npz`; el ID se
obtiene de los parámetros y del contenido del código. Una corrida con
parámetros distintos crea otra carpeta. **Las figuras publicadas usan los
IDs fijos descritos en [`docs/REPRODUCIBILIDAD.md`](docs/REPRODUCIBILIDAD.md),
no `LATEST.txt`**, que cambia al ejecutar un barrido nuevo.
La corrida histórica de fase 2 procede de una revisión anterior: con el
código actual, sus mismos parámetros producen otra huella y se vuelve a
simular. Sus datos originales sí están completos y permiten regenerar
exactamente las gráficas guardadas.

## Convenciones físicas

Se usan `\hbar=m=k_B=1` y `\omega=1` en las corridas publicadas.
`\beta=1/T`; `P` es el número de rebanadas de tiempo imaginario.
Una clase `1+2`, por ejemplo, contiene un ciclo de longitud 1 y otro de
longitud 2. Las probabilidades son frecuencias de equilibrio; no deben
confundirse con la tasa de aceptación de transposiciones. Las curvas exactas
proceden de las funciones canónicas, no de ajustes a los puntos Monte Carlo.

## Alcance y estado

La comparación con expresiones exactas valida este sistema finito. La
aparición de ciclos largos en `N<=4` no establece una transición de
condensación. Las cifras de coste dependen del equipo y de la implementación.
La extensión a otro potencial externo requerirá una nueva referencia
espectral y un estudio de discretización.

Autores del artículo: Camilo Guzmán, Santiago Sabogal y Milena Barrios.
