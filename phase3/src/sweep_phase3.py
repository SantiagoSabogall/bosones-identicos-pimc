"""Barrido de ciclos N=3,4 con varias semillas y datos reproducibles."""
import argparse
import hashlib
import json
from math import factorial
from dataclasses import asdict
from pathlib import Path
import numpy as np
from params import Params
from sampler import PIMCSampler
from cycles import cycle_types
from exact import class_probabilities,energy,z1
from occupations import partition as occupation_partition, energy as occupation_energy
from observables import Accumulator,replica_summary

ROOT=Path(__file__).resolve().parents[1]


def exact_particle_probabilities(N,beta,omega):
    classes=class_probabilities(N,beta,omega)
    return [sum(prob*length*kind.count(length)/N
                for kind,prob in classes.items()) for length in range(1,N+1)]


def jsonable(value):
    if isinstance(value,np.ndarray):return jsonable(value.tolist())
    if isinstance(value,np.generic):return jsonable(value.item())
    if isinstance(value,float) and not np.isfinite(value):return None
    if isinstance(value,dict):return {str(k):jsonable(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [jsonable(v) for v in value]
    return value


def run(N_values=(3,4),betas=None,P=4,steps=4000,burn=500,replicas=3,omega=1.,seed=20261109,
        global_heatbath=True):
    if replicas<2:raise ValueError('Se necesitan al menos dos semillas')
    if betas is None:betas=np.geomspace(.5,5.,7)
    betas=[float(b) for b in betas]
    config=dict(N_values=list(N_values),betas=betas,P=P,steps=steps,burn=burn,
                replicas=replicas,omega=omega,seed=seed,
                global_heatbath=global_heatbath)
    # La huella evita reutilizar datos generados con otros parámetros o código.
    digest=hashlib.sha256(json.dumps(config,sort_keys=True).encode())
    for path in sorted((ROOT/'src').glob('*.py')):digest.update(path.read_bytes())
    run_id=digest.hexdigest()[:16]
    folder=ROOT/'data'/run_id;folder.mkdir(parents=True,exist_ok=True)
    summary_file=folder/'summary.json'
    if summary_file.exists():
        return json.loads(summary_file.read_text()),folder
    results=[]
    for N in N_values:
        kinds=cycle_types(N)
        for j,beta in enumerate(betas):
            raws=[];rates=[];timings=[]
            for r in range(replicas):
                p=Params(N=N,beta=beta,omega=omega,P=P,n_burn=burn,
                         n_steps=steps,seed=seed+10000*N+100*j+r,
                         global_heatbath=global_heatbath)
                sampler=PIMCSampler(p);acc=Accumulator(N)
                sampler.run(acc.record);raw=acc.arrays();raws.append(raw)
                rates.append(sampler.acceptance_rates())
                timings.append(sampler.timing)
                np.savez_compressed(folder/f'N{N}_beta{j}_replica{r}.npz',**raw,
                                    params_json=json.dumps(asdict(p)),
                                    classes_json=json.dumps(kinds))
            summary=replica_summary(raws)
            class_exact=class_probabilities(N,beta,omega)
            observed=summary['class_flags']['mean']
            errors=summary['class_flags']['error']
            # Calidad interna y contraste exacto son diagnósticos diferentes.
            counts=summary['class_flags']['replica_means']*steps
            class_resolved=(np.all(counts>=20,axis=0) &
                            np.all(summary['class_flags']['n_eff']>=100,axis=0) &
                            np.all(summary['class_flags']['acf_resolved'],axis=0) &
                            (errors>0))
            deviations=np.abs(observed-np.array([class_exact[k] for k in kinds]))
            consistent=bool(np.all(deviations[class_resolved]<=4*errors[class_resolved]))
            valid=bool(summary['diagnostics']['valid'] and
                       np.all(summary['energy']['n_eff']>=100) and
                       np.all(summary['energy']['acf_resolved']))
            p_id=float(observed[0])
            z_mc=float(z1(beta,omega)**N/(factorial(N)*p_id)) if p_id>0 else None
            z_error=float(z_mc*errors[0]/p_id) if z_mc is not None else None
            seconds=sum(t['measurement_seconds'] for t in timings)
            energy_ess=float(np.sum(summary['energy']['n_eff']))
            row=dict(N=N,beta=beta,T=1/beta,classes=[list(k) for k in kinds],
                     class_mc=observed,class_error=errors,
                     class_exact=[class_exact[k] for k in kinds],
                     class_resolved=class_resolved,
                     exact_within_4sigma=consistent,
                     z_mc=z_mc,z_error=z_error,
                     z_exact=occupation_partition(N,beta,omega),
                     n_cycles_mc=summary['n_cycles']['mean'],
                     n_cycles_error=summary['n_cycles']['error'],
                     particle_mc=summary['particle_fractions']['mean'],
                     particle_error=summary['particle_fractions']['error'],
                     particle_exact=exact_particle_probabilities(N,beta,omega),
                     energy_mc=summary['energy']['mean'][0],
                     energy_error=summary['energy']['error'][0],
                     virial_mc=summary['virial']['mean'][0],
                     virial_error=summary['virial']['error'][0],
                     energy_exact=energy(N,beta,omega),
                     energy_occupation=occupation_energy(N,beta,omega),
                     diagnostics=summary['diagnostics'],acceptance=rates,
                     timing=timings,measurement_seconds=seconds,
                     energy_ess_per_second=energy_ess/seconds,
                     valid=valid)
            results.append(jsonable(row))
            print(f'N={N} beta={beta:.3f}: valid={valid}, '
                  f'cambios={summary["diagnostics"]["class_changes"]}',flush=True)
    result=dict(config=config,run_id=run_id,results=results)
    temporary=summary_file.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False))
    temporary.replace(summary_file)
    (ROOT/'LATEST.txt').write_text('data/'+run_id+'\n')
    return result,folder

if __name__=='__main__':
    cli=argparse.ArgumentParser()
    cli.add_argument('--steps',type=int,default=4000)
    cli.add_argument('--burn',type=int,default=500)
    cli.add_argument('--replicas',type=int,default=3)
    cli.add_argument('--P',type=int,default=4)
    cli.add_argument('--omega',type=float,default=1.)
    cli.add_argument('--betas',type=float,nargs='+')
    cli.add_argument('--N',type=int,nargs='+',choices=(3,4),default=[3,4])
    cli.add_argument('--no-global-heatbath',action='store_true')
    args=cli.parse_args()
    data,folder=run(tuple(args.N),args.betas,args.P,args.steps,args.burn,args.replicas,args.omega,
                    global_heatbath=not args.no_global_heatbath)
    print('Datos:',folder)
    from plot_phase3 import make_plots
    print('Figuras:',make_plots(data,ROOT/'plots'/data['run_id']))
