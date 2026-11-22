"""Parametros fisicos y Monte Carlo de la fase 2.

Unidades naturales: hbar = m = kB = 1.
Sistema: N bosones ideales (sin interaccion) en un oscilador armonico 1D.
"""

from dataclasses import dataclass


# --- Constantes en unidades naturales ---
HBAR = 1.0   # constante de Planck reducida
M = 1.0      # masa de cada particula
KB = 1.0     # constante de Boltzmann


@dataclass
class Params:
    # --- Fisica ---
    N: int = 2          # numero de bosones (fase 2 = 2)
    beta: float = 1.0   # inverso de temperatura 1/(kB*T)
    omega: float = 1.0  # frecuencia del oscilador armonico (confinamiento)
    nmax: int = 200     # niveles de energia truncados para sumas exactas

    # --- Path Integral Monte Carlo ---
    P: int = 12            # numero de time-slices (beads) por trayectoria
    n_steps: int = 40_000  # pasos de muestreo tras el burn-in
    n_burn: int = 8_000    # pasos de calentamiento (burn-in) descartados
    delta: float = 0.6     # escala del desplazamiento colectivo de ciclos
    seed: int = 12345      # semilla del generador aleatorio

    def __post_init__(self):
        import math
        if self.N != 2:
            raise ValueError("Esta implementación admite únicamente N=2")
        for name in ("beta", "omega", "delta"):
            value = getattr(self, name)
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{name} debe ser positivo y finito")
        for name, minimum in (("P", 2), ("n_steps", 2), ("n_burn", 0), ("nmax", 0)):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
                raise ValueError(f"{name} debe ser entero >= {minimum}")

    @property
    def tau(self) -> float:
        """Paso imaginario de tiempo tau = beta / P (longitud de cada enlace)."""
        return self.beta / self.P


# Instancia por defecto reutilizable
DEFAULT = Params()
