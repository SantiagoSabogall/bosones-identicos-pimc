"""Barrido reproducible con réplicas, muestras crudas y caché por configuración."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from params import Params
from sampler import PIMCSampler
from observables import Accumulator, sampling_diagnostics, block_mean_err
from analytic import z1_closed, pex_exact, R_exchange_exact, energy_boson_2
from figures_phase2 import make_all

ROOT = Path(__file__).resolve().parents[1]


def run_pipeline(steps=12000, burn=1000, replicas=3, omega=1.0, beads=8):
    if replicas < 2:
        raise ValueError('Se requieren al menos dos semillas independientes')
    config = dict(steps=steps, burn=burn, replicas=replicas, omega=omega,
                  P=beads, betas=np.geomspace(.1, 10, 10).tolist(), seed0=20261108)
    digest = hashlib.sha256(json.dumps(config, sort_keys=True).encode())
    for source in sorted((ROOT/'src').glob('*.py')):
        digest.update(source.read_bytes())
    fingerprint = digest.hexdigest()[:16]
    folder = ROOT/'data'/fingerprint
    folder.mkdir(parents=True, exist_ok=True)
    summary_path = folder/'summary.json'
    if summary_path.exists():
        summary = json.loads(summary_path.read_text())
    else:
        rows = []
        for j, beta in enumerate(config['betas']):
            means, errors, energies, virials, diagnostics = [], [], [], [], []
            for r in range(replicas):
                params = Params(beta=beta, omega=omega, P=beads, n_steps=steps,
                                n_burn=burn, seed=config['seed0']+100*j+r)
                sampler = PIMCSampler(params)
                acc = Accumulator()
                sampler.run(acc.record)
                raw = acc.as_dict()
                np.savez_compressed(folder/f'beta_{j}_seed_{r}.npz', **raw,
                                    params_json=json.dumps(vars(params)))
                d = sampling_diagnostics(raw['exchange_flags'])
                d['acceptance'] = sampler.acceptance_rates()
                d['burn_acceptance'] = sampler.burn_acceptance
                diagnostics.append(d)
                means.append(float(np.mean(raw['exchange_flags'])))
                errors.append(max(d['block_errors'].values(), default=float('nan')))
                energies.append(acc.energy_mean_err())
                virials.append(block_mean_err(raw['virial_samples']))
            f = float(np.mean(means))
            between = float(np.std(means, ddof=1)/np.sqrt(replicas))
            within = float(np.sqrt(np.sum(np.square(errors)))/replicas)
            error = max(between, within)
            consistent = all(abs(m-f) <= 4*np.sqrt(e*e+error*error)
                             for m,e in zip(means,errors))
            valid = all(d['valid'] for d in diagnostics) and consistent
            def combine(values):
                m,e = np.array(values).T
                return [float(m.mean()), float(max(np.std(m,ddof=1)/np.sqrt(replicas), np.linalg.norm(e)/replicas))]
            row = dict(beta=beta, f=f, error=error, exact=float(pex_exact(beta,omega)),
                       valid=bool(valid), seeds_consistent=bool(consistent),
                       replica_means=means, diagnostics=diagnostics,
                       energy=combine(energies), virial=combine(virials),
                       energy_exact=energy_boson_2(beta,omega,2000))
            rows.append(row)
            print(f'beta={beta:.3f}: f={f:.5f} +/- {error:.5f}, valid={valid}', flush=True)
        summary = dict(config=config, fingerprint=fingerprint, rows=rows)
        summary_path.write_text(json.dumps(summary, indent=2))
    rows = summary['rows']
    b = np.array([r['beta'] for r in rows]); f = np.array([r['f'] for r in rows]); e = np.array([r['error'] for r in rows])
    valid = np.array([r['valid'] for r in rows])
    # Los puntos no validados no se presentan como resultados físicos.
    f = np.where(valid, f, np.nan); e = np.where(valid, e, np.nan)
    z2 = .5*z1_closed(b,omega)**2/(1-f)
    data = dict(betas=b, f_mc=f, f_err=e, f_exact=pex_exact(b,omega),
                R_mc=f/(1-f), R_err=e/(1-f)**2, R_exact=R_exchange_exact(b,omega),
                Z2_mc=z2, Z2_err=z2*e/(1-f),
                Z2_exact=.5*(z1_closed(b,omega)**2+z1_closed(2*b,omega)),
                meta_omega=omega,meta_P=beads,meta_n_steps=steps,meta_n_burn=burn)
    np.savez_compressed(folder/'sweep.npz', **data)
    make_all(data, str(ROOT/'plots'/fingerprint))
    (ROOT/'LATEST.txt').write_text(str(folder.relative_to(ROOT))+'\n')
    return summary

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--steps',type=int,default=12000)
    parser.add_argument('--burn',type=int,default=1000)
    parser.add_argument('--replicas',type=int,default=3)
    parser.add_argument('--omega',type=float,default=1.)
    parser.add_argument('--beads',type=int,default=8)
    args=parser.parse_args()
    run_pipeline(args.steps,args.burn,args.replicas,args.omega,args.beads)
