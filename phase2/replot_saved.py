"""Recreate the three historical Phase 2 PNGs from a saved sweep.npz.

No Monte Carlo simulation is run. Run from any directory:
    python phase2/replot_saved.py
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "src"))
from figures_phase2 import make_all  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", default="7a2a04b53b62f674")
    args = parser.parse_args()
    source = HERE / "data" / args.run / "sweep.npz"
    if not source.is_file():
        parser.error(f"Saved sweep not found: {source}")
    with np.load(source) as data:
        paths = make_all(data, str(HERE / "plots" / args.run))
    print("\n".join(paths))


if __name__ == "__main__":
    main()
