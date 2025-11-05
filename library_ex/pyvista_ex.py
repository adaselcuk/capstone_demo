import numpy as np
import pyvista as pv

# ---- Helical coordinates ----
theta = np.linspace(0, 6 * np.pi, 300)   # parameter along the helix
r = 0.05                                  # radius (m)
x = r * np.cos(theta)
y = r * np.sin(theta)
z = 0.01 * theta                          # helix pitch (m per radian)

points = np.column_stack((x, y, z))       # shape (n_points, 3)

# ---- Create a smooth spline representation of the line ----
# n_points controls the resolution of the generated spline (more points -> smoother)
n_spline_points = 300
spring = pv.Spline(points, n_points=n_spline_points)

# ---- Quick geometric checks (debugging) ----
# approximate center and total length of the polyline
center = spring.center
# compute approximate length along spline points
spline_coords = spring.points
segment_lengths = np.sqrt(np.sum(np.diff(spline_coords, axis=0) ** 2, axis=1))
approx_length = segment_lengths.sum()
print("Spline center (x,y,z):", center)
print("Approximate spline length [m]:", approx_length)

# ---- Visualize with PyVista ----
plotter = pv.Plotter(window_size=(800, 600))
plotter.add_mesh(spring, color='springgreen', line_width=5, name='helical_spring')
plotter.add_text("Helical Spring Geometry", font_size=12, position='upper_left')
plotter.show_grid()
print("Opening interactive PyVista window (close it to continue).")
# show() will open a window; using screenshot parameter also saves an image
screenshot_filename = "helical_spring.png"
plotter.show(screenshot=screenshot_filename)   
