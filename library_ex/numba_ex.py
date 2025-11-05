import time
import numpy as np
from numba import njit

def fatigue_damage_python(stress_history, A, m):
    damage = 0.0
    for s in stress_history:
        if s > 0:  # consider positive half-cycles
            N = A * (s ** -m)  # S-N curve
            damage += 1.0 / N
    return damage

@njit
def fatigue_damage_numba(stress_history, A, m):
    damage = 0.0
    for s in stress_history:
        if s > 0:  # consider positive half-cycles
            N = A * (s ** -m)  # S-N curve
            damage += 1.0 / N
    return damage

if __name__ == "__main__":
    # Simulated stress data
    stress_signal = np.abs(120 * np.sin(np.linspace(0, 200 * np.pi, 1_000_000)))
    A, m = 1e12, 3.0

    # --- Time pure Python version ---
    runs = 3
    t0 = time.perf_counter()
    res_py = None
    for _ in range(runs):
        res_py = fatigue_damage_python(stress_signal, A, m)
    t1 = time.perf_counter()
    py_time = (t1 - t0) / runs
    print(f"Python version result = {res_py:.6e}")
    print(f"Python version average time over {runs} runs: {py_time:.6f} s")

    # --- Time numba version (first call compiles) ---
    # Measure compile + first run
    t_compile_start = time.perf_counter()
    res_nb_first = fatigue_damage_numba(stress_signal, A, m)  # compile + run
    t_compile_end = time.perf_counter()
    compile_plus_run = t_compile_end - t_compile_start
    print(f"Numba first-call result (compile+run) = {res_nb_first:.6e}")
    print(f"Numba compile + first run time: {compile_plus_run:.6f} s")

    # Now measure subsequent runs (actual runtime without compile)
    runs_nb = 5
    t2 = time.perf_counter()
    res_nb = None
    for _ in range(runs_nb):
        res_nb = fatigue_damage_numba(stress_signal, A, m)
    t3 = time.perf_counter()
    nb_time = (t3 - t2) / runs_nb
    print(f"Numba warmed-up result = {res_nb:.6e}")
    print(f"Numba average time over {runs_nb} runs (after compile): {nb_time:.6f} s")

    # Summary
    print("\nSummary:")
    print(f"  Python avg time: {py_time:.6f} s")
    print(f"  Numba (after compile) avg time: {nb_time:.6f} s")
    print(f"  Numba compile + first run: {compile_plus_run:.6f} s")
    if nb_time > 0:
        print(f"  Speedup (Python / Numba warmed) = {py_time / nb_time:.2f}x")
