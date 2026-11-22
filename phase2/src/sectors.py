"""Sectores de permutacion para 2 particulas identicas.

Para N=2 bosones hay 2 sectores:

  - IDENTIDAD  sigma = (0->0, 1->1): dos ciclos de longitud 1.
    Cada trayectoria es una closed path independiente de longitud beta.

  - INTERCAMBIO sigma = (0->1, 1->0): un ciclo de longitud 2.
    Las dos trayectorias se unen en una sola closed path de longitud 2*beta.

Condicion de frontera permutada:   x_i(beta) = x_{sigma(i)}(0).
Factor de simetrizacion del ensemble bosonico:   1 / N!  (= 1/2 para N=2).
"""

from math import factorial

IDENTITY = (0, 1)   # sigma(0)=0, sigma(1)=1
EXCHANGE = (1, 0)   # sigma(0)=1, sigma(1)=0

SECTORS = (IDENTITY, EXCHANGE)


def symmetrization_factor(N):
    """Factor de simetrizacion bosonico 1/N!."""
    return 1.0 / factorial(N)


def cycle_lengths(perm):
    """Longitudes de los ciclos de una permutacion dada como tupla.

    perm[i] = imagen de i.  Devuelve lista ordenada de longitudes de ciclo.
    IDENTITY -> [1, 1];  EXCHANGE -> [2].
    """
    n = len(perm)
    seen = [False] * n
    lengths = []
    for start in range(n):
        if seen[start]:
            continue
        length = 0
        i = start
        while not seen[i]:
            seen[i] = True
            i = perm[i]
            length += 1
        lengths.append(length)
    return sorted(lengths)


def num_cycles(perm):
    """Numero de ciclos de la permutacion."""
    return len(cycle_lengths(perm))


def is_exchange(perm):
    """True si el sector es el de intercambio (un ciclo de longitud 2)."""
    return cycle_lengths(perm) == [2]
