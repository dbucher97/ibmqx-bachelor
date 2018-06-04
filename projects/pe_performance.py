from main import *
# from simulation_errors import gen_noise_params
from phase_estimation import dummy_phase_estimation
import numpy as np
import matplotlib.pyplot as plt

def run_phase(f, t, N, n=2, a=0, backend="local_qiskit_simulator"):
    perc = []
    x = np.linspace(f, t, N)
    for p in x:
        pc = dummy_phase_estimation(p, n=n, ancilla=a, backend=backend)
        g = 0
        for k, v in pc.items():
            if v["phase_angle"] == f:
                g = v["percentage"]
        perc += [g]
    return x-f, np.array(perc)/100

ef = lambda d, n: 1/2**(2*n)*np.sin(np.pi*d*2**n)**2/np.sin(np.pi*d)**2
d = np.linspace(0, 0.25, 100)
y = ef(d, 2)

fig, ax = plt.subplots(figsize=(4.5, 3))
ax.grid(linestyle="dashed")

# ax.plot(d+0.25, y, linestyle="dashed", label="Theory")

# ax.plot(*run_phase(0.25, 0.5, 40), label="Sim. a=0", color=colors["exp"])
ax.plot(*run_phase(0.25, 0.5, 100, a=3), label=r"Sim. a=3, $\epsilon=0.1$", color=colors["exp"])
ax.plot(*run_phase(0.25, 0.5, 100, a=6), label=r"Sim. a=6, $\epsilon=0.01$", color=colors["sim"])

ax.set_xlabel(r"$\delta$")
ax.set_ylabel("success rate")

ax.set_ylim(ymin=0.8)

ax.set_title("PEA performance ancillary qubits")

ax.legend()
# plt.plot(*run_phase(0.25, 0.5, 20, a=3))
plt.savefig("plots/pe_performance_ancilla_p.pdf", bbox_inches="tight")
