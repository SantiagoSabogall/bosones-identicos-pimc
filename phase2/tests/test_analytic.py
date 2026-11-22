"""Tests de analytic.py: limites de alta y baja temperatura y convergencia."""

import numpy as np

from params import HBAR
import analytic


OMEGA = 1.0
NMAX = 400


def test_high_T_Z_approx_half_Z1_squared():
    # beta -> 0 : Z1(2beta) ~ Z1(beta), ambos grandes; Z_B ~ Z1^2/2 domina.
    beta = 1e-3
    z1 = analytic.Z1(beta, OMEGA, NMAX)
    zB = analytic.Z_boson_2(beta, OMEGA, NMAX)
    # El termino de intercambio Z1(2beta)/2 es despreciable frente a Z1^2/2.
    assert abs(zB - 0.5 * z1 * z1) / (0.5 * z1 * z1) < 1e-2


def test_high_T_energy_classical_limit():
    # Limite clasico: E -> 2 * kT = 2 / beta  (2 osciladores, equiparticion).
    # beta debe ser pequeno pero compatible con la truncacion nmax: los niveles
    # relevantes van hasta n ~ 1/(beta*omega), asi que beta*omega*nmax >> 1.
    beta = 0.05  # con nmax=400 => beta*nmax = 20 >> 1, suma converge
    E = analytic.energy_boson_2(beta, OMEGA, NMAX)
    assert abs(E - 2.0 / beta) / (2.0 / beta) < 2e-2


def test_low_T_energy_ground_state():
    # Limite de baja T: E -> energia del estado fundamental = 2 * (hbar*omega/2).
    beta = 50.0
    E = analytic.energy_boson_2(beta, OMEGA, NMAX)
    E0 = 2.0 * (HBAR * OMEGA / 2.0)
    assert abs(E - E0) < 1e-3


def test_Z_positive_and_monotone_in_beta():
    betas = np.linspace(0.1, 10.0, 50)
    Zs = np.array([analytic.Z_boson_2(b, OMEGA, NMAX) for b in betas])
    assert np.all(Zs > 0.0)
    # Z decrece monotonamente al aumentar beta (baja T).
    assert np.all(np.diff(Zs) < 0.0)


def test_nmax_convergence():
    beta = 1.0
    z_small = analytic.Z_boson_2(beta, OMEGA, 50)
    z_large = analytic.Z_boson_2(beta, OMEGA, 500)
    assert abs(z_large - z_small) < 1e-8


def test_energy_matches_two_times_single():
    # 2 bosones ideales: la energia NO es simplemente 2*E1 por el termino de
    # intercambio, pero a alta T debe acercarse a 2*E1. Comprobacion de cordura.
    beta = 0.05  # compatible con truncacion nmax=400
    E = analytic.energy_boson_2(beta, OMEGA, NMAX)
    E1 = analytic.energy_1(beta, OMEGA, NMAX)  # formula cerrada, exacta
    assert abs(E - 2.0 * E1) / (2.0 * E1) < 5e-2
