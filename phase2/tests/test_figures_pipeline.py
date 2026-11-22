"""Tests for the figures pipeline: closed-form exact helpers and Z2 reconstruction.

Covers S1 (Z2 reconstruction), S2 (exchange-term ratio R), S3 (exchange fraction P_ex).
"""

import numpy as np

import analytic


OMEGA = 1.0
NMAX = 400


def test_z1_closed_matches_truncated_sum():
    # Closed form z(beta) = 1/(2 sinh(beta/2)) must match the truncated level sum.
    for beta in (0.1, 0.5, 1.0, 4.0, 10.0):
        assert abs(analytic.z1_closed(beta) - analytic.Z1(beta, OMEGA, NMAX)) < 1e-9


def test_R_exchange_exact_equals_tanh_half_beta():
    # R = z(2 beta) / z(beta)^2 = tanh(beta/2).
    for beta in (0.1, 0.5, 1.0, 4.0, 10.0):
        R = analytic.R_exchange_exact(beta)
        assert abs(R - np.tanh(beta / 2.0)) < 1e-12
        # consistency with the ratio of closed-form partition functions
        z = analytic.z1_closed
        assert abs(R - z(2.0 * beta) / z(beta) ** 2) < 1e-12


def test_R_exchange_limits():
    # High T (beta->0): exchange term negligible, R -> 0. Low T (beta->inf): R -> 1.
    assert analytic.R_exchange_exact(1e-3) < 1e-2
    assert analytic.R_exchange_exact(40.0) > 1.0 - 1e-6


def test_pex_exact_equals_closed_form():
    # P_ex = z(2 beta)/(z(beta)^2 + z(2 beta)) = (1 - exp(-beta)) / 2.
    for beta in (0.1, 0.5, 1.0, 4.0, 10.0):
        pex = analytic.pex_exact(beta)
        assert abs(pex - (1.0 - np.exp(-beta)) / 2.0) < 1e-12
        # equals the truncated-sum exchange_weight_fraction
        assert abs(pex - analytic.exchange_weight_fraction(beta, OMEGA, NMAX)) < 1e-6


def test_pex_limits():
    # High T -> 0 (classical Boltzmann), low T -> 1/2.
    assert analytic.pex_exact(1e-3) < 1e-3
    assert abs(analytic.pex_exact(40.0) - 0.5) < 1e-6


def test_Z2_from_fraction_recovers_exact_at_exact_f():
    # Reference-sector reconstruction with the exact fraction must give Z2_exact.
    for beta in (0.2, 1.0, 4.0):
        f = analytic.pex_exact(beta)
        Z2 = analytic.Z2_from_fraction(beta, f)
        Z2_exact = analytic.Z_boson_2(beta, OMEGA, NMAX)
        assert abs(Z2 - Z2_exact) / Z2_exact < 1e-6


# --- T2: MC sweep over beta using the official sampler -----------------------

import os

import mc_sweep
from params import Params


def test_sweep_roundtrip_and_fields(tmp_path):
    # A tiny sweep: structure, exact references, and save/load roundtrip.
    betas = [0.5, 2.0]
    p = Params(P=8, n_steps=4000, n_burn=1000, seed=321)
    data = mc_sweep.sweep(betas, p_base=p, seed0=321)
    for key in ("betas", "f_mc", "f_err", "f_exact", "R_mc", "R_err",
                "R_exact", "Z2_mc", "Z2_err", "Z2_exact", "acc_perm"):
        assert key in data and len(data[key]) == len(betas)
    # exact references are the closed forms, independent of sampling
    assert abs(data["f_exact"][0] - analytic.pex_exact(0.5)) < 1e-12
    assert abs(data["R_exact"][1] - analytic.R_exchange_exact(2.0)) < 1e-12
    out = os.path.join(tmp_path, "sweep.npz")
    mc_sweep.save_sweep(out, data, p)
    loaded = mc_sweep.load_sweep(out)
    assert np.allclose(loaded["betas"], data["betas"])
    assert np.allclose(loaded["f_mc"], data["f_mc"])
    assert int(loaded["meta_P"]) == p.P


def test_sweep_fraction_matches_exact_and_grows_with_beta():
    # f_mc tracks the exact fraction (within a few sigma) and grows as T drops.
    betas = [0.5, 4.0]
    p = Params(P=12, n_steps=12000, n_burn=3000, seed=99)
    data = mc_sweep.sweep(betas, p_base=p, seed0=99)
    for i, b in enumerate(betas):
        dev = abs(data["f_mc"][i] - data["f_exact"][i]) / data["f_err"][i]
        assert dev < 4.0, f"beta={b}: f_mc off by {dev:.1f} sigma"
    assert data["f_mc"][1] > data["f_mc"][0]  # more exchange at lower T


# --- T3: figures with residual panels ---------------------------------------

import figures_phase2


def _synthetic_sweep(betas):
    # Build a data dict from the exact closed forms (no sampling): f_mc = f_exact,
    # tiny nonzero errors so residuals are finite.
    b = np.asarray([float(x) for x in betas])
    f = analytic.pex_exact(b)
    sf = np.full_like(b, 0.01)
    one_minus_f = 1.0 - f
    return {
        "betas": b, "f_mc": f, "f_err": sf, "f_exact": analytic.pex_exact(b),
        "R_mc": f / one_minus_f, "R_err": sf / one_minus_f ** 2,
        "R_exact": analytic.R_exchange_exact(b),
        "Z2_mc": 0.5 * analytic.z1_closed(b) ** 2 / one_minus_f,
        "Z2_err": np.full_like(b, 1e-3),
        "Z2_exact": np.asarray([analytic.Z_boson_2(float(x), OMEGA, NMAX) for x in b]),
        "acc_perm": np.full_like(b, 0.3),
    }


def test_three_figures_written(tmp_path):
    data = _synthetic_sweep([0.2, 0.5, 1.0, 2.0, 5.0])
    paths = figures_phase2.make_all(data, outdir=str(tmp_path))
    assert len(paths) == 3
    for p in paths:
        assert os.path.exists(p) and os.path.getsize(p) > 0


def test_figures_handle_zero_error_point(tmp_path):
    # A sampled fraction that never left a sector gives f_err == 0 at that beta.
    # Figures must still render: the residual panel masks that point instead of
    # dividing by zero. Regression for the high-T (beta=0.1) sweep point.
    data = _synthetic_sweep([0.1, 0.5, 1.0, 4.0])
    data["f_mc"][0] = 0.0
    data["f_err"][0] = 0.0
    data["R_mc"][0] = 0.0
    data["R_err"][0] = 0.0
    data["Z2_err"][0] = 0.0
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("error", RuntimeWarning)
        paths = figures_phase2.make_all(data, outdir=str(tmp_path))
    assert len(paths) == 3
    for p in paths:
        assert os.path.exists(p) and os.path.getsize(p) > 0
