"""PIMC canónico de 2-4 bosones ideales con fronteras permutadas.

La distribución objetivo es proporcional al producto de N*P propagadores
exactos de Mehler. Las propuestas de transposición son simétricas.
"""
import numpy as np
from time import perf_counter
from cycles import cycles, cycle_type, swapped_images
from params import HBAR, M
from propagador import log_rho


class PIMCSampler:
    def __init__(self, params):
        self.p = params
        self.rng = np.random.default_rng(params.seed)
        self.x = self.rng.normal(0, 0.3, size=(params.N, params.P))
        self.perm = tuple(range(params.N))
        self._chol_cache = {}
        self._reset_counters()

    def _reset_counters(self):
        self.counters = dict(local=0, shifts=0, shift_accepted=0,
                             global_draws=0, perm_attempts=0, perm_accepted=0)

    def _cycle_indices(self):
        for cycle in cycles(self.perm):
            yield tuple((i, k) for i in cycle for k in range(self.p.P))

    def _bead_move(self):
        i = int(self.rng.integers(self.p.N))
        k = int(self.rng.integers(self.p.P))
        if k:
            left = self.x[i, k - 1]
        else:
            left = self.x[self.perm.index(i), -1]
        if k < self.p.P - 1:
            right = self.x[i, k + 1]
        else:
            right = self.x[self.perm[i], 0]
        a = self.p.omega * self.p.tau
        mean = (left + right) / (2 * np.cosh(a))
        variance = HBAR * np.tanh(a) / (2 * M * self.p.omega)
        self.x[i, k] = self.rng.normal(mean, np.sqrt(variance))
        self.counters['local'] += 1

    def _cycle_shift(self):
        for indices in self._cycle_indices():
            old = np.array([self.x[index] for index in indices])
            proposed = old + self.rng.normal(scale=self.p.delta)
            before = np.sum(log_rho(old, np.roll(old, -1), self.p.tau, self.p.omega))
            after = np.sum(log_rho(proposed, np.roll(proposed, -1), self.p.tau, self.p.omega))
            self.counters['shifts'] += 1
            if np.log(self.rng.random()) < min(0., after - before):
                for index, value in zip(indices, proposed):
                    self.x[index] = value
                self.counters['shift_accepted'] += 1

    def _cycle_heatbath(self):
        """Extrae cada ciclo de la gaussiana exacta condicionada a sigma."""
        for indices in self._cycle_indices():
            length = len(indices)
            key = (length, self.p.tau, self.p.omega)
            if key not in self._chol_cache:
                a = M * self.p.omega / (HBAR * np.sinh(self.p.omega * self.p.tau))
                c = np.cosh(self.p.omega * self.p.tau)
                q = np.zeros((length, length))
                for j in range(length):
                    k = (j + 1) % length
                    q[j, j] += a * c
                    q[k, k] += a * c
                    q[j, k] -= a
                    q[k, j] -= a
                self._chol_cache[key] = np.linalg.cholesky(np.linalg.inv(q))
            values = self._chol_cache[key] @ self.rng.standard_normal(length)
            for index, value in zip(indices, values):
                self.x[index] = value
            self.counters['global_draws'] += 1

    def closure_log_weight(self, perm):
        return sum(log_rho(self.x[i, -1], self.x[perm[i], 0],
                           self.p.tau, self.p.omega)
                   for i in range(self.p.N))

    def log_weight(self, perm=None):
        """Peso completo, útil para auditar la razón de aceptación."""
        if perm is None:
            perm = self.perm
        total = sum(np.sum(log_rho(self.x[i, :-1], self.x[i, 1:],
                                   self.p.tau, self.p.omega))
                    for i in range(self.p.N))
        return float(total + self.closure_log_weight(perm))

    def _permutation_move(self):
        pair = self.rng.choice(self.p.N, size=2, replace=False)
        proposed = swapped_images(self.perm, int(pair[0]), int(pair[1]))
        delta = self.closure_log_weight(proposed) - self.closure_log_weight(self.perm)
        self.counters['perm_attempts'] += 1
        if np.log(self.rng.random()) < min(0., delta):
            self.perm = proposed
            self.counters['perm_accepted'] += 1

    def sweep(self):
        for _ in range(self.p.N * self.p.P):
            self._bead_move()
        self._cycle_shift()
        if self.p.global_heatbath:
            self._cycle_heatbath()
        self._permutation_move()

    def run(self, record_fn=None):
        start=perf_counter()
        for _ in range(self.p.n_burn):
            self.sweep()
        burn_seconds=perf_counter()-start
        self.burn_counters = self.counters.copy()
        self._reset_counters()
        start=perf_counter()
        for _ in range(self.p.n_steps):
            self.sweep()
            if record_fn is not None:
                record_fn(self)
        self.timing=dict(burn_seconds=burn_seconds,
                         measurement_seconds=perf_counter()-start)

    @property
    def current_cycles(self):
        return cycles(self.perm)

    @property
    def current_cycle_type(self):
        return cycle_type(self.perm)

    def acceptance_rates(self):
        c = self.counters
        return dict(shift=c['shift_accepted'] / max(1, c['shifts']),
                    permutation=c['perm_accepted'] / max(1, c['perm_attempts']))
