"""Parámetros de N=2, 3 y 4 bosones ideales en un oscilador armónico 1D."""
from dataclasses import dataclass
from math import isfinite

HBAR = 1.0
M = 1.0
KB = 1.0

@dataclass(frozen=True)
class Params:
    N: int = 3
    beta: float = 1.0
    omega: float = 1.0
    P: int = 4
    n_burn: int = 1000
    n_steps: int = 10000
    delta: float = 0.6
    seed: int = 12345
    global_heatbath: bool = True

    def __post_init__(self):
        if type(self.N) is not int or self.N not in (2, 3, 4):
            raise ValueError('N debe ser 2, 3 o 4')
        for name in ('P', 'n_burn', 'n_steps', 'seed'):
            value = getattr(self, name)
            minimum = 2 if name == 'P' else 0 if name in ('n_burn', 'seed') else 1
            if type(value) is not int or value < minimum:
                raise ValueError(f'{name} debe ser entero >= {minimum}')
        for name in ('beta', 'omega', 'delta'):
            value = getattr(self, name)
            if not isfinite(value) or value <= 0:
                raise ValueError(f'{name} debe ser positivo y finito')
        if type(self.global_heatbath) is not bool:
            raise ValueError('global_heatbath debe ser booleano')

    @property
    def tau(self):
        return self.beta / self.P
