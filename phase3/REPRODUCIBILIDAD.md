# Registro de reproducibilidad de Fase 3

Entorno de referencia comprobado el 21 de noviembre de 2026: Python 3.14.0,
NumPy 2.3.5, Matplotlib 3.10.6 y pytest 9.2.0 en Fedora GNU/Linux.
Las versiones exactas de las dependencias directas están en
`requirements-lock.txt`. Los resultados previos están en
`data/e81ec15bbc1df520`, que se conserva como referencia histórica.

Para reproducir desde esta carpeta:

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python -m pytest -q -p no:cacheprovider tests
.venv/bin/python src/sweep_phase3.py --N 3 4 --betas 0.1 1 10 --P 4 --steps 4000 --burn 500 --replicas 3
```

Cada directorio `data/<id>` corresponde a una huella SHA-256 truncada de
parámetros y archivos de `src`. El `summary.json` se publica por sustitución
atómica después de terminar todas las réplicas. Una carpeta sin ese archivo
representa una corrida interrumpida y no debe interpretarse como resultado.
`LATEST.txt` apunta a la última corrida completada. Los `.npz` registran
series completas, parámetros y clases.

La auditoría de normalización independiente está implementada en
`src/occupations.py`; sus pruebas usan una malla de temperaturas y frecuencias
que no reutiliza el algoritmo de ciclos.

Corridas de cierre: `f58f237895157d1b` (temperatura) y
`7837d0146dbd1097` (repetición larga de $N=3,\beta=1$).
`study_closure.json` relaciona las 26 configuraciones del estudio de $P$ y
la comparación de actualizaciones. En este repositorio, `make all` ejecuta
pruebas, regenera las auditorías y compila el artículo. `make thermal` y
`make study` recalculan o reutilizan las corridas según su huella.
En este repositorio, `phase2/`, `phase3/` y `paper/` son directorios
hermanos. `make article` compila el artículo. La presentación se conserva
fuera de este repositorio de reproducibilidad.
`AUDITORIA_CADENAS.md`, regenerado con `python audit_series.py`, contiene
transiciones, permanencias, autocorrelaciones y comparación entre mitades.
`MANIFIESTO_CIERRE.md` identifica cada corrida y verifica que conserven
resúmenes y series crudas completos.
