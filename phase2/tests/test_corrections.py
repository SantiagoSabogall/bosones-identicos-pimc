import numpy as np
import pytest
from params import Params
from sampler import PIMCSampler
from sectors import IDENTITY, EXCHANGE
from observables import sampling_diagnostics
from analytic import pex_exact, exchange_weight_fraction, Z2_from_fraction, Z_boson_2

@pytest.mark.parametrize('kw',[{'N':3},{'P':1},{'beta':0},{'omega':-1},{'n_steps':0}])
def test_reject_invalid(kw):
    with pytest.raises(ValueError): Params(**kw)

def test_frequency():
    for omega in (.4,2.3):
        for b in (.2,2):
            f=pex_exact(b,omega)
            assert np.isclose(f,exchange_weight_fraction(b,omega,2000))
            assert np.isclose(Z2_from_fraction(b,f,omega), Z_boson_2(b,omega,2000))

def test_trapped_chain_invalid():
    d=sampling_diagnostics(np.zeros(10000))
    assert not d['valid'] and d['sector_changes']==0

@pytest.mark.parametrize('sector',[IDENTITY,EXCHANGE])
def test_global_heatbath_covariance(sector):
    s=PIMCSampler(Params(P=2,beta=1.7,omega=1.3))
    s.perm=sector
    # Exact single-time variance, beta for singleton, 2 beta for exchanged cycle.
    b=s.p.beta*(2 if sector==EXCHANGE else 1)
    expected=1/(2*s.omega*np.tanh(b*s.omega/2))
    values=[]
    for _ in range(12000):
        s._global_heatbath(); values.append(s.x[0,0])
    assert abs(np.var(values)-expected)<.05*expected

def test_high_temperature_moves_between_sectors():
    s=PIMCSampler(Params(P=4,beta=.1,n_steps=6000,n_burn=300,seed=19))
    flags=[]
    s.run(lambda s:flags.append(s.in_exchange))
    assert abs(np.mean(flags)-pex_exact(.1))<.015
    assert s.acceptance_rates()['sector_changes']>100

def test_nonunit_frequency_energy_and_sectors():
    from observables import Accumulator
    from analytic import energy_boson_2
    s=PIMCSampler(Params(P=3,beta=.8,omega=2.3,n_steps=5000,n_burn=300,seed=47))
    a=Accumulator(); s.run(a.record)
    assert abs(np.mean(a.exchange_flags)-pex_exact(.8,2.3))<.035
    assert abs(np.mean(a.virial_samples)-energy_boson_2(.8,2.3,400))<.12
