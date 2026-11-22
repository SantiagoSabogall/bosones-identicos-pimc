import numpy as np
from diagnostics import autocorrelation, integrated_time


def test_iid_and_correlated_series():
    rng=np.random.default_rng(400)
    iid=rng.normal(size=20000)
    simple=integrated_time(iid)
    assert simple['resolved'] and 0.35 < simple['tau'] < 0.85
    ar=np.empty(20000)
    ar[0]=rng.normal()
    noise=rng.normal(size=len(ar)-1)
    for i in range(1,len(ar)):
        ar[i]=0.7*ar[i-1]+noise[i-1]
    measured=integrated_time(ar)
    # AR(1): tau=(1+phi)/(2(1-phi))=2.833...
    assert measured['resolved'] and 1.8 < measured['tau'] < 4.2
    assert measured['ess'] < simple['ess']
    assert np.isclose(autocorrelation(ar)[0],1.)


def test_constant_series_is_unresolved():
    result=integrated_time(np.ones(100))
    assert not result['resolved'] and result['ess']==0
