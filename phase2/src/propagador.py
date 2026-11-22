"""Propagador termico de 1 particula (densidad de Feynman-Kac) via formula de Mehler.

Para el oscilador armonico 1D:

    rho(x, x', tau) = sqrt( m*omega / (2*pi*hbar*sinh(omega*tau)) )
                      * exp( -m*omega / (2*hbar*sinh(omega*tau))
                             * ( (x^2 + x'^2)*cosh(omega*tau) - 2*x*x' ) )

Es el peso de cada enlace (link) de la trayectoria discretizada en tau = beta/P.
Soporta entradas escalares o arrays (vectorizado).
"""

import numpy as np

from params import HBAR, M


def rho(x, xp, tau, omega):
    """Densidad termica rho(x, x', tau) de la formula de Mehler."""
    s = np.sinh(omega * tau)
    c = np.cosh(omega * tau)
    pref = np.sqrt(M * omega / (2.0 * np.pi * HBAR * s))
    arg = -M * omega / (2.0 * HBAR * s) * ((x * x + xp * xp) * c - 2.0 * x * xp)
    return pref * np.exp(arg)


def log_rho(x, xp, tau, omega):
    """Logaritmo de rho (estable para productos de muchos enlaces)."""
    s = np.sinh(omega * tau)
    c = np.cosh(omega * tau)
    log_pref = 0.5 * np.log(M * omega / (2.0 * np.pi * HBAR * s))
    arg = -M * omega / (2.0 * HBAR * s) * ((x * x + xp * xp) * c - 2.0 * x * xp)
    return log_pref + arg
