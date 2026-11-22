"""Corrida de control de 2 bosones: PIMC vs valor exacto (analytic.py).

Carga params, corre el sampler, acumula energia y estadistica de ciclos,
compara contra el calculo exacto e imprime una tabla. Guarda las muestras en .npz.
"""

import os

import numpy as np

import analytic
from params import Params
from sampler import PIMCSampler
from observables import Accumulator, sampling_diagnostics, block_mean_err


def run(params=None, save_path=None, verbose=True):
    if params is None:
        params = Params()

    sampler = PIMCSampler(params)
    acc = Accumulator()
    sampler.run(record_fn=acc.record)

    # --- muestreado ---
    E_mc, E_err = acc.energy_mean_err()
    f_mc, f_err = acc.exchange_fraction()
    hist = acc.cycle_histogram()
    diagnostics = sampling_diagnostics(acc.exchange_flags)
    virial = block_mean_err(acc.virial_samples)
    rates = sampler.acceptance_rates()

    # --- exacto ---
    E_exact = analytic.energy_boson_2(params.beta, params.omega, params.nmax)
    f_exact = analytic.exchange_weight_fraction(params.beta, params.omega, params.nmax)

    if verbose:
        print("=" * 60)
        print(f"PIMC control  N={params.N}  beta={params.beta}  omega={params.omega}"
              f"  P={params.P}")
        print(f"pasos={params.n_steps}  burn={params.n_burn}  seed={params.seed}")
        print("-" * 60)
        print(f"{'observable':<22}{'muestreado':<22}{'exacto':<14}")
        print(f"{'energia E':<22}{f'{E_mc:.4f} +/- {E_err:.4f}':<22}{E_exact:<14.4f}")
        print(f"{'frac. intercambio':<22}{f'{f_mc:.4f} +/- {f_err:.4f}':<22}{f_exact:<14.4f}")
        print("-" * 60)
        print(f"ciclos: 1-ciclos={hist['cycle_len_1']}  2-ciclos={hist['cycle_len_2']}")
        print(f"aceptacion: bead={rates['bead']:.3f}  perm={rates['perm']:.3f}")
        dE = abs(E_mc - E_exact) / E_err if E_err > 0 else float("nan")
        df = abs(f_mc - f_exact) / f_err if f_err > 0 else float("nan")
        print(f"desviacion energia: {dE:.2f} sigma   intercambio: {df:.2f} sigma")
        print("diagnosticos:", diagnostics)
        print("energia virial:", virial)
        print("=" * 60)

    result = {
        "diagnostics": diagnostics, "virial": virial,
        "E_mc": E_mc, "E_err": E_err, "E_exact": E_exact,
        "f_mc": f_mc, "f_err": f_err, "f_exact": f_exact,
        "cycle_hist": hist, "accept": rates,
    }

    if save_path is not None:
        d = acc.as_dict()
        np.savez(
            save_path,
            E_samples=d["E_samples"],
            exchange_flags=d["exchange_flags"],
            cycle1_counts=d["cycle1_counts"],
            cycle2_counts=d["cycle2_counts"],
            beta=params.beta, omega=params.omega, P=params.P,
            E_exact=E_exact, f_exact=f_exact,
        )
        if verbose:
            print(f"muestras guardadas en {save_path}")

    return result


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    run(save_path=os.path.join(here, "samples_phase2.npz"))
