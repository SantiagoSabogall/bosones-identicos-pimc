"""Control canónico independiente mediante ocupaciones del oscilador 1D."""
from itertools import combinations_with_replacement
from math import exp, log
import numpy as np


def _check(N, beta, omega):
    if N not in (2, 3, 4) or beta <= 0 or omega <= 0:
        raise ValueError("Se requiere N=2,3,4 y beta, omega positivos")


def log_partition(N, beta, omega=1.0):
    """Producto de ocupaciones, sin importar la enumeración de ciclos."""
    _check(N, beta, omega)
    a = beta * omega
    return -N * a / 2 - sum(np.log(-np.expm1(-j * a))
                             for j in range(1, N + 1))


def partition(N, beta, omega=1.0):
    return float(exp(log_partition(N, beta, omega)))


def energy(N, beta, omega=1.0):
    """Derivada analítica del producto de ocupaciones."""
    _check(N, beta, omega)
    a = beta * omega
    return float(N * omega / 2 +
                 sum(j * omega / np.expm1(j * a) for j in range(1, N + 1)))


def finite_level_sum(N, beta, omega=1.0, max_level=40):
    """Suma directa sobre n_1<=...<=n_N; converge por abajo al Z exacto."""
    _check(N, beta, omega)
    if max_level < 0:
        raise ValueError("max_level debe ser no negativo")
    return sum(exp(-beta * omega * (sum(state) + N / 2))
               for state in combinations_with_replacement(range(max_level + 1), N))
