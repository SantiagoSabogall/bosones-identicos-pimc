from itertools import permutations
from math import factorial
import numpy as np
import pytest
from cycles import cycle_type, cycle_types, multiplicity, swapped_images
from exact import class_probabilities, class_weights, partition, explicit_partition, energy, z1

EXPECTED = {
    2: {(1,1):1, (2,):1},
    3: {(1,1,1):1, (1,2):3, (3,):2},
    4: {(1,1,1,1):1, (1,1,2):6, (2,2):3, (1,3):8, (4,):6},
}

@pytest.mark.parametrize('N', [2,3,4])
def test_cycle_multiplicities_by_enumeration(N):
    observed = {kind:0 for kind in cycle_types(N)}
    for perm in permutations(range(N)):
        observed[cycle_type(perm)] += 1
    assert observed == EXPECTED[N]
    assert {kind:multiplicity(kind) for kind in cycle_types(N)} == observed
    assert sum(observed.values()) == factorial(N)

@pytest.mark.parametrize('N', [2,3,4])
@pytest.mark.parametrize('beta,omega', [(.1,1.), (.8,2.3), (4.,.7)])
def test_exact_partition_and_probabilities(N,beta,omega):
    assert np.isclose(partition(N,beta,omega), explicit_partition(N,beta,omega))
    probs=class_probabilities(N,beta,omega)
    assert set(probs)==set(EXPECTED[N])
    assert np.isclose(sum(probs.values()),1.)
    assert all(p>0 for p in probs.values())
    assert np.isclose(sum(class_weights(N,beta,omega).values())/factorial(N),
                      partition(N,beta,omega))

@pytest.mark.parametrize('N', [2,3,4])
def test_energy_derivative(N):
    beta=.7;omega=1.4;h=1e-5
    derivative=-(np.log(partition(N,beta+h,omega))-
                 np.log(partition(N,beta-h,omega)))/(2*h)
    assert np.isclose(energy(N,beta,omega),derivative,rtol=1e-8)


def test_transpositions_generate_all_permutations():
    for N in (3,4):
        start=tuple(range(N));found={start};frontier=[start]
        while frontier:
            current=frontier.pop()
            for a in range(N):
                for b in range(a+1,N):
                    nxt=swapped_images(current,a,b)
                    assert swapped_images(nxt,a,b)==current
                    if nxt not in found:
                        found.add(nxt);frontier.append(nxt)
        assert len(found)==factorial(N)


def test_n2_is_previous_control():
    beta=.8
    z=z1(beta)
    expected=z1(2*beta)/(z*z+z1(2*beta))
    assert np.isclose(class_probabilities(2,beta)[(2,)],expected)
