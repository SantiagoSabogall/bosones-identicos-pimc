"""Autocorrelación integrada y tamaño efectivo de muestra de series estacionarias."""
import numpy as np


def autocorrelation(x):
    x = np.asarray(x, dtype=float)
    if x.ndim != 1 or len(x) < 16:
        raise ValueError("La serie debe ser unidimensional y tener >=16 datos")
    centered = x - x.mean()
    variance = np.dot(centered, centered)
    if variance <= 0:
        return np.full(len(x), np.nan)
    size = 1 << (2 * len(x) - 1).bit_length()
    spectrum = np.fft.rfft(centered, n=size)
    acov = np.fft.irfft(spectrum * spectrum.conj(), n=size)[:len(x)]
    acov /= np.arange(len(x), 0, -1)
    return acov / acov[0]


def integrated_time(x, window_factor=5.0):
    """Ventana automática M >= c*tau(M); tau=1/2+sum_{t=1}^M rho(t)."""
    rho = autocorrelation(x)
    if not np.isfinite(rho[0]):
        return dict(tau=float("nan"), window=0, ess=0., error=0.,
                    resolved=False)
    n = len(rho)
    tau = 0.5
    window = 0
    for lag in range(1, n // 2):
        if rho[lag] <= 0 and lag >= window_factor:
            break
        tau = max(0.5, tau + rho[lag])
        window = lag
        if lag >= window_factor * tau:
            break
    ess = min(float(n), n / (2 * tau))
    error = np.sqrt(np.var(x, ddof=1) / ess)
    return dict(tau=float(tau), window=window, ess=float(ess),
                error=float(error), resolved=bool(n >= 20 * tau))
