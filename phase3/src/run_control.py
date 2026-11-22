"""Control rápido de clases de ciclos: python src/run_control.py --N 3."""
import argparse
from collections import Counter
from exact import class_probabilities, partition, energy
from params import Params
from sampler import PIMCSampler


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--N',type=int,choices=(2,3,4),default=3)
    parser.add_argument('--beta',type=float,default=1.0)
    parser.add_argument('--omega',type=float,default=1.0)
    parser.add_argument('--P',type=int,default=4)
    parser.add_argument('--burn',type=int,default=1000)
    parser.add_argument('--steps',type=int,default=10000)
    parser.add_argument('--seed',type=int,default=12345)
    a=parser.parse_args()
    p=Params(N=a.N,beta=a.beta,omega=a.omega,P=a.P,n_burn=a.burn,
             n_steps=a.steps,seed=a.seed)
    s=PIMCSampler(p);counts=Counter()
    s.run(lambda state:counts.update([state.current_cycle_type]))
    print(f'N={p.N}, beta={p.beta}, omega={p.omega}, P={p.P}')
    print(f'Z_N exacta={partition(p.N,p.beta,p.omega):.8g}, '
          f'E_N exacta={energy(p.N,p.beta,p.omega):.8g}')
    print('clase\tMC\texacta')
    for kind,prob in class_probabilities(p.N,p.beta,p.omega).items():
        print(f'{kind}\t{counts[kind]/p.n_steps:.5f}\t{prob:.5f}')
    print('aceptación',s.acceptance_rates())
    print('cambios de permutación aceptados',s.counters['perm_accepted'])

if __name__=='__main__':main()
