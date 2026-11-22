"""Inventario reproducible de corridas y entregables del cierre."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STUDY = ROOT / "study_closure.json"


def status(run_id):
    folder = ROOT / "data" / run_id
    summary = folder / "summary.json"
    if not summary.exists():
        return "incompleta"
    saved = json.loads(summary.read_text())
    expected = (len(saved["config"]["N_values"]) *
                len(saved["config"]["betas"]) * saved["config"]["replicas"])
    observed = len(list(folder.glob("*.npz")))
    if observed != expected or not all(r["valid"] for r in saved["results"]):
        return f"revisar ({observed}/{expected} series)"
    return f"completa ({observed} series)"


def main():
    study = json.loads(STUDY.read_text())
    lines = ["# Manifiesto de cierre de la Fase 3", "",
             "Las rutas de esta tabla son relativas a `phase3/`.",
             "El estado comprueba que exista `summary.json`, que el número de",
             "series crudas coincida con la configuración y que los controles",
             "internos de cadena indiquen `valid=True`. El acuerdo exacto se",
             "reporta por separado en `RESULTADOS_CIERRE.md`.", "",
             "| Grupo | N | β | P | modo | ID | estado |",
             "|---|---:|---:|---:|---|---|---|"]
    for group, run_id, N, beta, P, mode in [
        ("térmico", "f58f237895157d1b", "3,4", "0.1,1,10", 4, "global"),
        ("seguimiento", "7837d0146dbd1097", 3, 1, 4, "global"),
    ]:
        lines.append(f"| {group} | {N} | {beta} | {P} | {mode} | "
                     f"`{run_id}` | {status(run_id)} |")
    for row in study:
        run_id = row["run_id"]
        lines.append(f"| estudio P/coste | {row['N']} | {row['beta']:g} | "
                     f"{row['P']} | {row['mode']} | `{run_id}` | {status(run_id)} |")
    lines.extend(["", "## Entregables", "",
                  "- `src/`, `tests/`, `requirements-lock.txt`, `Makefile`: código y pruebas.",
                  "- `data/<ID>/`: resúmenes y series crudas con parámetros y semillas.",
                  "- `study_closure.json`: índice y valores del estudio de P y coste.",
                  "- `RESULTADOS_CIERRE.md`, `AUDITORIA_CADENAS.md`: auditorías numéricas.",
                  "- `plots/`: gráficas del barrido y del estudio de P y coste.",
                  "- `../paper/`: fuente, figuras vectoriales y PDF del artículo.",
                  "", "## Regeneración", "",
                  "Desde `phase3/`, ejecutar `make all`. Los resúmenes",
                  "completos con igual huella de parámetros y código se reutilizan;",
                  "una carpeta sin `summary.json` se vuelve a calcular.", ""])
    destination = ROOT / "MANIFIESTO_CIERRE.md"
    destination.write_text("\n".join(lines))
    print(destination)


if __name__ == "__main__":
    main()
