import numpy as np

# Gear ratio setup
r1, r2 = 0.05, 0.1  # radii in meters
omega1 = np.linspace(0, 100, 500)  # gear 1 angular speed ramp (rad/s)
print(omega1)

# Ideal gear relationship: ω₂ r₁ = ω₁ r₂
omega2 = (r1 / r2) * omega1

# Torque scaling (assuming power conservation)
torque1 = 5.0  # Nm
torque2 = (r2 / r1) * torque1
