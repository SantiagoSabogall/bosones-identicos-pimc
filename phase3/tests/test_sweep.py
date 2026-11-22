import json
from pathlib import Path
import numpy as np
from sweep_phase3 import exact_particle_probabilities,run
from plot_phase3 import make_plots


def test_exact_particle_probabilities():
    for N in (3,4):
        for beta in (.5,1.,4.):
            p=exact_particle_probabilities(N,beta,1.)
            assert len(p)==N and np.isclose(sum(p),1)
            assert all(0<=v<=1 for v in p)


def test_sweep_and_figures(tmp_path,monkeypatch):
    import sweep_phase3
    monkeypatch.setattr(sweep_phase3,'ROOT',tmp_path)
    (tmp_path/'src').mkdir()
    data,folder=run(N_values=(3,),betas=[1.],P=2,steps=500,burn=50,replicas=2)
    row=data['results'][0]
    assert np.isclose(sum(row['class_mc']),1)
    assert np.isclose(sum(row['particle_mc']),1)
    assert np.isclose(sum(row['particle_exact']),1)
    assert row['z_mc'] > 0 and row['z_error'] > 0
    assert row['z_exact'] > 0
    assert row['measurement_seconds'] > 0
    assert json.loads((folder/'summary.json').read_text())['run_id']==data['run_id']
    with np.load(folder/'N3_beta0_replica0.npz',allow_pickle=False) as z:
        assert z['n_cycles'].shape==(500,3)
        assert z['particle_fractions'].shape==(500,3)
        assert z['class_flags'].shape[0]==500
    paths=make_plots(data,tmp_path/'plots')
    assert len(paths)==5
    assert all(Path(p).stat().st_size>0 for p in paths)
