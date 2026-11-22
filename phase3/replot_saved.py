"""Recreate the historical Phase 3 PNGs from a saved summary.json.

No Monte Carlo simulation is run. Run from any directory:
    python phase3/replot_saved.py --run e81ec15bbc1df520
"""
from __future__ import annotations

import argparse
import json
import sys
from math import factorial
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "src"))
from plot_phase3 import make_plots  # noqa: E402
from exact import z1  # noqa: E402
from occupations import partition, energy  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", default="e81ec15bbc1df520")
    args = parser.parse_args()
    source = HERE / "data" / args.run / "summary.json"
    if not source.is_file():
        parser.error(f"Saved summary not found: {source}")
    data = json.loads(source.read_text())
    # The 2026-11-09 historical JSON predates these derived fields.
    # Add them in memory only; never rewrite the published measurements.
    omega = float(data["config"].get("omega", 1.0))
    for row in data["results"]:
        n, beta = int(row["N"]), float(row["beta"])
        row.setdefault("class_resolved", [bool(row["valid"])] * len(row["classes"]))
        row.setdefault("energy_occupation", energy(n, beta, omega))
        row.setdefault("z_exact", partition(n, beta, omega))
        p_id = row["class_mc"][0]
        row.setdefault("z_mc", z1(beta, omega) ** n / (factorial(n) * p_id))
        row.setdefault("z_error", row["z_mc"] * row["class_error"][0] / p_id)
    print("\n".join(make_plots(data, HERE / "plots" / args.run)))


if __name__ == "__main__":
    main()
