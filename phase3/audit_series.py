"""Auditoría posterior de las series crudas, independiente del resumen PIMC."""
from pathlib import Path
import json
import numpy as np
from src.diagnostics import integrated_time


ROOT = Path(__file__).resolve().parent
RUNS = ("f58f237895157d1b", "7837d0146dbd1097")


def half_discrepancy(values):
    first, second = np.array_split(np.asarray(values, dtype=float), 2)
    a, b = integrated_time(first), integrated_time(second)
    error = np.hypot(a["error"], b["error"])
    if not a["resolved"] or not b["resolved"] or error == 0:
        return None
    return abs(first.mean() - second.mean()) / error


def chain_metrics(raw):
    ids = raw["class_ids"]
    n_classes = raw["class_flags"].shape[1]
    transitions = np.zeros((n_classes, n_classes), dtype=int)
    np.add.at(transitions, (ids[:-1], ids[1:]), 1)
    boundaries = np.r_[0, np.flatnonzero(np.diff(ids)) + 1, len(ids)]
    dwell_lengths = np.diff(boundaries)
    dwell_classes = ids[boundaries[:-1]]
    half_values = [half_discrepancy(raw["class_flags"][:, j])
                   for j in range(n_classes)]
    half_values.append(half_discrepancy(raw["energy"]))
    energy_tau = integrated_time(raw["energy"])["tau"]
    return {
        "outgoing": (transitions.sum(axis=1) - np.diag(transitions)).tolist(),
        "longest_dwell": int(dwell_lengths.max()),
        "mean_dwell_by_class": [
            float(dwell_lengths[dwell_classes == j].mean())
            if np.any(dwell_classes == j) else None
            for j in range(n_classes)
        ],
        "max_half_sigma": max((x for x in half_values if x is not None),
                              default=None),
        "energy_tau": float(energy_tau),
        "thermo_virial_corr": float(np.corrcoef(raw["energy"], raw["virial"])[0, 1]),
    }


def audit_run(run_id):
    folder = ROOT / "data" / run_id
    summary = json.loads((folder / "summary.json").read_text())
    rows = []
    for n_index, N in enumerate(summary["config"]["N_values"]):
        for b_index, beta in enumerate(summary["config"]["betas"]):
            replicas = []
            for r in range(summary["config"]["replicas"]):
                with np.load(folder / f"N{N}_beta{b_index}_replica{r}.npz") as raw:
                    replicas.append(chain_metrics(raw))
            finite_half = [r["max_half_sigma"] for r in replicas
                           if r["max_half_sigma"] is not None]
            rows.append({
                "N": N, "beta": beta,
                "min_outgoing_by_class": np.min(
                    np.array([r["outgoing"] for r in replicas]), axis=0).tolist(),
                "max_dwell": max(r["longest_dwell"] for r in replicas),
                "max_half_sigma": max(finite_half) if finite_half else None,
                "energy_tau_mean": float(np.mean([r["energy_tau"] for r in replicas])),
                "energy_tau_sd": float(np.std([r["energy_tau"] for r in replicas], ddof=1)),
                "thermo_virial_corr_mean": float(np.mean(
                    [r["thermo_virial_corr"] for r in replicas])),
            })
    return rows


def main():
    lines = ["# Auditoría adicional de las cadenas de la Fase 3", "",
             "Se calcularon las transiciones a partir de `class_ids` guardados en cada",
             "archivo `.npz`. Una transición es un cambio efectivo de clase entre dos",
             "mediciones sucesivas. Las permanencias cuentan barridos consecutivos",
             "en la misma clase. La discrepancia entre mitades usa errores de",
             "autocorrelación de cada mitad; es un diagnóstico, no una prueba formal",
             "de estacionariedad. Los ciclos muy raros pueden carecer de resolución.", ""]
    for run_id in RUNS:
        lines.extend([f"## Corrida `{run_id}`", "",
                      "| N | β | mínimo de salidas por clase y réplica | permanencia máxima | diferencia máxima entre mitades | τ energía entre réplicas | corr(Etermo,Evirial) |",
                      "|---:|---:|---|---:|---:|---:|---:|"])
        for r in audit_run(run_id):
            half = (f"{r['max_half_sigma']:.2f}σ" if r["max_half_sigma"] is not None
                    else "no resuelta")
            lines.append(
                f"| {r['N']} | {r['beta']:g} | {r['min_outgoing_by_class']} | "
                f"{r['max_dwell']} | {half} | "
                f"{r['energy_tau_mean']:.2f} ± {r['energy_tau_sd']:.2f} | "
                f"{r['thermo_virial_corr_mean']:.3f} |"
            )
        lines.append("")
    lines.extend(["La dispersión de τ entre tres réplicas es descriptiva; no constituye",
                  "un intervalo de confianza preciso. Las energías termodinámica y",
                  "virial se miden en las mismas configuraciones, por lo que su",
                  "correlación impide contarlas como controles estadísticos independientes.", ""])
    destination = ROOT / "AUDITORIA_CADENAS.md"
    destination.write_text("\n".join(lines))
    print(destination)


if __name__ == "__main__":
    main()
