"""Vector figures for the APS-style paper, regenerated from saved summaries.

The script only plots completed Phase 2/3 runs; it does not simulate or alter
the underlying measurements. All axes are title-free and captions live in TeX.
"""
from __future__ import annotations

import argparse
import json
from math import factorial
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
PHASE2 = PROJECT / "phase2/data/7a2a04b53b62f674/summary.json"
PHASE3_OLD = PROJECT / "phase3/data/e81ec15bbc1df520/summary.json"
PHASE3_NEW = PROJECT / "phase3/data/f58f237895157d1b/summary.json"
FOLLOWUP = PROJECT / "phase3/data/7837d0146dbd1097/summary.json"
STUDY = PROJECT / "phase3/study_closure.json"
OUT = HERE / "figuras"


def read(path: Path):
    return json.loads(path.read_text())


def z(beta, length=1):
    return 1.0 / (2.0 * np.sinh(length * beta / 2.0))


def full_cycle_exact(beta, n):
    a = z(beta)
    b = z(beta, 2)
    if n == 2:
        return b / (a * a + b)
    c = z(beta, 3)
    if n == 3:
        return 2 * c / (a**3 + 3 * a * b + 2 * c)
    d = z(beta, 4)
    return 6 * d / (a**4 + 6 * a * a * b + 3 * b * b + 8 * a * c + 6 * d)


def style():
    sns.set_theme(context="paper", style="ticks", palette="colorblind")
    plt.rcParams.update({
        "font.size": 8,
        "axes.labelsize": 8,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "legend.fontsize": 7,
        "lines.linewidth": 1.3,
        "lines.markersize": 3.5,
        "axes.linewidth": 0.7,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "savefig.facecolor": "white",
    })


def save(fig, name):
    OUT.mkdir(exist_ok=True)
    path = OUT / name
    fig.savefig(path, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)
    print(path)


def clean_axis(ax):
    ax.grid(axis="y", color="0.9", linewidth=0.45)
    sns.despine(ax=ax)


def exchange_cycles():
    phase2 = read(PHASE2)["rows"]
    phase3 = read(PHASE3_OLD)["results"]
    phase3 += read(PHASE3_NEW)["results"]
    followup = read(FOLLOWUP)["results"][0]
    # Replace the short beta=1 N=3 point after its split-chain diagnostic.
    phase3 = [r for r in phase3 if not (r["N"] == 3 and r["beta"] == 1.0)]
    phase3.append(followup)
    colors = sns.color_palette("colorblind", 3)
    fig, ax = plt.subplots(figsize=(3.35, 3.05))
    grid = np.geomspace(0.1, 10, 300)
    for n, color, line, marker in zip((2, 3, 4), colors,
                                      ("-", "--", "-."), ("o", "s", "^")):
        if n == 2:
            points = [(r["beta"], r["f"], r["error"]) for r in phase2]
        else:
            points = [(r["beta"], r["class_mc"][-1], r["class_error"][-1])
                      for r in phase3 if r["N"] == n and
                      r.get("class_resolved", [True] * len(r["classes"]))[-1]]
        points.sort()
        beta, probability, error = map(np.array, zip(*points))
        ax.plot(grid, full_cycle_exact(grid, n), color=color, linestyle=line,
                label=rf"$N={n}$")
        ax.errorbar(beta, probability, yerr=error, fmt=marker, color=color,
                    ecolor=color, elinewidth=0.7, capsize=1.5, markeredgecolor="white",
                    markeredgewidth=0.35, linestyle="none")
    ax.set_xscale("log")
    ax.set_xlim(0.09, 11)
    ax.set_ylim(0, 0.55)
    ax.set_xlabel(r"Inverse temperature $\beta\hbar\omega$")
    ax.set_ylabel(r"Full-cycle probability $p_{(N)}$")
    ax.legend(frameon=False, loc="upper left", ncol=1)
    clean_axis(ax)
    save(fig, "exchange_cycles.pdf")


def partition_check():
    rows = read(PHASE3_NEW)["results"]
    followup = read(FOLLOWUP)["results"][0]
    rows = [r for r in rows if not (r["N"] == 3 and r["beta"] == 1.0)]
    rows.append(followup)
    colors = sns.color_palette("colorblind", 3)[1:]
    fig, ax = plt.subplots(figsize=(3.35, 2.65))
    for n, color, marker in zip((3, 4), colors, ("o", "s")):
        points = sorted((r for r in rows if r["N"] == n), key=lambda r: r["beta"])
        beta = [r["beta"] for r in points]
        ratio = [r["z_mc"] / r["z_exact"] for r in points]
        error = [r["z_error"] / r["z_exact"] for r in points]
        ax.errorbar(beta, ratio, yerr=error, fmt=marker, color=color,
                    capsize=2, elinewidth=0.8, linestyle="none", label=rf"$N={n}$")
    ax.axhline(1, color="0.35", linestyle="--", linewidth=0.9)
    ax.set_xscale("log")
    ax.set_xlim(0.08, 12)
    ax.set_ylim(0.89, 1.12)
    ax.set_xlabel(r"Inverse temperature $\beta\hbar\omega$")
    ax.set_ylabel(r"$\widehat Z_N/Z_N^{\mathrm{occ}}$")
    ax.legend(frameon=False, loc="upper right")
    clean_axis(ax)
    save(fig, "partition_check.pdf")


def p_convergence():
    rows = read(STUDY)
    colors = sns.color_palette("colorblind", 3)
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 2.35), sharex=True)
    for ax, n in zip(axes, (3, 4)):
        for beta, color, marker in zip((0.5, 1.0, 5.0), colors,
                                       ("o", "s", "^")):
            points = sorted((r for r in rows if r["N"] == n and r["beta"] == beta
                             and r["mode"] == "global"), key=lambda r: r["P"])
            ax.axhline(points[0]["class_exact"][-1], color=color,
                       linestyle="--", linewidth=0.8)
            ax.errorbar([r["P"] for r in points], [r["class_mc"][-1] for r in points],
                        yerr=[r["class_error"][-1] for r in points], fmt=marker + "-",
                        color=color, capsize=2, linewidth=0.8,
                        label=rf"$\beta\hbar\omega={beta:g}$")
        ax.set_xlabel(r"Imaginary-time slices $P$")
        ax.set_xticks((2, 4, 8, 16))
        ax.set_ylabel(rf"$p_{{({n})}}$" if n == 3 else "")
        clean_axis(ax)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, frameon=False, fontsize=6, ncol=3,
               loc="upper center", bbox_to_anchor=(0.5, 1.10))
    save(fig, "p_convergence.pdf")


def class_exact(beta, n, kinds):
    weights = []
    for kind in kinds:
        counts = [kind.count(length) for length in range(1, n + 1)]
        multiplicity = factorial(n)
        for length, count in enumerate(counts, start=1):
            multiplicity /= length**count * factorial(count)
        weights.append(multiplicity * np.prod(
            [z(beta, length)**count for length, count in enumerate(counts, start=1)]))
    return np.array(weights) / np.sum(weights)


def all_classes(n_values=(3, 4)):
    rows = read(PHASE3_OLD)["results"] + read(PHASE3_NEW)["results"]
    rows = [r for r in rows if not (r["N"] == 3 and r["beta"] == 1.0)]
    rows.append(read(FOLLOWUP)["results"][0])
    line_styles = ("-", "--", "-.", ":", (0, (5, 2, 1, 2)))
    markers = ("o", "s", "^", "D", "v")
    for n in n_values:
        points = sorted((r for r in rows if r["N"] == n), key=lambda r: r["beta"])
        kinds = points[0]["classes"]
        colors = sns.color_palette("colorblind", len(kinds))
        grid = np.geomspace(0.1, 10, 200)
        exact = np.array([class_exact(beta, n, kinds) for beta in grid])
        fig, ax = plt.subplots(figsize=(3.35, 3.05 if n == 4 else 2.75))
        for j, (kind, color, line, marker) in enumerate(zip(
                kinds, colors, line_styles, markers)):
            label = "$" + "+".join(map(str, kind)) + "$"
            ax.plot(grid, exact[:, j], color=color, linestyle=line, label=label)
            chosen = [r for r in points if r.get("class_resolved", [True] * len(kinds))[j]]
            ax.errorbar([r["beta"] for r in chosen],
                        [r["class_mc"][j] for r in chosen],
                        yerr=[r["class_error"][j] for r in chosen],
                        fmt=marker, linestyle="none", color=color,
                        capsize=1.4, elinewidth=0.7, markersize=3)
        ax.set_xscale("log")
        ax.set_xlim(0.09, 11)
        ax.set_ylim(bottom=0)
        ax.set_xlabel(r"Inverse temperature $\beta\hbar\omega$")
        ax.set_ylabel(r"Cycle-class probability $p_\lambda$")
        ax.legend(frameon=False, fontsize=6, ncol=2)
        clean_axis(ax)
        save(fig, f"class_probabilities_N{n}.pdf")


def energy_exact(beta, n):
    beta = np.asarray(beta)
    return n / 2 + sum(length / np.expm1(length * beta)
                       for length in range(1, n + 1))


def energy_control():
    rows = read(PHASE3_OLD)["results"] + read(PHASE3_NEW)["results"]
    rows = [r for r in rows if not (r["N"] == 3 and r["beta"] == 1.0)]
    rows.append(read(FOLLOWUP)["results"][0])
    colors = sns.color_palette("colorblind", 3)[1:]
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 3.05), sharex=True, sharey=True)
    grid = np.geomspace(0.1, 10, 300)
    for ax, n, color in zip(axes, (3, 4), colors):
        points = sorted((r for r in rows if r["N"] == n), key=lambda r: r["beta"])
        ax.plot(grid, energy_exact(grid, n), color="0.2", label="Exact")
        ax.errorbar([r["beta"] for r in points],
                    [r["energy_mc"] for r in points],
                    yerr=[r["energy_error"] for r in points],
                    fmt="o", linestyle="none", color=color,
                    capsize=1.8, elinewidth=0.8, label="PIMC")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlim(0.09, 11)
        ax.set_ylim(1.3, 50)
        ax.set_xlabel(r"Inverse temperature $\beta\hbar\omega$")
        ax.text(0.06, 0.93, rf"$N={n}$", transform=ax.transAxes,
                ha="left", va="top")
        clean_axis(ax)
    axes[0].set_ylabel(r"Energy $E_N/(\hbar\omega)$")
    axes[0].legend(frameon=False, loc="lower left")
    save(fig, "energy_control.pdf")


def sampling_cost():
    rows = read(STUDY)
    colors = sns.color_palette("colorblind", 3)[1:]
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 2.75))
    for n, color, marker in zip((3, 4), colors, ("o", "s")):
        points = sorted((r for r in rows if r["N"] == n and r["beta"] == 1.0
                         and r["mode"] == "global"), key=lambda r: r["P"])
        axes[0].plot([r["P"] for r in points],
                     [r["energy_ess_per_second"] for r in points],
                     marker=marker, color=color, label=rf"$N={n}$")
        global_p4 = next(r for r in points if r["P"] == 4)
        local_p4 = next(r for r in rows if r["N"] == n and r["beta"] == 1.0
                        and r["P"] == 4 and r["mode"] == "local")
        axes[1].plot((0, 1), (local_p4["energy_ess_per_second"],
                              global_p4["energy_ess_per_second"]),
                     marker=marker, color=color, label=rf"$N={n}$")
    axes[0].set_xticks((2, 4, 8, 16))
    axes[0].set_xlabel(r"Imaginary-time slices $P$")
    axes[1].set_xticks((0, 1), ("Local", "Whole cycle"))
    axes[1].set_xlabel(r"Update at $P=4$")
    for ax in axes:
        ax.set_ylabel(r"Effective energy samples / s")
        clean_axis(ax)
    axes[0].legend(frameon=False)
    save(fig, "sampling_cost.pdf")


def worldline_topology():
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 2.35), sharex=True, sharey=True)
    u = np.linspace(0, 1, 200)
    colors = sns.color_palette("colorblind", 2)
    identity = (-0.8 + 0.12 * np.sin(2 * np.pi * u),
                0.8 - 0.12 * np.sin(2 * np.pi * u))
    exchange = (-0.8 + 1.6 * u + 0.10 * np.sin(2 * np.pi * u),
                 0.8 - 1.6 * u - 0.10 * np.sin(2 * np.pi * u))
    for ax, curves, label in zip(axes, (identity, exchange),
                                  (r"(a) $\sigma=\mathrm{id}$",
                                   r"(b) $\sigma=(12)$")):
        for y, color, line in zip(curves, colors, ("-", "--")):
            ax.plot(u, y, color=color, linestyle=line, linewidth=1.7)
            ax.plot((0, 1), (y[0], y[-1]), "o", color=color, markersize=3.5)
        ax.text(0.03, 0.95, label, transform=ax.transAxes, va="top")
        ax.set_xticks((0, 1), ("0", "1"))
        ax.set_xlabel(r"Imaginary time $u/(\beta\hbar)$")
        ax.set_ylim(-1.2, 1.2)
        clean_axis(ax)
    axes[0].set_ylabel(r"Position $x/\sqrt{\hbar/(m\omega)}$")
    save(fig, "worldline_topology.pdf")


def phase2_controls():
    rows = read(PHASE2)["rows"]
    beta = np.array([r["beta"] for r in rows])
    fraction = np.array([r["f"] for r in rows])
    fraction_error = np.array([r["error"] for r in rows])
    grid = np.geomspace(0.1, 10, 300)
    color = sns.color_palette("colorblind", 3)[0]
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 2.55))
    z_exact = (z(grid)**2 + z(grid, 2)) / 2
    z_mc = z(beta)**2 / (2 * (1 - fraction))
    axes[0].plot(grid, z_exact, color="0.2", label="Exact")
    axes[0].errorbar(beta, z_mc, yerr=z_mc * fraction_error / (1 - fraction),
                     fmt="o", color=color, capsize=1.7, label="PIMC")
    axes[0].set_yscale("log")
    axes[0].set_ylabel(r"Bosonic partition function $Z_2$")
    axes[0].legend(frameon=False)
    axes[1].plot(grid, np.tanh(grid / 2), color="0.2", label="Exact")
    axes[1].errorbar(beta, fraction / (1 - fraction),
                     yerr=fraction_error / (1 - fraction)**2,
                     fmt="s", color=color, capsize=1.7, label="PIMC")
    axes[1].set_ylabel(r"Exchange/identity ratio $R$")
    axes[1].legend(frameon=False)
    for ax in axes:
        ax.set_xscale("log")
        ax.set_xlim(0.09, 11)
        ax.set_xlabel(r"Inverse temperature $\beta\hbar\omega$")
        clean_axis(ax)
    save(fig, "phase2_partition_ratio.pdf")


def phase2_energy():
    rows = read(PHASE2)["rows"]
    beta = np.array([r["beta"] for r in rows])
    color = sns.color_palette("colorblind", 3)[0]
    fig, ax = plt.subplots(figsize=(3.35, 2.55))
    grid = np.geomspace(0.1, 10, 300)
    ax.plot(grid, energy_exact(grid, 2), color="0.2", label="Exact")
    ax.errorbar(beta, [r["energy"][0] for r in rows],
                yerr=[r["energy"][1] for r in rows], fmt="o", color=color,
                capsize=1.7, label="PIMC")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel(r"Inverse temperature $\beta\hbar\omega$")
    ax.set_ylabel(r"Energy $E_2/(\hbar\omega)$")
    ax.legend(frameon=False)
    clean_axis(ax)
    save(fig, "phase2_energy.pdf")


def class_histograms():
    rows = read(PHASE3_OLD)["results"]
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 2.85), sharey=True)
    colors = sns.color_palette("colorblind", 2)
    for ax, n in zip(axes, (3, 4)):
        row = min((r for r in rows if r["N"] == n),
                  key=lambda r: abs(r["beta"] - 1))
        positions = np.arange(len(row["classes"]))
        ax.bar(positions, row["class_exact"], width=0.55, color="0.83",
               edgecolor="0.35", linewidth=0.5, label="Exact")
        ax.errorbar(positions, row["class_mc"], yerr=row["class_error"],
                    fmt="o", color=colors[0], capsize=2, label="PIMC")
        labels = ["+".join(map(str, kind)) for kind in row["classes"]]
        ax.set_xticks(positions, labels, rotation=35, ha="right")
        ax.set_xlabel(rf"Cycle class, $N={n}$")
        ax.set_ylim(0, 0.57)
        clean_axis(ax)
    axes[0].set_ylabel(r"Class probability $p_\lambda$")
    axes[0].legend(frameon=False)
    save(fig, "class_histograms.pdf")


def particle_cycle_fractions():
    rows = read(PHASE3_OLD)["results"] + read(PHASE3_NEW)["results"]
    rows = [r for r in rows if not (r["N"] == 3 and r["beta"] == 1.0)]
    rows.append(read(FOLLOWUP)["results"][0])
    colors = sns.color_palette("colorblind", 4)
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 3.0), sharex=True, sharey=True)
    grid = np.geomspace(0.1, 10, 200)
    for ax, n in zip(axes, (3, 4)):
        points = sorted((r for r in rows if r["N"] == n), key=lambda r: r["beta"])
        kinds = points[0]["classes"]
        exact_classes = np.array([class_exact(b, n, kinds) for b in grid])
        for length in range(1, n + 1):
            line = ("-", "--", "-.", ":")[length - 1]
            marker = ("o", "s", "^", "D")[length - 1]
            color = colors[length - 1]
            exact = sum(exact_classes[:, j] * length * kind.count(length) / n
                        for j, kind in enumerate(kinds))
            ax.plot(grid, exact, color=color, linestyle=line,
                    label=rf"$\ell={length}$")
            chosen = []
            for r in points:
                resolved = r.get("class_resolved", [True] * len(kinds))
                contributing = [j for j, kind in enumerate(kinds)
                                if kind.count(length)]
                if all(resolved[j] for j in contributing):
                    chosen.append(r)
            ax.errorbar([r["beta"] for r in chosen],
                        [r["particle_mc"][length - 1] for r in chosen],
                        yerr=[r["particle_error"][length - 1] for r in chosen],
                        fmt=marker, color=color, linestyle="none", capsize=1.4)
        ax.set_xscale("log")
        ax.set_xlim(0.09, 11)
        ax.set_ylim(0, 1.04)
        ax.set_xlabel(r"Inverse temperature $\beta\hbar\omega$")
        ax.text(0.06, 0.94, rf"$N={n}$", transform=ax.transAxes, va="top")
        clean_axis(ax)
    axes[0].set_ylabel(r"Particle-weighted fraction $q_\ell$")
    axes[1].legend(frameon=False, ncol=2, fontsize=6, loc="upper right")
    save(fig, "particle_cycle_fractions.pdf")


def main():
    jobs = {
        "exchange_cycles.pdf": exchange_cycles,
        "partition_check.pdf": partition_check,
        "p_convergence.pdf": p_convergence,
        "class_probabilities_N3.pdf": lambda: all_classes((3,)),
        "class_probabilities_N4.pdf": lambda: all_classes((4,)),
        "energy_control.pdf": energy_control,
        "sampling_cost.pdf": sampling_cost,
        "worldline_topology.pdf": worldline_topology,
        "phase2_partition_ratio.pdf": phase2_controls,
        "phase2_energy.pdf": phase2_energy,
        "class_histograms.pdf": class_histograms,
        "particle_cycle_fractions.pdf": particle_cycle_fractions,
    }
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="list available figure names")
    parser.add_argument("--figure", action="append", choices=jobs,
                        help="generate only this figure; may be repeated")
    args = parser.parse_args()
    if args.list:
        print("\n".join(jobs))
        return
    style()
    for name in args.figure or jobs:
        jobs[name]()


if __name__ == "__main__":
    main()
