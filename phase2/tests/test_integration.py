"""Test de integracion end-to-end de la fase 2.

Criterio de exito: el muestreador PIMC reproduce el control exacto.
  (a) energia muestreada coincide con analytic dentro de ~3-4 sigma;
  (b) el muestreador visita AMBOS sectores (0 < frac intercambio < 1);
  (c) auditoria de normalizacion: la fraccion de intercambio coincide con la exacta;
  (d) convergencia al aumentar P (reducir tau = beta/P).
"""

import numpy as np

import analytic
from params import Params
from sampler import PIMCSampler
from observables import Accumulator
from run_phase2 import run


import pytest


def _short_params(**kw):
    # beta=1.0: regimen bien convergido para el heat-bath (ver plots.py sobre alta T).
    base = dict(N=2, beta=1.0, omega=1.0, nmax=400,
                P=12, n_steps=25_000, n_burn=5_000, delta=0.6, seed=2024)
    base.update(kw)
    return Params(**base)


@pytest.fixture(scope="module")
def control_run():
    # Una sola cadena compartida por los tres criterios de equilibrio (a, b, c).
    return run(_short_params(), verbose=False)


def test_energy_matches_exact_within_sigma(control_run):
    res = control_run
    dev = abs(res["E_mc"] - res["E_exact"]) / res["E_err"]
    assert dev < 3.0, f"energia a {dev:.1f} sigma (mc={res['E_mc']:.3f}, ex={res['E_exact']:.3f})"


def test_both_sectors_visited(control_run):
    res = control_run
    assert 0.0 < res["f_mc"] < 1.0, f"frac intercambio = {res['f_mc']}"


def test_exchange_fraction_normalization(control_run):
    # Auditoria de normalizacion: la razon de pesos entre sectores produce
    # la fraccion de intercambio exacta (incluye el factor de simetrizacion).
    res = control_run
    dev = abs(res["f_mc"] - res["f_exact"]) / res["f_err"]
    assert dev < 3.0, f"frac intercambio a {dev:.1f} sigma (mc={res['f_mc']:.3f}, ex={res['f_exact']:.3f})"


def test_consistency_across_P():
    # Mehler es exacto para cualquier P admitido: comprobar consistencia.
    res_coarse = run(_short_params(P=3, n_steps=20_000), verbose=False)
    res_fine = run(_short_params(P=16, n_steps=20_000), verbose=False)
    err_coarse = abs(res_coarse["E_mc"] - res_coarse["E_exact"])
    err_fine = abs(res_fine["E_mc"] - res_fine["E_exact"])
    # P fino no debe ser peor que P grueso por mas de la barra de error combinada.
    assert err_fine <= err_coarse + 2.0 * (res_coarse["E_err"] + res_fine["E_err"])
