import numpy as np
from scipy.integrate import solve_bvp

# Beam parameters
E, I, L, q = 210e9, 8e-6, 2.0, 1000.0

def beam_eq(x, y):
    # supplies the system of first-order ODEs for the beam deflection problem
    # inputs are x (1-D array) and y (2-D array with shape (4, len(x)))

    # each row is one of the variables, evaluated at all x points:
    # y[0] = deflection, y[1] = slope, y[2] = curvature = moment/EI, y[3] = shear/(EI)
    return np.vstack([y[1], y[2], y[3], np.ones_like(x) * q / (E * I)])

def bc(ya, yb):
    # ya = y at left boundary, yb = y at right boundary
    # Simply supported: deflection = 0 at both ends, moment = 0 at both ends
    return np.array([ya[0], ya[2], yb[0], yb[2]])

x = np.linspace(0, L, 50)
print("np.linspace -> x: shape =", x.shape, "first 5 values =", x[:5])

y_init = np.zeros((4, x.size))
print("np.zeros -> y_init: shape =", y_init.shape)

# call beam_eq once on the initial guess to inspect library-call outputs (np.vstack, np.ones_like)
initial_rhs = beam_eq(x, y_init)
print("beam_eq(x, y_init) -> shape =", initial_rhs.shape, "first column =", initial_rhs[:, 0])

sol = solve_bvp(beam_eq, bc, x, y_init)
print("solve_bvp -> success =", getattr(sol, "success", None), "message =", getattr(sol, "message", None))

y_deflect = sol.y[0]
print("solution -> y_deflect: shape =", y_deflect.shape, "first 5 values =", y_deflect[:5])
