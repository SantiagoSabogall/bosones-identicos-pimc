# Manifiesto de cierre de la Fase 3

Las rutas de esta tabla son relativas a `phase3/`.
El estado comprueba que exista `summary.json`, que el número de
series crudas coincida con la configuración y que los controles
internos de cadena indiquen `valid=True`. El acuerdo exacto se
reporta por separado en `RESULTADOS_CIERRE.md`.

| Grupo | N | β | P | modo | ID | estado |
|---|---:|---:|---:|---|---|---|
| térmico | 3,4 | 0.1,1,10 | 4 | global | `f58f237895157d1b` | completa (18 series) |
| seguimiento | 3 | 1 | 4 | global | `7837d0146dbd1097` | completa (3 series) |
| estudio P/coste | 3 | 0.5 | 2 | global | `5b78fd5ee8eddb89` | completa (3 series) |
| estudio P/coste | 3 | 0.5 | 4 | global | `4de78b644c1ace1e` | completa (3 series) |
| estudio P/coste | 3 | 0.5 | 8 | global | `e16b17e6838902f9` | completa (3 series) |
| estudio P/coste | 3 | 0.5 | 16 | global | `27fa10f5ac9a1e87` | completa (3 series) |
| estudio P/coste | 3 | 1 | 2 | global | `f9afbf9d29417213` | completa (3 series) |
| estudio P/coste | 3 | 1 | 4 | global | `cee8081ccdb7d1ab` | completa (3 series) |
| estudio P/coste | 3 | 1 | 8 | global | `0768268ca6a4da1a` | completa (3 series) |
| estudio P/coste | 3 | 1 | 16 | global | `94c5b46ae09e02e0` | completa (3 series) |
| estudio P/coste | 3 | 5 | 2 | global | `692a86145e431890` | completa (3 series) |
| estudio P/coste | 3 | 5 | 4 | global | `097bf490254da2fa` | completa (3 series) |
| estudio P/coste | 3 | 5 | 8 | global | `a893599bf56a913a` | completa (3 series) |
| estudio P/coste | 3 | 5 | 16 | global | `054a73c87a421839` | completa (3 series) |
| estudio P/coste | 4 | 0.5 | 2 | global | `fd612b52e8237bf5` | completa (3 series) |
| estudio P/coste | 4 | 0.5 | 4 | global | `060c0ad9037e2418` | completa (3 series) |
| estudio P/coste | 4 | 0.5 | 8 | global | `854d0062fb644b4f` | completa (3 series) |
| estudio P/coste | 4 | 0.5 | 16 | global | `f82cfedf264a8727` | completa (3 series) |
| estudio P/coste | 4 | 1 | 2 | global | `301d8cdb7eb5bd41` | completa (3 series) |
| estudio P/coste | 4 | 1 | 4 | global | `f75b86e692ac7b83` | completa (3 series) |
| estudio P/coste | 4 | 1 | 8 | global | `45332e81ac7b22cd` | completa (3 series) |
| estudio P/coste | 4 | 1 | 16 | global | `8a4791ebe67f33dc` | completa (3 series) |
| estudio P/coste | 4 | 5 | 2 | global | `83779acf197babc0` | completa (3 series) |
| estudio P/coste | 4 | 5 | 4 | global | `09e20b86dc9101d7` | completa (3 series) |
| estudio P/coste | 4 | 5 | 8 | global | `02b1585e7f64b6db` | completa (3 series) |
| estudio P/coste | 4 | 5 | 16 | global | `8b5a82f4eb57ca1a` | completa (3 series) |
| estudio P/coste | 3 | 1 | 4 | local | `883becbc49516b81` | completa (3 series) |
| estudio P/coste | 4 | 1 | 4 | local | `9d4b6b38cb17fd44` | completa (3 series) |

## Entregables

- `src/`, `tests/`, `requirements-lock.txt`, `Makefile`: código y pruebas.
- `data/<ID>/`: resúmenes y series crudas con parámetros y semillas.
- `study_closure.json`: índice y valores del estudio de P y coste.
- `RESULTADOS_CIERRE.md`, `AUDITORIA_CADENAS.md`: auditorías numéricas.
- `plots/`: gráficas del barrido y del estudio de P y coste.
- `../paper/`: fuente, figuras vectoriales y PDF del artículo.

## Regeneración

Desde `phase3/`, ejecutar `make all`. Los resúmenes
completos con igual huella de parámetros y código se reutilizan;
una carpeta sin `summary.json` se vuelve a calcular.
