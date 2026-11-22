"""Publication figures for the N=2 boson PIMC pipeline.

Reads one MC sweep (see `mc_sweep.py`) and draws three figures, each with a
main panel (PIMC points vs exact closed form) and a residual panel in units of
the statistical error sigma:

  Figure 1  fig1_Z2_mc_vs_exact.png     : Z2 partition function, MC vs exact.
  Figure 2  fig2_exchange_term_vs_T.png : exchange-term contribution R(T).
  Figure 3  fig3_cycle_fraction_vs_T.png: MC exchange-sector fraction P_ex(T).

All three come from the SAME sweep (one official sampler run per beta); the
figures never re-run physics, so they cannot disagree with the sampled data.
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import analytic
import mc_sweep


MC_COLOR = "#D65F5F"
EX_COLOR = "#4878CF"


def _residual_axes(fig):
    """Two stacked axes sharing x: main (3/1) on top, residual below."""
    gs = fig.add_gridspec(2, 1, height_ratios=[3, 1], hspace=0.08)
    a_main = fig.add_subplot(gs[0, 0])
    a_res = fig.add_subplot(gs[1, 0], sharex=a_main)
    plt.setp(a_main.get_xticklabels(), visible=False)
    return a_main, a_res


def _draw_sigma_bands(ax):
    ax.axhline(0, c="k", lw=0.8)
    for s in (-3, -2, 2, 3):
        ax.axhline(s, ls=":" if abs(s) == 2 else "--", c="gray", lw=0.8)
    ax.set_ylim(-4.5, 4.5)


def _residual(mc, exact, err):
    """Residual in sigma, with finite errors only.

    A sampled fraction that never left a sector gives err == 0 (no estimable
    error bar); such a point has no meaningful residual, so it is masked out of
    the residual panel rather than plotted at +/-inf.
    """
    mc = np.asarray(mc, float)
    exact = np.asarray(exact, float)
    err = np.asarray(err, float)
    good = np.isfinite(err) & (err > 0)
    res = np.full_like(mc, np.nan)
    res[good] = (mc[good] - exact[good]) / err[good]
    return res, good


def _footer(fig, meta):
    if not meta:
        return
    txt = (f"Mehler, P={meta.get('P', '?')}, "
           f"{meta.get('n_steps', '?')} steps + {meta.get('n_burn', '?')} burn-in, "
           f"see summary.json for blocks and replicas")
    fig.text(0.5, 0.005, txt, ha="center", fontsize=7)


def figure_Z2(data, path, meta=None):
    """Figure 1: Z2 (Monte Carlo) vs Z2 (exact) as a function of T."""
    omega = float(data.get("meta_omega", 1.0))
    T = 1.0 / data["betas"]
    fig = plt.figure(figsize=(6, 6.2))
    a1, a2 = _residual_axes(fig)

    bb = np.geomspace(data["betas"].min(), data["betas"].max(), 400)
    Z2_curve = 0.5 * (analytic.z1_closed(bb, omega) ** 2 + analytic.z1_closed(2.0 * bb, omega))
    a1.semilogy(1.0 / bb, Z2_curve, "-", c=EX_COLOR,
                label=r"exacto: $\frac{1}{2}(z(\beta)^2+z(2\beta))$")
    a1.errorbar(T, data["Z2_mc"], data["Z2_err"], fmt="o", ms=6, capsize=4,
                elinewidth=1.5, c=MC_COLOR, label="PIMC (sector de referencia)")
    a1.set_ylabel(r"$Z_2$")
    a1.set_title(r"Funcion de particion de 2 bosones (N=2, oscilador 1D)")
    a1.legend(loc="upper right")

    res, good = _residual(data["Z2_mc"], data["Z2_exact"], data["Z2_err"])
    a2.errorbar(T[good], res[good], 1, fmt="o", c=MC_COLOR, capsize=3)
    _draw_sigma_bands(a2)
    a2.set_xscale("log")
    a2.set_xlabel(r"$T = 1/\beta$  (unidades naturales, $k_B=1$)")
    a2.set_ylabel(r"$(Z_2^{MC}-Z_2^{ex})/\sigma$")
    _footer(fig, meta)
    fig.subplots_adjust(left=0.16, right=0.96, top=0.93, bottom=0.11)
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def figure_exchange_term(data, path, meta=None):
    """Figure 2: contribution of the exchange term R = z(2b)/z(b)^2 vs T."""
    omega = float(data.get("meta_omega", 1.0))
    T = 1.0 / data["betas"]
    fig = plt.figure(figsize=(6, 6.2))
    a1, a2 = _residual_axes(fig)

    bb = np.geomspace(data["betas"].min(), data["betas"].max(), 400)
    TT = 1.0 / bb
    a1.plot(TT, analytic.R_exchange_exact(bb, omega), "-", c=EX_COLOR,
            label=r"exacto: $\tanh(\beta\omega/2)$")
    m = TT >= omega
    a1.plot(TT[m], bb[m] * omega / 2.0, ":", c="gray", label=r"alta $T$: $\beta\omega/2$")
    a1.axhline(1.0, ls="--", c="gray", lw=0.8)
    a1.errorbar(T, data["R_mc"], data["R_err"], fmt="o", ms=6, capsize=4,
                elinewidth=1.5, c=MC_COLOR, label="PIMC")
    a1.set_ylim(0, 1.15)
    a1.set_ylabel(r"$R=Z_{\mathrm{int}}/Z_{\mathrm{id}}=z(2\beta)/z(\beta)^2$")
    a1.set_title(r"Contribucion del termino de intercambio (N=2)")
    a1.legend(loc="upper right")

    res, good = _residual(data["R_mc"], data["R_exact"], data["R_err"])
    a2.errorbar(T[good], res[good], 1, fmt="o", c=MC_COLOR, capsize=3)
    _draw_sigma_bands(a2)
    a2.set_xscale("log")
    a2.set_xlabel(r"$T = 1/\beta$  (unidades naturales, $k_B=1$)")
    a2.set_ylabel(r"$(R_{MC}-R_{ex})/\sigma$")
    _footer(fig, meta)
    fig.subplots_adjust(left=0.16, right=0.96, top=0.93, bottom=0.11)
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def figure_cycle_fraction(data, path, meta=None):
    """Figure 3: MC exchange-sector fraction P_ex vs T."""
    omega = float(data.get("meta_omega", 1.0))
    T = 1.0 / data["betas"]
    fig = plt.figure(figsize=(6, 6.2))
    a1, a2 = _residual_axes(fig)

    bb = np.geomspace(data["betas"].min(), data["betas"].max(), 400)
    TT = 1.0 / bb
    a1.plot(TT, analytic.pex_exact(bb, omega), "-", c=EX_COLOR,
            label=r"exacto: $(1-e^{-\beta\omega})/2$")
    a1.axhline(0.5, ls="--", c="gray", lw=0.8)
    a1.errorbar(T, data["f_mc"], data["f_err"], fmt="o", ms=6, capsize=4,
                elinewidth=1.5, c=MC_COLOR, label="PIMC")
    a1.set_ylim(0, 0.6)
    a1.set_ylabel(r"fraccion MC en sector intercambio, $P_{\mathrm{ex}}$")
    a1.set_title(r"Frecuencia de ciclos de permutacion vs $T$ (N=2)")
    a1.legend(loc="upper right")

    res, good = _residual(data["f_mc"], data["f_exact"], data["f_err"])
    a2.errorbar(T[good], res[good], 1, fmt="o", c=MC_COLOR, capsize=3)
    _draw_sigma_bands(a2)
    a2.set_xscale("log")
    a2.set_xlabel(r"$T = 1/\beta$  (unidades naturales, $k_B=1$)")
    a2.set_ylabel(r"$(P_{MC}-P_{ex})/\sigma$")
    _footer(fig, meta)
    fig.subplots_adjust(left=0.16, right=0.96, top=0.93, bottom=0.11)
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def _meta_from_data(data):
    """Extract metadata keys (meta_*) saved alongside the sweep arrays."""
    return {
        "P": int(data["meta_P"]) if "meta_P" in data else None,
        "n_steps": int(data["meta_n_steps"]) if "meta_n_steps" in data else None,
        "n_burn": int(data["meta_n_burn"]) if "meta_n_burn" in data else None,
    }


def make_all(data, outdir):
    """Write all three figures into `outdir`; return their paths in order."""
    os.makedirs(outdir, exist_ok=True)
    meta = _meta_from_data(data)
    return [
        figure_Z2(data, os.path.join(outdir, "fig1_Z2_mc_vs_exact.png"), meta),
        figure_exchange_term(data, os.path.join(outdir, "fig2_exchange_term_vs_T.png"), meta),
        figure_cycle_fraction(data, os.path.join(outdir, "fig3_cycle_fraction_vs_T.png"), meta),
    ]


def main():
    # Entrada única validada: no reutilizar el npz heredado sin verificar.
    from validate_phase2 import run_pipeline
    run_pipeline()


if __name__ == "__main__":
    main()
