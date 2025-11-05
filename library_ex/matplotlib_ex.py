import numpy as np
import matplotlib.pyplot as plt

# ---- Data preparation ----
time = np.linspace(0, 10, 500)        # time vector (s)
r1, r2 = 0.05, 0.1                    # radii in meters
gear_ratio = r1 / r2                  

# driver angular speed (simple linear ramp for demo)
omega1 = 10 * time                     # rad/s
omega2 = gear_ratio * omega1           # driven gear angular speed

# ---- Plot ----
plt.figure(figsize=(6, 4))
plt.plot(time, omega1, label='Gear 1 (driver)')
plt.plot(time, omega2, label='Gear 2 (driven)')
plt.xlabel('Time [s]')
plt.ylabel('Angular speed [rad/s]')
plt.title('Gear speed relationship (driver vs driven)')
plt.grid(True)
plt.legend()
plt.tight_layout()

# Save a copy to disk for later viewing and also show interactively
outname = "gear_speeds.png"
plt.savefig(outname)
print(f"\nPlot saved to: {outname}")
plt.show()
