"""Calculo de control exacto: funcion de particion de 2 bosones en un oscilador 1D.

Niveles de 1 particula:  E_n = hbar*omega*(n + 1/2),  n = 0,1,2,...
Z de 1 particula:        Z1(beta) = sum_n exp(-beta*E_n)
Z simetrizada de 2 bosones (sin espin):
    Z_B = ( Z1(beta)^2 + Z1(2*beta) ) / 2

El termino Z1(2*beta)/2 es la contribucion de intercambio (ciclo de longitud 2).
"""

import numpy as np

from params import HBAR


def Z1(beta, omega, nmax):
    """Funcion de particion de 1 particula (oscilador armonico 1D)."""
    n = np.arange(nmax + 1)
    En = HBAR * omega * (n + 0.5)
    return float(np.sum(np.exp(-beta * En)))


def Z_boson_2(beta, omega, nmax):
    """Funcion de particion simetrizada de 2 bosones."""
    z1 = Z1(beta, omega, nmax)
    z1_2b = Z1(2.0 * beta, omega, nmax)
    return 0.5 * (z1 * z1 + z1_2b)


def Z_distinguible_2(beta, omega, nmax):
    """Z de 2 particulas distinguibles (sin simetrizar): Z1^2. Referencia."""
    z1 = Z1(beta, omega, nmax)
    return z1 * z1


def exchange_weight_fraction(beta, omega, nmax):
    """Peso relativo del sector de intercambio dentro de Z_B.

    = [Z1(2*beta)/2] / Z_B.  Es la fraccion de intercambio exacta de equilibrio.
    """
    z1_2b = Z1(2.0 * beta, omega, nmax)
    return 0.5 * z1_2b / Z_boson_2(beta, omega, nmax)


def energy_boson_2(beta, omega, nmax, h=1e-6):
    """Energia media de 2 bosones:  E = -d(ln Z_B)/d(beta)  (diferencia central)."""
    lnZ_p = np.log(Z_boson_2(beta + h, omega, nmax))
    lnZ_m = np.log(Z_boson_2(beta - h, omega, nmax))
    return float(-(lnZ_p - lnZ_m) / (2.0 * h))


def energy_1(beta, omega, nmax):
    """Energia media de 1 oscilador armonico (analitica exacta).

    E1 = (hbar*omega/2) * coth(beta*hbar*omega/2).
    """
    x = beta * HBAR * omega / 2.0
    return 0.5 * HBAR * omega / np.tanh(x)


# ---------------------------------------------------------------------------
# Formas cerradas exactas con omega configurable, hbar = kB = 1.
# Equivalen a las sumas truncadas de arriba, pero sin error de truncacion;
# se usan como referencia en los graficos y para reconstruir Z2 desde el MC.
# ---------------------------------------------------------------------------

def z1_closed(beta, omega=1.0):
    """Funcion de particion de 1 oscilador armonico en forma cerrada.

    z(beta) = sum_n exp(-beta*(n+1/2)) = 1 / (2*sinh(beta/2)).
    """
    return 1.0 / (2.0 * np.sinh(np.asarray(beta) * HBAR * omega / 2.0))


def R_exchange_exact(beta, omega=1.0):
    """Contribucion relativa del termino de intercambio (sector permutado).

    R = Z_intercambio / Z_identidad = z(2*beta) / z(beta)^2 = tanh(beta/2).
    Alta T (beta->0): R -> beta/2 -> 0 (simetrizacion despreciable).
    Baja T (beta->inf): R -> 1.
    """
    return np.tanh(np.asarray(beta) * HBAR * omega / 2.0)


def pex_exact(beta, omega=1.0):
    """Fraccion de equilibrio en el sector de intercambio (N=2).

    P_ex = z(2*beta) / (z(beta)^2 + z(2*beta)) = (1 - exp(-beta)) / 2.
    Alta T -> 0 (limite clasico de Boltzmann); baja T -> 1/2.
    """
    return -0.5 * np.expm1(-np.asarray(beta) * HBAR * omega)


def Z2_from_fraction(beta, f, omega=1.0):
    """Reconstruye Z2 desde la fraccion de intercambio muestreada f.

    Metodo de sector de referencia: el sector identidad integra exactamente a
    z(beta)^2 (enlaces de Mehler, sin error de Trotter), y f = Z_E/(Z_I+Z_E),
    de modo que Z_I/(Z_I+Z_E) = 1 - f.  Entonces

        Z2 = 0.5 * (Z_I + Z_E) = 0.5 * Z_I / (1 - f) = 0.5 * z(beta)^2 / (1 - f).

    El Monte Carlo solo aporta la razon f; la normalizacion absoluta viene de
    la forma cerrada exacta del sector identidad.
    """
    zI = z1_closed(beta, omega) ** 2
    return 0.5 * zI / (1.0 - f)
