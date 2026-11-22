import numpy as np
import pytest
from dataclasses import replace
from params import Params
from sampler import PIMCSampler
from observables import Accumulator,block_mean_error,replica_summary,thermodynamic_energy
from exact import class_probabilities,energy

@pytest.mark.parametrize('N,perm,counts,particle',[
 (3,(1,2,0),[0,0,1],[0,0,1]),
 (4,(1,0,3,2),[0,2,0,0],[0,1,0,0]),
 (4,(1,0,2,3),[2,1,0,0],[.5,.5,0,0])])
def test_cycle_definitions(N,perm,counts,particle):
    s=PIMCSampler(Params(N=N,P=2));s.perm=perm
    a=Accumulator(N);a.record(s);d=a.arrays()
    np.testing.assert_array_equal(d['n_cycles'][0],counts)
    np.testing.assert_allclose(d['particle_fractions'][0],particle)
    assert d['class_flags'].sum()==1


def test_thermodynamic_energy_finite_difference():
    s=PIMCSampler(Params(N=4,P=3,beta=1.2,omega=1.4));s.perm=(1,0,3,2)
    h=1e-5;old=s.p
    s.p=replace(old,beta=old.beta+h);plus=s.log_weight()
    s.p=replace(old,beta=old.beta-h);minus=s.log_weight();s.p=old
    assert np.isclose(thermodynamic_energy(s),-(plus-minus)/(2*h),rtol=1e-8)


def test_block_and_replica_summary():
    rng=np.random.default_rng(2);arr=[]
    for _ in range(3):
        ids=rng.integers(0,3,4096)
        arr.append(dict(class_ids=ids,class_flags=(ids[:,None]==np.arange(3)),
                        n_cycles=rng.random((4096,4)),
                        particle_fractions=rng.random((4096,4)),
                        energy=rng.random(4096),virial=rng.random(4096)))
    out=replica_summary(arr)
    assert out['class_flags']['mean'].shape==(3,)
    assert np.isclose(out['class_flags']['mean'].sum(),1)
    assert out['diagnostics']['valid']
    with pytest.raises(ValueError):block_mean_error(np.ones(10),16)

@pytest.mark.parametrize('N',[3,4])
def test_sampled_energy_and_classes(N):
    p=Params(N=N,P=3,beta=1.,n_steps=4000,n_burn=400,seed=830+N)
    s=PIMCSampler(p);a=Accumulator(N);s.run(a.record);d=a.arrays()
    exact=class_probabilities(N,p.beta)
    for i,kind in enumerate(a.classes):
        assert abs(d['class_flags'][:,i].mean()-exact[kind])<.06
    assert abs(d['virial'].mean()-energy(N,p.beta))<.18
    assert abs(d['energy'].mean()-energy(N,p.beta))<.18
    assert np.allclose(d['particle_fractions'].sum(axis=1),1)
