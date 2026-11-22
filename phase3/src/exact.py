"""Control canónico exacto para 2-4 bosones ideales, hbar=m=kB=1."""
from math import factorial
import numpy as np
from cycles import cycle_types, multiplicity


def z1(beta, omega=1.0):
    if beta <= 0 or omega <= 0:
        raise ValueError('beta y omega deben ser positivos')
    a = beta * omega
    return float(np.exp(-a / 2) / -np.expm1(-a))


def e1(beta, omega=1.0):
    """Energía media de una partícula a inversa de temperatura beta."""
    a = beta * omega
    return float(omega * (0.5 + 1 / np.expm1(a)))


def class_numerator(kind, beta, omega=1.0):
    """Peso integrado de una clase antes de dividir por N!."""
    result = float(multiplicity(kind))
    for length in kind:
        result *= z1(length * beta, omega)
    return result


def class_weights(N, beta, omega=1.0):
    return {kind: class_numerator(kind, beta, omega)
            for kind in cycle_types(N)}


def partition(N, beta, omega=1.0):
    if N not in (2, 3, 4):
        raise ValueError('Control implementado para N=2,3,4')
    return sum(class_weights(N, beta, omega).values()) / factorial(N)


def class_probabilities(N, beta, omega=1.0):
    weights = class_weights(N, beta, omega)
    total = sum(weights.values())
    return {kind: value / total for kind, value in weights.items()}


def energy(N, beta, omega=1.0):
    """-d log(Z_N)/d beta, evaluado por clases sin diferencias finitas."""
    probs = class_probabilities(N, beta, omega)
    return sum(prob * sum(length * e1(length * beta, omega)
                          for length in kind)
               for kind, prob in probs.items())


def explicit_partition(N, beta, omega=1.0):
    z = lambda length: z1(length * beta, omega)
    if N == 2:
        return (z(1)**2 + z(2)) / 2
    if N == 3:
        return (z(1)**3 + 3*z(1)*z(2) + 2*z(3)) / 6
    if N == 4:
        return (z(1)**4 + 6*z(1)**2*z(2) + 3*z(2)**2
                + 8*z(1)*z(3) + 6*z(4)) / 24
    raise ValueError('N debe ser 2,3,4')
