import numpy as np
import pytest
from occupations import partition as occupation_partition, energy as occupation_energy, finite_level_sum
from exact import partition as cycle_partition, energy as cycle_energy


@pytest.mark.parametrize("N", (2, 3, 4))
@pytest.mark.parametrize("beta,omega", ((0.1, 1.), (0.5, 1.), (1.2, 2.3), (5., 0.7), (10., 1.)))
def test_independent_occupation_control(N, beta, omega):
    assert np.isclose(occupation_partition(N, beta, omega),
                      cycle_partition(N, beta, omega), rtol=2e-13)
    assert np.isclose(occupation_energy(N, beta, omega),
                      cycle_energy(N, beta, omega), rtol=2e-13)


@pytest.mark.parametrize("N", (2, 3, 4))
def test_direct_fock_sum(N):
    # Beta=1 makes a finite cutoff inexpensive and quantitatively converged.
    reference = occupation_partition(N, 1.)
    low = finite_level_sum(N, 1., max_level=12)
    high = finite_level_sum(N, 1., max_level=28)
    assert low <= high <= reference * (1 + 1e-12)
    assert np.isclose(high, reference, rtol=3e-12)
