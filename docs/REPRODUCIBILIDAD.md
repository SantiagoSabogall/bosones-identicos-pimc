# Reproducción y procedencia de los resultados

Esta guía distingue tres tareas: **regenerar figuras desde datos**, **verificar
el código** y **ejecutar PIMC de nuevo**. Las dos primeras son las rápidas.
Los comandos se muestran desde la raíz del repositorio.

## Entorno

Se verificó en Fedora con Python 3.14.0, NumPy 2.3.5, SciPy 1.16.2,
Matplotlib 3.10.6, Seaborn 0.13.2 y pytest 9.2.0.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
bash scripts/test_all.sh
```

Para los PDF del artículo, instalar además `latexmk`, `pdflatex` y
`bibtex`. El script `paper/build.sh` incorpora la copia local de REVTeX.
Si solo se necesitan figuras PDF, LaTeX no es necesario.

## Datos fijados para el manuscrito

| Conjunto | Ruta | Condiciones y uso |
|---|---|---|
| Fase 2 | `phase2/data/7a2a04b53b62f674/` | `N=2`; 10 valores de `β` entre 0.1 y 10; `P=4`; 3 cadenas, 8000 mediciones y 500 descartes cada una. |
| Fase 3 histórica | `phase3/data/e81ec15bbc1df520/` | `N=3,4`; 7 temperaturas entre 0.5 y 5; `P=4`; 3 cadenas, 4000 mediciones y 500 descartes. Incluye la instantánea `β≈1.077`. |
| Fase 3 de cierre | `phase3/data/f58f237895157d1b/` | `N=3,4`; `β=0.1,1,10`; 3 cadenas, 4000 mediciones y 500 descartes. |
| Seguimiento largo | `phase3/data/7837d0146dbd1097/` | `N=3`, `β=1`, `P=4`; 3 cadenas, 12000 mediciones y 2000 descartes. Sustituye el punto corto de ese parámetro en las figuras editoriales. |
| Estudio de `P` y coste | `phase3/study_closure.json` y los directorios `phase3/data/<run_id>/` que enumera | 24 configuraciones con heat-bath global y 2 locales; `P=2,4,8,16`, `β=0.5,1,5`, `N=3,4`; semilla base 20261121. |

Cada `summary.json` registra configuración, resultados, barras y
diagnósticos. Los `.npz` de la misma carpeta contienen las series de las
réplicas y sus parámetros. `study_closure.json` registra el ID de cada
configuración individual. Estos archivos permiten auditar la procedencia
de los puntos de cada gráfica. Los directorios con ID son parte de los
datos y deben mantenerse junto con el código.

`data_checksums.sha256` fija las sumas SHA-256 de los 209 archivos de
datos y del estudio. Desde la raíz, ejecute
`sha256sum -c data_checksums.sha256` para verificar su integridad.

## Reproducción rápida

```bash
python paper/generar_figuras.py
bash paper/build.sh
```

La primera orden genera los doce PDF a partir de resúmenes existentes.
La segunda hace lo mismo y compila `paper/paper.pdf`. Para una figura
individual, use `--figure NOMBRE.pdf`; consulte
[`FIGURAS.md`](FIGURAS.md). El script no lee `LATEST.txt`, por lo que una
corrida nueva no cambia silenciosamente las figuras del artículo.

Los PNG de informes de fase se regeneran también sin PIMC:

```bash
python phase2/replot_saved.py
python phase3/replot_saved.py --run e81ec15bbc1df520
```

## Repetir una corrida Monte Carlo

```bash
python phase2/src/validate_phase2.py --steps 8000 --burn 500 --replicas 3 --beads 4
python phase3/src/sweep_phase3.py --N 3 4 --betas 0.1 1 10 --steps 4000 --burn 500 --replicas 3 --P 4
```

Ambos barridos utilizan semillas base definidas en los scripts. La huella
de la corrida depende de la configuración y del contenido de `src/*.py`.
Si el resumen correspondiente ya existe, el programa reutiliza la
caché; para una repetición independiente, cambie la semilla o un parámetro
y conserve la nueva carpeta. No borre el resumen publicado para forzar
una ejecución: eso impediría comparar versiones de datos.

**Excepción histórica:** el ID de Fase 2 `7a2a04b53b62f674` se obtuvo con
una revisión anterior de `phase2/src`. El código actualmente empaquetado
calcula otra huella incluso con los mismos parámetros, por lo que el
comando de Fase 2 inicia una nueva simulación. Se conservan íntegros
`summary.json`, `sweep.npz` y las series de sus tres cadenas por temperatura.
La reproducción de las figuras desde esos datos es exacta; una nueva
cadena solo debe esperarse compatible estadísticamente.

El barrido de Fase 3 histórica empleó una versión previa del flujo; su
configuración guardada no contiene todas las claves del código actual.
Se conserva como dato histórico y alimenta las figuras indicadas; un
barrido nuevo con parámetros similares puede obtener otro ID.

El estudio completo de coste se lanza con:

```bash
python phase3/study_closure.py
python phase3/report_closure.py
python phase3/audit_series.py
python phase3/manifest_closure.py
```

**Este estudio es más costoso**: recorre 26 configuraciones. Sus tiempos
pueden variar con el equipo, carga del sistema y versión de Python. Las
cifras de muestras efectivas por segundo son descriptivas, no constantes
universales del método.

## Qué se ha verificado

- Las pruebas unitarias comprueban el propagador, enumeración de clases,
  normalización, controles exactos y funcionamiento de los muestreadores.
- La fórmula canónica por ciclos se compara con la base de ocupaciones;
  este contraste sí audita el factor global `1/N!` de forma independiente.
- La reconstrucción de `Z_N` desde la fracción del sector identidad usa
  ese mismo sector muestreado y es una verificación correlacionada con el
  histograma de clases.
- Las barras de error y el criterio de resolución de clases raras se
  describen en `phase2/README.md`, `phase3/README.md` y en los pies del
  artículo. Un punto omitido de una figura no se elimina del JSON.
- El PDF y los datos guardados describen solo el oscilador armónico ideal.
  No se han incluido resultados del potencial externo propuesto para
  Fase 4.

Para citas públicas, use una versión fija del repositorio. Al actualizar
el artículo o los datos, cree otra versión en lugar de cambiar el
significado de una etiqueta de publicación existente.
