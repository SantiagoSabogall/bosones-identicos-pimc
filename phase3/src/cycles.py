"""Permutaciones, ciclos y clases de conjugación para N pequeño."""
from collections import Counter
from math import factorial


def validate_perm(perm):
    perm = tuple(perm)
    if tuple(sorted(perm)) != tuple(range(len(perm))):
        raise ValueError('La permutación debe contener cada índice exactamente una vez')
    return perm


def cycles(perm):
    perm = validate_perm(perm)
    seen = set()
    result = []
    for start in range(len(perm)):
        if start in seen:
            continue
        current = start
        cycle = []
        while current not in seen:
            seen.add(current)
            cycle.append(current)
            current = perm[current]
        result.append(tuple(cycle))
    return tuple(result)


def cycle_type(perm):
    return tuple(sorted(len(c) for c in cycles(perm)))


def cycle_types(N):
    """Particiones no decrecientes de N, expresadas como longitudes de ciclos."""
    if type(N) is not int or N < 1:
        raise ValueError('N debe ser entero positivo')
    def visit(remaining, low, prefix):
        if remaining == 0:
            yield prefix
        for length in range(low, remaining + 1):
            yield from visit(remaining - length, length, prefix + (length,))
    return tuple(visit(N, 1, ()))


def multiplicity(kind):
    """N! / producto_l(l^n_l n_l!), para una partición de N."""
    if not kind or tuple(sorted(kind)) != tuple(kind) or min(kind) < 1:
        raise ValueError('Se esperaba una partición no decreciente')
    counts = Counter(kind)
    denominator = 1
    for length, count in counts.items():
        denominator *= length ** count * factorial(count)
    return factorial(sum(kind)) // denominator


def swapped_images(perm, a, b):
    """Transposición propuesta: intercambia dos imágenes de sigma."""
    perm = list(validate_perm(perm))
    if not (0 <= a < len(perm) and 0 <= b < len(perm)) or a == b:
        raise ValueError('Se requieren dos índices diferentes')
    perm[a], perm[b] = perm[b], perm[a]
    return tuple(perm)
