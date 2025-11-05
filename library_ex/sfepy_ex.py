import numpy as np

# ---- SfePy imports (imperative API) ----
from sfepy.discrete.fem import Mesh, FEDomain, Field
from sfepy.discrete import FieldVariable, Material, Integral, Equation, Equations, Problem
from sfepy.terms import Term
from sfepy.discrete.conditions import Conditions, EssentialBC
from sfepy.mechanics.matcoefs import stiffness_from_youngpoisson
from sfepy.solvers.ls import ScipyDirect
from sfepy.solvers.nls import Newton

n_turns = 3               # number of helix turns
n_points_per_turn = 50    # resolution along the helix
n_nodes = n_turns * n_points_per_turn + 1

radius = 0.05             # meters
pitch = 0.02              # axial distance per turn (meters)
t = np.linspace(0.0, 2.0 * np.pi * n_turns, n_nodes)

x_coords = radius * np.cos(t)
y_coords = radius * np.sin(t)
z_coords = (pitch / (2.0 * np.pi)) * t

coors_1d = z_coords[:, None]  # shape (n_nodes, 1)
print("Using 1D coordinates for mesh (shape):", coors_1d.shape)

# Connectivity: connect consecutive nodes with 2-node line elements
conn = np.column_stack([np.arange(0, n_nodes - 1, dtype=np.int32),
                        np.arange(1, n_nodes, dtype=np.int32)])
print("Created connectivity 'conn' with shape:", conn.shape, "  (2-node line elements)")

mat_ids = np.zeros(conn.shape[0], dtype=np.int32)   # all elements same material
descs = ['1_2']  # element type descriptor: 1D, 2 nodes # element dimension and number of nodes per element

# ---- 2) Build SfePy Mesh object from data ----
# Mesh.from_data(name, coors, ngroups, conns, mat_ids, descs)
mesh = Mesh.from_data('helical_spring', coors_1d, None, [conn], [mat_ids], descs)
print("Mesh.from_data -> mesh created. Mesh summary:")
print("  number of mesh vertices:", mesh.n_nod)
print("  mesh dimension (mesh.dim):", mesh.dim)

# ---- 3) Create FEDomain and regions ----
domain = FEDomain('domain', mesh)
bb = domain.get_mesh_bounding_box()
print("FEDomain created. Bounding box:\n", bb)

# region covering whole mesh (useful for integrals / fields)
omega = domain.create_region('Omega', 'all')
print("Region 'Omega' created (entire mesh).")

# create regions for the two ends (use for boundary conditions)
# using 1D mesh coordinates: the single coordinate is at index 0 and
# is referenced in region strings as 'x'
min_x, max_x = bb[:, 0]
eps = 1e-8 * (max_x - min_x + 1.0)  # small tolerance
left = domain.create_region('Left', 'vertices in x < %.10f' % (min_x + eps), 'vertex')
right = domain.create_region('Right', 'vertices in x > %.10f' % (max_x - eps), 'vertex')
print("Regions for BCs: 'Left' and 'Right' created (end vertices).")

# ---- 4) Field and Variables (displacement field, vector-valued) ----
# linear approximation of displacement (1 component in 1D)
# field defines basis functions, their approximation order, etc.
field = Field.from_args('displacement', np.float64, 'vector', omega, approx_order=1)
print("Field.from_args -> field created:", field.name, "approx_order =", field.approx_order)

# creating the variables associated with the field
u = FieldVariable('u', 'unknown', field)   # displacement (unknown)
v = FieldVariable('v', 'test', field, primary_var_name='u')  # virtual/test field
print("FieldVariable objects: 'u' (unknown) and 'v' (test) created.")

# ---- 5) Material: linear elasticity coefficients ----
E = 210e9   # Pa (steel) # Young's modulus
nu = 0.3 # Poisson's ratio
# Use 1D stiffness tensor (rod-like) since the mesh is 1D now.
# stiffness_from_youngpoisson accepts spatial dimension as first arg.
D = stiffness_from_youngpoisson(1, E, nu)
material = Material('m', D=D) # define material with name 'm' and property D
print("Material defined: Young's E = %.3e Pa, nu = %.3f. D shape:" % (E, nu), D.shape)

# ---- 6) Weak form (term) and equations ----
# integral defines numerical integration order
integral = Integral('i', order=3)
print("Integral created with order =", integral.order)

# linear elasticity term: dw_lin_elastic(m.D, v, u) integrated over Omega
term = Term.new('dw_lin_elastic(m.D, v, u)', integral, omega, m=material, v=v, u=u)
print("Term.new -> linear elasticity term created.")

# Equation wraps the term into an equation
eq = Equation('balance', term)
eqs = Equations([eq])
print("Equation and Equations assembled.")

# ---- 7) Boundary conditions (essential / Dirichlet) ----
# Fix left end (all displacement components = 0), prescribe small displacement at right end
fix_bc = EssentialBC('fix_left', left, {'u.all': 0.0})
prescribed_disp = 0.001  # 1 mm in all directions (tiny push) for demonstration
disp_bc = EssentialBC('prescribe_right', right, {'u.all': prescribed_disp})
print("EssentialBCs created: fix_left and prescribe_right (small displacement).")

# ---- 8) Solver setup and problem construction ----
ls = ScipyDirect({})                       # linear solver
nls = Newton({}, lin_solver=ls)            # nonlinear solver wrapper
print("Linear and nonlinear solvers prepared (ScipyDirect, Newton).")

# High level problem definition
pb = Problem('linear_elasticity_spring', equations=eqs)

pb.set_solver(nls)  # this tells Problem which top-level solver to use.

# apply BCs (stationary problem -> time_update called once to install BCs)
pb.time_update(ebcs=Conditions([fix_bc, disp_bc]))
print("Problem.time_update -> boundary conditions applied.")

# ---- 9) Solve the problem ----
print("Starting solver: pb.solve() ...")
solution = pb.solve()
print("pb.solve() finished. Type of 'solution':", type(solution))

# Many SfePy examples return a FieldVariable-like object that can create output dicts.
if hasattr(solution, 'create_output_dict'):
    out = solution.create_output_dict()
    vtk_name = 'helical_spring_result.vtk'
    pb.save_state(vtk_name, out=out)
    print("Solution saved to VTK file:", vtk_name)
else:
    # In some setups pb.solve() may return a vector/array (legacy interfaces).
    # Print a compact summary and try to save nothing instead of crashing.
    try:
        sol_len = len(solution)
    except Exception:
        sol_len = None
    print("Solver returned object without 'create_output_dict'. length/size:", sol_len)

# ---- 10) Quick inspections / teaching prints ----
# For teaching: show displacements at ends (if available)
try:
    # get nodal displacements if solution is field-like
    if hasattr(solution, 'get_state'):
        full_state = solution.get_state()
        print("Full solution state vector length:", full_state.shape)
    elif hasattr(solution, 'create_output_dict'):
        # If we got output dict, try to extract first field array for a quick peek
        fields_out = out.get('vertex_data', {}) or out.get('point_data', {})
        print("Output dict contains keys:", list(out.keys()))
    else:
        print("Solution object type (no quick state extraction).")
except Exception as e:
    print("Could not extract/print solution state (non-fatal):", e)