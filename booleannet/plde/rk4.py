"""
Fourth-order Runge-Kutta stepper.

Signature matches the old matplotlib.mlab.rk4 helper: derivs(state, t).
"""
import numpy as np


def rk4(derivs, y0, t):
    "Integrate derivs(y, t) and return states at each time in t."
    y0 = np.atleast_1d(np.asarray(y0, dtype=float))
    t = np.asarray(t, dtype=float)
    yout = np.zeros((len(t), y0.size), dtype=float)
    yout[0] = y0

    for i in range(len(t) - 1):
        thist = t[i]
        dt = t[i + 1] - t[i]
        dt2 = dt / 2.0
        y = yout[i]
        k1 = np.atleast_1d(np.asarray(derivs(y, thist), dtype=float))
        k2 = np.atleast_1d(np.asarray(derivs(y + dt2 * k1, thist + dt2), dtype=float))
        k3 = np.atleast_1d(np.asarray(derivs(y + dt2 * k2, thist + dt2), dtype=float))
        k4 = np.atleast_1d(np.asarray(derivs(y + dt * k3, thist + dt), dtype=float))
        yout[i + 1] = y + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
    return yout
