"""Path Integral Monte Carlo (PIMC) para 2 bosones en un oscilador 1D.

Estado
------
  x : array (2, P)  posiciones de las 2 trayectorias en P time-slices (beads).
      x[i, k] es el bead k de la particula i.
  perm : tupla de sectors (IDENTITY o EXCHANGE), el sector de permutacion actual.

Topologia de enlaces
--------------------
  Dentro de una trayectoria i, los beads se enlazan en cadena:
      x[i,0] - x[i,1] - ... - x[i,P-1]
  El ultimo bead de i se enlaza con el PRIMER bead de la particula perm[i]:
      x[i, P-1] - x[perm[i], 0]
  IDENTITY  -> dos lazos cerrados independientes (ciclos de longitud 1 cada uno).
  EXCHANGE  -> un solo lazo cerrado de longitud 2*P (ciclo de longitud 2).

Cada enlace pesa con el propagador de 1 particula rho(x, x', tau), tau = beta/P.
Movimientos:
  (a) heat-bath local, desplazamiento colectivo y heat-bath gaussiano de ciclos.
  (b) permutation move: proponer cambiar de sector reconectando los extremos,
      con aceptacion Metropolis sobre la razon de pesos de los enlaces de cierre.
El muestreador DEBE visitar ambos sectores.
"""

import numpy as np

from propagador import log_rho
from sectors import IDENTITY, EXCHANGE, is_exchange, cycle_lengths


class PIMCSampler:
    def __init__(self, params):
        self.p = params
        self.rng = np.random.default_rng(params.seed)
        self.P = params.P
        self.tau = params.tau
        self.omega = params.omega
        # Ancho natural de un bead = sqrt(hbar * sinh(omega*tau) / (m*omega)).
        # El paso single-bead se escala con este ancho para mantener la
        # aceptacion ~0.5 a cualquier tau (clave a alta T, donde tau es pequeno).
        from params import HBAR, M
        bead_width = np.sqrt(HBAR * np.sinh(self.omega * self.tau) / (M * self.omega))
        self.step = params.delta * bead_width
        # Inicializar trayectorias cerca del origen con la escala correcta
        self.x = self.rng.normal(0.0, max(bead_width, 0.3), size=(2, self.P))
        self.perm = IDENTITY
        # Contadores de aceptacion
        self.acc_bead = 0
        self.try_bead = 0
        self.acc_shift = self.try_shift = 0
        self.global_draws = 0
        self.acc_perm = 0
        self.try_perm = 0

    def _cycle_indices(self):
        seen = set()
        for start in range(2):
            if start in seen:
                continue
            particles = []
            i = start
            while i not in seen:
                seen.add(i)
                particles.append(i)
                i = self.perm[i]
            yield [(i, k) for i in particles for k in range(self.P)]

    def _global_heatbath(self):
        """Remuestrea cada ciclo completo de su gaussiana exacta.

        No usa probabilidades analíticas de sectores: la permutación sigue
        cambiando mediante Metropolis. Elimina los modos lentos locales.
        """
        from params import HBAR, M
        for indices in self._cycle_indices():
            length = len(indices)
            key = (length, self.tau, self.omega)
            if not hasattr(self, "_chol_cache"):
                self._chol_cache = {}
            if key not in self._chol_cache:
                a = M * self.omega / (HBAR * np.sinh(self.omega * self.tau))
                q = np.zeros((length, length))
                for j in range(length):
                    k = (j + 1) % length
                    q[j, j] += a * np.cosh(self.omega * self.tau)
                    q[k, k] += a * np.cosh(self.omega * self.tau)
                    q[j, k] -= a
                    q[k, j] -= a
                # Cache factor of covariance for fast independent cycle draws.
                self._chol_cache[key] = np.linalg.cholesky(np.linalg.inv(q))
            values = self._chol_cache[key] @ self.rng.standard_normal(length)
            for index, value in zip(indices, values):
                self.x[index] = value
        self.global_draws += 1

    def _cycle_shift(self):
        """Desplazamiento colectivo simétrico; razón exacta de enlaces."""
        for indices in self._cycle_indices():
            old = np.array([self.x[index] for index in indices])
            new = old + self.rng.normal(scale=self.p.delta)
            before = np.sum(log_rho(old, np.roll(old, -1), self.tau, self.omega))
            after = np.sum(log_rho(new, np.roll(new, -1), self.tau, self.omega))
            self.try_shift += 1
            if np.log(self.rng.random()) < min(0.0, after - before):
                for index, value in zip(indices, new):
                    self.x[index] = value
                self.acc_shift += 1

    # --- enlaces ---
    def _closure_partner(self, i):
        """Particula a la que se enlaza el ultimo bead de i (segun perm)."""
        return self.perm[i]

    def _bead_log_links(self, i, k, xval, perm):
        """log-peso de los 2 enlaces que tocan el bead (i,k) si valiera xval.

        Enlace 'izquierdo' k-1 -> k  y enlace 'derecho' k -> k+1.
        En los extremos (k=0 o k=P-1) el enlace cruza a la particula socia via perm.
        """
        P = self.P
        x = self.x
        # vecino izquierdo
        if k == 0:
            # viene del ultimo bead de la particula j tal que perm[j]=i
            j = perm.index(i)
            left = x[j, P - 1]
        else:
            left = x[i, k - 1]
        # vecino derecho
        if k == P - 1:
            right = x[perm[i], 0]
        else:
            right = x[i, k + 1]
        ll = log_rho(left, xval, self.tau, self.omega)
        lr = log_rho(xval, right, self.tau, self.omega)
        return ll + lr

    def _bead_neighbors(self, i, k, perm):
        """Vecinos izquierdo (L) y derecho (R) del bead (i,k) segun la topologia."""
        P = self.P
        x = self.x
        if k == 0:
            j = perm.index(i)
            L = x[j, P - 1]
        else:
            L = x[i, k - 1]
        if k == P - 1:
            R = x[perm[i], 0]
        else:
            R = x[i, k + 1]
        return L, R

    def _bead_move(self):
        """Heat-bath EXACTO de un bead: su condicional es Gaussiana (aceptacion 1).

        Dos enlaces de Mehler tocan el bead y; con L,R vecinos, la densidad en y es
            p(y) ~ exp(-a*y^2 + b*y),  a = m*omega*c/(hbar*s),  b = (m*omega/(hbar*s))*(L+R).
        => y ~ Normal(mean = (L+R)/(2c),  var = hbar*s/(2*m*omega*c)).
        Aceptación uno no garantiza mezcla rápida de modos colectivos.
        """
        from params import HBAR, M
        i = self.rng.integers(2)
        k = self.rng.integers(self.P)
        L, R = self._bead_neighbors(i, k, self.perm)
        s = np.sinh(self.omega * self.tau)
        c = np.cosh(self.omega * self.tau)
        mean = (L + R) / (2.0 * c)
        var = HBAR * s / (2.0 * M * self.omega * c)
        self.x[i, k] = mean + np.sqrt(var) * self.rng.standard_normal()
        self.try_bead += 1
        self.acc_bead += 1  # heat-bath: siempre aceptado

    def _closure_log_weight(self, perm):
        """log-peso de los enlaces de CIERRE para un sector dado.

        Son los enlaces x[i, P-1] -> x[perm[i], 0] para i=0,1.
        Los enlaces internos no dependen del sector, se cancelan en la razon.
        """
        P = self.P
        x = self.x
        total = 0.0
        for i in (0, 1):
            total += log_rho(x[i, P - 1], x[perm[i], 0], self.tau, self.omega)
        return total

    def _perm_move(self):
        """Propone saltar al otro sector (identidad <-> intercambio)."""
        cur = self.perm
        prop = EXCHANGE if cur == IDENTITY else IDENTITY
        log_cur = self._closure_log_weight(cur)
        log_prop = self._closure_log_weight(prop)
        self.try_perm += 1
        if np.log(self.rng.random()) < (log_prop - log_cur):
            self.perm = prop
            self.acc_perm += 1

    def sweep(self):
        """Actualizaciones locales y colectivas, seguidas de reconexión de cierres."""
        for _ in range(2 * self.P):
            self._bead_move()
        self._cycle_shift()
        self._global_heatbath()
        self._perm_move()

    def run(self, record_fn=None):
        """Burn-in y muestreo. record_fn(sampler) se llama por paso muestreado."""
        for _ in range(self.p.n_burn):
            self.sweep()
        self.burn_acceptance = self.acceptance_rates()
        self.acc_bead = self.try_bead = self.acc_perm = self.try_perm = 0
        self.acc_shift = self.try_shift = self.global_draws = 0
        for _ in range(self.p.n_steps):
            self.sweep()
            if record_fn is not None:
                record_fn(self)

    # --- lecturas de estado ---
    @property
    def in_exchange(self):
        return is_exchange(self.perm)

    @property
    def current_cycles(self):
        return cycle_lengths(self.perm)

    def acceptance_rates(self):
        rb = self.acc_bead / self.try_bead if self.try_bead else 0.0
        rp = self.acc_perm / self.try_perm if self.try_perm else 0.0
        return {"bead": rb, "perm": rp, "cycle_shift": self.acc_shift / max(1, self.try_shift), "sector_changes": self.acc_perm}
