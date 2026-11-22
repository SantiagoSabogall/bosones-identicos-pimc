# Validación ejecutada

Código original conservado sin cambios. Nueva versión en esta carpeta.

Pruebas: 34 de la suite completa y una adicional de energía/intercambio con ω=2.3 pasaron. Se repitieron dos pruebas del pipeline tras ajustar sus metadatos y figuras.

Barrido: P=4, 8000 muestras + 500 barridos de termalización por semilla, tres semillas por temperatura, ω=1. Los diez puntos pasaron los criterios operativos documentados. Todos los residuos de intercambio son menores que 1.5 errores estimados; los de energía termodinámica y virial son menores que 3.

Reproducción:

```bash
python src/validate_phase2.py --steps 8000 --burn 500 --beads 4
```

| β | Intercambio MC | Exacto | Validado |
|---|---|---|---|
| 0.1000 | 0.04642 ± 0.00199 | 0.04758 | True |
| 0.1668 | 0.07479 ± 0.00382 | 0.07682 | True |
| 0.2783 | 0.12342 ± 0.00307 | 0.12145 | True |
| 0.4642 | 0.18329 ± 0.00387 | 0.18567 | True |
| 0.7743 | 0.27913 ± 0.00657 | 0.26948 | True |
| 1.2915 | 0.36621 ± 0.00310 | 0.36258 | True |
| 2.1544 | 0.44196 ± 0.00284 | 0.44202 | True |
| 3.5938 | 0.48537 ± 0.00205 | 0.48625 | True |
| 5.9948 | 0.49933 ± 0.00160 | 0.49875 | True |
| 10.0000 | 0.50008 ± 0.00094 | 0.49998 | True |

Muestras y diagnósticos en `data/7a2a04b53b62f674`. Las figuras correspondientes están en `plots/7a2a04b53b62f674`.

La carpeta de esta corrida tiene la huella calculada al iniciarla. Ajustes posteriores de documentación y presentación cambian la huella para futuras corridas; el programa recalculará resultados en una carpeta distinta. Los cambios posteriores no modificaron el algoritmo de muestreo empleado.
