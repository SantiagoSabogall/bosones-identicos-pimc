"""Estadísticas de clases, tamaños de ciclo y energía para N=2..4."""
import numpy as np
from cycles import cycle_types
from params import M, HBAR
from diagnostics import integrated_time


def link_dlogrho_dtau(x, xp, tau, omega):
    s=np.sinh(omega*tau);c=np.cosh(omega*tau)
    return -omega*c/(2*s)+(M*omega**2/(2*HBAR))*((x*x+xp*xp)-2*x*xp*c)/s**2


def thermodynamic_energy(sampler):
    x=sampler.x;p=sampler.p;total=0.
    for i in range(p.N):
        total+=np.sum(link_dlogrho_dtau(x[i,:-1],x[i,1:],p.tau,p.omega))
        total+=link_dlogrho_dtau(x[i,-1],x[sampler.perm[i],0],p.tau,p.omega)
    return float(-total/p.P)


class Accumulator:
    def __init__(self,N):
        self.N=N;self.classes=cycle_types(N)
        self.class_to_col={kind:i for i,kind in enumerate(self.classes)}
        self.ids=[];self.counts=[];self.particles=[];self.energies=[];self.virials=[]
        self.permutation_accepted=[]
        self._previous_accepted=0

    def record(self,sampler):
        if sampler.p.N!=self.N:raise ValueError('N diferente')
        kind=sampler.current_cycle_type
        n=np.bincount(kind,minlength=self.N+1)[1:]
        self.ids.append(self.class_to_col[kind])
        self.counts.append(n)
        self.particles.append(np.arange(1,self.N+1)*n/self.N)
        self.energies.append(thermodynamic_energy(sampler))
        self.virials.append(float(M*sampler.p.omega**2*np.sum(sampler.x**2)/sampler.p.P))
        accepted=sampler.counters['perm_accepted']
        self.permutation_accepted.append(accepted-self._previous_accepted)
        self._previous_accepted=accepted

    def arrays(self):
        ids=np.asarray(self.ids,dtype=int)
        return dict(class_ids=ids,
                    class_flags=(ids[:,None]==np.arange(len(self.classes))).astype(np.uint8),
                    n_cycles=np.asarray(self.counts,dtype=int).reshape(-1,self.N),
                    particle_fractions=np.asarray(self.particles,dtype=float).reshape(-1,self.N),
                    energy=np.asarray(self.energies),virial=np.asarray(self.virials),
                    permutation_accepted=np.asarray(self.permutation_accepted,dtype=np.uint8))


def block_mean_error(values,size):
    x=np.asarray(values,dtype=float)
    if x.ndim==1:x=x[:,None]
    n=len(x)//size
    if n<8:raise ValueError('Se necesitan ocho bloques')
    blocks=x[:n*size].reshape(n,size,x.shape[1]).mean(axis=1)
    return blocks.mean(axis=0),blocks.std(axis=0,ddof=1)/np.sqrt(n)


def replica_summary(arrays,minimum_changes=30):
    if len(arrays)<2:raise ValueError('Se requieren dos réplicas o más')
    out={}
    for key in ('class_flags','n_cycles','particle_fractions','energy','virial'):
        means=[];errors=[];taus=[];esses=[];resolved=[]
        for raw in arrays:
            x=np.asarray(raw[key],dtype=float)
            if x.ndim==1:x=x[:,None]
            sizes=[size for size in (16,64,256,1024) if len(x)//size>=8]
            if not sizes:raise ValueError('Muy pocas muestras para bloques')
            means.append(x.mean(axis=0))
            ac=[integrated_time(x[:,j]) for j in range(x.shape[1])]
            taus.append([d['tau'] for d in ac])
            esses.append([d['ess'] for d in ac])
            resolved.append([d['resolved'] for d in ac])
            block_error=np.max([block_mean_error(x,size)[1] for size in sizes],axis=0)
            errors.append(np.maximum(block_error,[d['error'] for d in ac]))
        means=np.asarray(means);errors=np.asarray(errors)
        between=means.std(axis=0,ddof=1)/np.sqrt(len(means))
        within=np.sqrt(np.sum(errors**2,axis=0))/len(means)
        out[key]={'mean':means.mean(axis=0),'error':np.maximum(between,within),
                  'replica_means':means,'replica_errors':errors,
                  'tau_int':np.asarray(taus),'n_eff':np.asarray(esses),
                  'acf_resolved':np.asarray(resolved)}
    changes=[int(np.count_nonzero(np.diff(a['class_ids']))) for a in arrays]
    visited=[int(len(np.unique(a['class_ids']))) for a in arrays]
    out['diagnostics']={'class_changes':changes,'classes_visited':visited,
                        'valid':all(c>=minimum_changes for c in changes),
                        'class_ess':out['class_flags']['n_eff'].tolist(),
                        'class_tau_int':out['class_flags']['tau_int'].tolist(),
                        'energy_ess':out['energy']['n_eff'].tolist(),
                        'energy_tau_int':out['energy']['tau_int'].tolist(),
                        'acf_resolved':out['class_flags']['acf_resolved'].tolist()}
    return out
