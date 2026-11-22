"""Tests de propagador.py: traza = Z1, propiedad de semigrupo y positividad."""

import numpy as np
from scipy import integrate

import analytic
from propagador import rho


OMEGA = 1.0
NMAX = 400


def test_trace_equals_Z1():
    # integral de rho(x, x, tau) dx == Z1(beta=tau)
    tau = 0.7
    f = lambda x: rho(x, x, tau, OMEGA)
    val, _ = integrate.quad(f, -20, 20)
    z1 = analytic.Z1(tau, OMEGA, NMAX)
    assert abs(val - z1) / z1 < 1e-6


def test_semigroup_property():
    # rho(x, x', 2tau) == integral rho(x, y, tau) rho(y, x', tau) dy
    tau = 0.4
    x, xp = 0.3, -0.5
    direct = rho(x, xp, 2.0 * tau, OMEGA)
    integrand = lambda y: rho(x, y, tau, OMEGA) * rho(y, xp, tau, OMEGA)
    conv, _ = integrate.quad(integrand, -20, 20)
    assert abs(direct - conv) / direct < 1e-6


def test_positivity():
    xs = np.linspace(-3, 3, 25)
    for tau in (0.1, 0.5, 2.0):
        for x in xs:
            for xp in xs:
                assert rho(x, xp, tau, OMEGA) > 0.0


def test_vectorized_matches_scalar():
    tau = 0.6
    xs = np.array([-1.0, 0.0, 1.5])
    xps = np.array([0.5, -0.5, 2.0])
    vec = rho(xs, xps, tau, OMEGA)
    for i in range(len(xs)):
        assert abs(vec[i] - rho(float(xs[i]), float(xps[i]), tau, OMEGA)) < 1e-12
