"""Monte Carlo sweep over temperature for the N=2 boson PIMC pipeline.

Runs the OFFICIAL sampler (`sampler.PIMCSampler` with the exact Mehler
propagator) over a grid of inverse temperatures `beta`, and records the
exchange-sector fraction `f` with its block-averaging error. From `f` it builds
the three observables the figures need, each paired with its exact closed form:

  - f     : fraction of MC time in the exchange sector    -> Figure 3 (P_ex)
  - R     : exchange/identity weight ratio = f / (1 - f)  -> Figure 2
  - Z2    : reference-sector reconstruction                -> Figure 1
            Z2 = 0.5 * z(beta)^2 / (1 - f),  z(beta) = 1/(2 sinh(beta/2))

This is the SINGLE source of MC data for all three figures: one sweep, one
sampler, no duplicated standalone samplers. Results are saved to an `.npz`
together with the run metadata (P, n_steps, n_burn, omega, seeds) so a figure
can never be drawn from stale or mismatched data.
"""

import os

import numpy as np

import analytic
from params import Params
from sampler import PIMCSampler
from observables import Accumulator, sampling_diagnostics


def sweep(betas, p_base=None, seed0=12345):
    """Run the official sampler at each beta; return aligned observable arrays.

    A distinct seed (seed0 + index) is used per beta so the points are
    statistically independent. Errors propagate from the block-averaging error
    on the exchange fraction f:

        R  = f / (1 - f),       sigma_R  = sigma_f / (1 - f)^2
        Z2 = 0.5 z^2 / (1 - f), sigma_Z2 = Z2 * sigma_f / (1 - f)
    """
    if p_base is None:
        p_base = Params()
    betas = [float(b) for b in betas]

    f_mc, f_err, acc_perm = [], [], []
    valid = []
    for n, b in enumerate(betas):
        p = Params(N=p_base.N, beta=b, omega=p_base.omega, nmax=p_base.nmax,
                   P=p_base.P, n_steps=p_base.n_steps, n_burn=p_base.n_burn,
                   delta=p_base.delta, seed=seed0 + n)
        s = PIMCSampler(p)
        acc = Accumulator()
        s.run(record_fn=acc.record)
        f, sf = acc.exchange_fraction()
        valid.append(sampling_diagnostics(acc.exchange_flags)["valid"])
        f_mc.append(f)
        f_err.append(sf)
        acc_perm.append(s.acceptance_rates()["perm"])

    b = np.asarray(betas)
    f = np.asarray(f_mc)
    sf = np.asarray(f_err)
    omega = p_base.omega

    one_minus_f = 1.0 - f
    R_mc = f / one_minus_f
    R_err = sf / one_minus_f ** 2
    z2 = 0.5 * analytic.z1_closed(b, omega) ** 2 / one_minus_f
    z2_err = z2 * sf / one_minus_f

    return {
        "betas": b,
        "valid": np.asarray(valid),
        "meta_omega": omega,
        "f_mc": f,
        "f_err": sf,
        "f_exact": analytic.pex_exact(b, omega),
        "R_mc": R_mc,
        "R_err": R_err,
        "R_exact": analytic.R_exchange_exact(b, omega),
        "Z2_mc": z2,
        "Z2_err": z2_err,
        "Z2_exact": np.asarray([analytic.Z_boson_2(float(x), omega, p_base.nmax)
                                for x in b]),
        "acc_perm": np.asarray(acc_perm),
    }


def save_sweep(path, data, p_base, seed0=12345):
    """Save sweep arrays plus run metadata to an .npz file."""
    d = os.path.dirname(os.path.abspath(path))
    os.makedirs(d, exist_ok=True)
    data = dict(data)
    data.pop("meta_omega", None)
    np.savez(
        path,
        meta_P=p_base.P, meta_n_steps=p_base.n_steps, meta_n_burn=p_base.n_burn,
        meta_omega=p_base.omega, meta_delta=p_base.delta, meta_seed0=seed0,
        **data,
    )


def load_sweep(path):
    """Load a sweep .npz into a plain dict of arrays."""
    with np.load(path) as z:
        return {k: z[k] for k in z.files}


# Default production sweep: beta from 0.1 (high T, exchange negligible) to 10
# (low T, exchange saturates). The exchange fraction is well behaved across the
# whole range because it only tracks the sector occupation, not the energy
# estimator (which is noisy at very high T, see plots.py).
DEFAULT_BETAS = np.geomspace(0.1, 10.0, 10)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "..", "data", "sweep_phase2.npz")
    p_base = Params(P=12, n_steps=20_000, n_burn=4_000, delta=0.6)
    data = sweep(DEFAULT_BETAS, p_base=p_base, seed0=20261108)
    save_sweep(out, data, p_base, seed0=20261108)
    print(f"sweep saved to {os.path.abspath(out)}  ({len(DEFAULT_BETAS)} betas)")
    for i, b in enumerate(data["betas"]):
        dev = abs(data["f_mc"][i] - data["f_exact"][i]) / data["f_err"][i]
        print(f"  beta={b:6.3f}  f_mc={data['f_mc'][i]:.4f} +/- "
              f"{data['f_err'][i]:.4f}  f_ex={data['f_exact'][i]:.4f}  "
              f"({dev:4.1f} sigma)  acc_perm={data['acc_perm'][i]:.3f}")


if __name__ == "__main__":
    main()
