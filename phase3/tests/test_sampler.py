from collections import Counter
from itertools import permutations
import numpy as np
import pytest
from params import Params
from sampler import PIMCSampler
from cycles import swapped_images
from exact import class_probabilities

@pytest.mark.parametrize('bad', [{'N':5},{'P':1},{'beta':0},{'omega':-2},
                                 {'n_steps':0},{'delta':float('nan')}])
def test_reject_bad_parameters(bad):
    with pytest.raises(ValueError): Params(**bad)

@pytest.mark.parametrize('N', [2,3,4])
def test_boundary_weight_ratio(N):
    s=PIMCSampler(Params(N=N,P=3,beta=.7,omega=1.3))
    s.x=np.arange(N*3).reshape(N,3)*.1
    for perm in permutations(range(N)):
        for a in range(N):
            for b in range(a+1,N):
                nxt=swapped_images(perm,a,b)
                closure=s.closure_log_weight(nxt)-s.closure_log_weight(perm)
                full=s.log_weight(nxt)-s.log_weight(perm)
                assert np.isclose(closure,full,atol=1e-12)

@pytest.mark.parametrize('N,perm,length', [(3,(1,2,0),3),(4,(1,2,3,0),4),
                                          (4,(1,0,3,2),2)])
def test_global_heatbath_variance(N,perm,length):
    s=PIMCSampler(Params(N=N,P=2,beta=1.2,omega=1.4))
    s.perm=perm; vals=[]
    for _ in range(5000):
        s._cycle_heatbath();vals.append(s.x[0,0])
    exact=1/(2*s.p.omega*np.tanh(length*s.p.beta*s.p.omega/2))
    assert abs(np.var(vals)-exact)<.07*exact

@pytest.mark.parametrize('N', [3,4])
def test_class_frequencies_match_exact(N):
    p=Params(N=N,P=3,beta=1.,omega=1.,n_burn=800,n_steps=9000,seed=478+N)
    s=PIMCSampler(p);counts=Counter()
    s.run(lambda sampler:counts.update([sampler.current_cycle_type]))
    probs=class_probabilities(N,p.beta,p.omega)
    assert set(counts)==set(probs)
    for kind,expected in probs.items():
        observed=counts[kind]/p.n_steps
        assert abs(observed-expected)<.035, (N,kind,observed,expected)
    assert s.counters['perm_accepted']>500
    assert s.counters['global_draws']>=p.n_steps
    assert s.burn_counters['perm_accepted']>0
