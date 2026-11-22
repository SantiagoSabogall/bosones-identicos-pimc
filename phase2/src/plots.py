"""Graficas de la fase 2: histograma de ciclos, frecuencia de intercambio y energia.

Genera PNGs en el directorio del proyecto:
  - cycles_hist.png        : histograma de longitudes de ciclo (1 vs 2).
  - exchange_vs_T.png      : fraccion de intercambio vs temperatura.
  - energy_vs_T.png        : energia muestreada vs exacta vs temperatura.
  - worldlines.png         : visualizacion simple de worldlines de ejemplo.
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import analytic
from params import Params
from sampler import PIMCSampler
from observables import Accumulator
from sectors import EXCHANGE, IDENTITY

HERE = os.path.dirname(os.path.abspath(__file__))


def plot_cycle_histogram(acc, path):
    hist = acc.cycle_histogram()
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.bar(["1-ciclos", "2-ciclos"],
           [hist["cycle_len_1"], hist["cycle_len_2"]],
           color=["#4878CF", "#D65F5F"])
    ax.set_ylabel("conteo total sobre muestras")
    ax.set_title("Histograma de longitudes de ciclo (N=2)")
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def sweep_temperature(betas, base=None):
    """Corre PIMC y el exacto en un barrido de beta. Devuelve arrays alineados."""
    if base is None:
        base = Params()
    E_mc, E_err, E_ex = [], [], []
    f_mc, f_err, f_ex = [], [], []
    for b in betas:
        p = Params(N=base.N, beta=float(b), omega=base.omega, nmax=base.nmax,
                   P=base.P, n_steps=base.n_steps, n_burn=base.n_burn,
                   delta=base.delta, seed=base.seed)
        s = PIMCSampler(p)
        acc = Accumulator()
        s.run(record_fn=acc.record)
        em, ee = acc.energy_mean_err()
        fm, fe = acc.exchange_fraction()
        E_mc.append(em); E_err.append(ee)
        f_mc.append(fm); f_err.append(fe)
        E_ex.append(analytic.energy_boson_2(p.beta, p.omega, p.nmax))
        f_ex.append(analytic.exchange_weight_fraction(p.beta, p.omega, p.nmax))
    return (np.array(E_mc), np.array(E_err), np.array(E_ex),
            np.array(f_mc), np.array(f_err), np.array(f_ex))


def plot_exchange_vs_T(betas, f_mc, f_err, f_ex, path):
    T = 1.0 / betas
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.errorbar(T, f_mc, yerr=f_err, fmt="o", capsize=3, label="PIMC", color="#D65F5F")
    order = np.argsort(T)
    ax.plot(T[order], f_ex[order], "-", label="exacto", color="#4878CF")
    ax.set_xlabel("temperatura T = 1/beta")
    ax.set_ylabel("fraccion de intercambio")
    ax.set_title("Frecuencia de intercambio vs temperatura (N=2)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def plot_energy_vs_T(betas, E_mc, E_err, E_ex, path):
    T = 1.0 / betas
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.errorbar(T, E_mc, yerr=E_err, fmt="o", capsize=3, label="PIMC", color="#D65F5F")
    order = np.argsort(T)
    ax.plot(T[order], E_ex[order], "-", label="exacto", color="#4878CF")
    ax.set_xlabel("temperatura T = 1/beta")
    ax.set_ylabel("energia media E")
    ax.set_title("Energia muestreada vs exacta (N=2)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def plot_worldlines(path, params=None):
    """Worldlines de una configuracion de ejemplo en cada sector."""
    if params is None:
        params = Params(n_burn=2000, n_steps=1)
    fig, axes = plt.subplots(1, 2, figsize=(9, 4), sharey=True)
    for ax, sector, title in ((axes[0], IDENTITY, "sector identidad"),
                              (axes[1], EXCHANGE, "sector intercambio")):
        s = PIMCSampler(params)
        s.perm = sector
        for _ in range(params.n_burn):
            s.sweep()
            s.perm = sector  # fijar el sector para la ilustracion
        P = s.P
        tau_axis = np.arange(P) * s.tau
        for i in (0, 1):
            ax.plot(s.x[i], tau_axis, "-o", ms=3,
                    color=("#4878CF" if i == 0 else "#D65F5F"),
                    label=f"particula {i}")
        ax.set_xlabel("posicion x")
        ax.set_title(title)
        ax.legend(fontsize=8)
    axes[0].set_ylabel("tiempo imaginario tau")
    fig.suptitle("Worldlines de ejemplo (N=2)")
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def main():
    base = Params()
    # Histograma de ciclos de una corrida
    s = PIMCSampler(base)
    acc = Accumulator()
    s.run(record_fn=acc.record)
    plot_cycle_histogram(acc, os.path.join(HERE, "cycles_hist.png"))

    # Barrido de temperatura. Rango beta >= 0.5: a beta mucho menor (T muy alta)
    # el estimador termodinamico de energia tiene gran varianza por la
    # cancelacion -0.5*w*c/s y el modo colectivo del anillo mezcla lento; ese
    # regimen requeriria P y muestreo mucho mayores. La fisica de fase 2
    # (fraccion de intercambio vs T y acuerdo con Z exacta) se demuestra aqui.
    sweep_base = Params(N=base.N, omega=base.omega, nmax=base.nmax, P=base.P,
                        n_steps=20_000, n_burn=5_000, delta=base.delta, seed=base.seed)
    betas = np.array([0.5, 1.0, 2.0, 4.0, 8.0])
    E_mc, E_err, E_ex, f_mc, f_err, f_ex = sweep_temperature(betas, sweep_base)
    plot_exchange_vs_T(betas, f_mc, f_err, f_ex, os.path.join(HERE, "exchange_vs_T.png"))
    plot_energy_vs_T(betas, E_mc, E_err, E_ex, os.path.join(HERE, "energy_vs_T.png"))

    # Worldlines
    plot_worldlines(os.path.join(HERE, "worldlines.png"))
    print("PNGs generados en", HERE)


if __name__ == "__main__":
    main()
