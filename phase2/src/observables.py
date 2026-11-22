"""Estimadores de energia y estadistica de ciclos a partir de las trayectorias PIMC.

Energia (ESTIMADOR TERMODINAMICO para enlaces exactos de Mehler):
  El peso de una configuracion es W = producto sobre enlaces de rho(x, x', tau),
  con tau = beta/P. La energia es el estimador termodinamico

      E = - d(ln W)/d(beta)  =  -(1/P) * sum_enlaces  d(ln rho)/d(tau).

  Para el propagador de Mehler, con s = sinh(omega*tau), c = cosh(omega*tau),
  A = x^2 + x'^2, B = 2*x*x':

      d(ln rho)/d(tau) = -0.5*omega*c/s + (m*omega^2 / (2*hbar)) * (A - B*c) / s^2.

  Con enlaces exactos de Mehler, el estimador virial armónico también es
  válido en equilibrio a P finito. Ambos estimadores tienen varianzas distintas.

Estadistica de ciclos:
  - fraccion de muestras en el sector de intercambio,
  - histograma de longitudes de ciclo (cuantos 1-ciclos vs 2-ciclos).
"""

import numpy as np

from params import M, HBAR
from sectors import is_exchange, cycle_lengths


def _link_dln_dtau(xa, xb, tau, omega):
    """d(ln rho)/d(tau) para un enlace (xa -> xb) del propagador de Mehler."""
    s = np.sinh(omega * tau)
    c = np.cosh(omega * tau)
    A = xa * xa + xb * xb
    B = 2.0 * xa * xb
    return -0.5 * omega * c / s + (M * omega * omega / (2.0 * HBAR)) * (A - B * c) / (s * s)


def thermodynamic_energy(sampler):
    """E = -(1/P) * sum_enlaces d(ln rho)/d(tau) sobre la topologia actual."""
    x = sampler.x
    P = sampler.P
    tau = sampler.tau
    omega = sampler.omega
    perm = sampler.perm
    total = 0.0
    for i in (0, 1):
        # enlaces internos k -> k+1
        for k in range(P - 1):
            total += _link_dln_dtau(x[i, k], x[i, k + 1], tau, omega)
        # enlace de cierre: ultimo bead de i -> primer bead de perm[i]
        total += _link_dln_dtau(x[i, P - 1], x[perm[i], 0], tau, omega)
    return float(-total / P)


class Accumulator:
    """Acumula observables muestra a muestra."""

    def __init__(self):
        self.virial_samples = []
        self.E_samples = []        # energia por muestra
        self.exchange_flags = []   # 1 si sector intercambio, 0 si identidad
        self.cycle1_counts = []    # numero de 1-ciclos en la muestra
        self.cycle2_counts = []    # numero de 2-ciclos en la muestra

    def record(self, sampler):
        # Estimador termodinamico de energia (total, 2 particulas).
        E = thermodynamic_energy(sampler)
        self.E_samples.append(E)
        self.virial_samples.append(float(M * sampler.omega**2 * np.sum(sampler.x**2) / sampler.P))

        self.exchange_flags.append(1 if is_exchange(sampler.perm) else 0)
        lengths = cycle_lengths(sampler.perm)
        self.cycle1_counts.append(lengths.count(1))
        self.cycle2_counts.append(lengths.count(2))

    # --- resumenes ---
    def energy_mean_err(self, n_blocks=20):
        """Energia media y error por block averaging."""
        return block_mean_err(np.asarray(self.E_samples), n_blocks)

    def exchange_fraction(self, n_blocks=20):
        """Fraccion de intercambio y su error."""
        return block_mean_err(np.asarray(self.exchange_flags, float), n_blocks)

    def cycle_histogram(self):
        """Conteo total de 1-ciclos y 2-ciclos sobre todas las muestras."""
        return {
            "cycle_len_1": int(np.sum(self.cycle1_counts)),
            "cycle_len_2": int(np.sum(self.cycle2_counts)),
        }

    def as_dict(self):
        return {
            "virial_samples": np.asarray(self.virial_samples),
            "E_samples": np.asarray(self.E_samples),
            "exchange_flags": np.asarray(self.exchange_flags),
            "cycle1_counts": np.asarray(self.cycle1_counts),
            "cycle2_counts": np.asarray(self.cycle2_counts),
        }


def block_mean_err(samples, n_blocks=20):
    """Media y error estandar via promedios de bloques (reduce autocorrelacion)."""
    samples = np.asarray(samples, float)
    n = len(samples)
    if n == 0:
        return float("nan"), float("nan")
    n_blocks = min(n_blocks, n)
    block_size = n // n_blocks
    trimmed = samples[: block_size * n_blocks]
    blocks = trimmed.reshape(n_blocks, block_size).mean(axis=1)
    mean = float(blocks.mean())
    err = float(blocks.std(ddof=1) / np.sqrt(n_blocks)) if n_blocks > 1 else float("nan")
    return mean, err


def sampling_diagnostics(flags):
    """Diagnóstico conservador; los umbrales son criterios operativos explícitos."""
    x = np.asarray(flags, float)
    changes = int(np.count_nonzero(np.diff(x)))
    sizes = [b for b in (16, 64, 256, 1024) if len(x) // b >= 8]
    errors = {}
    for size in sizes:
        blocks = x[:len(x)//size*size].reshape(-1, size).mean(axis=1)
        errors[str(size)] = float(blocks.std(ddof=1) / np.sqrt(len(blocks)))
    positive = [v for v in errors.values() if v > 0]
    stable = len(positive) >= 2 and 0.5 <= positive[-1]/positive[-2] <= 2.0
    valid = changes >= 100 and 0 < x.mean() < 1 and stable
    return {"valid": bool(valid), "sector_changes": changes,
            "block_errors": errors, "block_stable": bool(stable),
            "reason": "ok" if valid else "muestreo insuficiente o error de bloques inestable"}
