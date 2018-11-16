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
    return x, np.array(perc)/100

n=1
a = 0
if n == 2:
    a = 0.25

ef = lambda d, n: 1/2**(2*n)*np.sin(np.pi*d*2**n)**2/np.sin(np.pi*d)**2
d = np.linspace(0.0, 0.5-a, 100)
y = ef(d, n)

fig, ax = plt.subplots(figsize=(4.5, 3))
ax.grid(linestyle="dashed")


ax.plot(d+a, y, linestyle="dashed", label="Theory", color="red")

ax.plot(*run_phase(a, 0.5, 10, n=n), label="Simulation", marker="o", markerfacecolor='none',
        color=colors["sim"])
ax.plot(*run_phase(a, 0.5, 10, n=n, backend="ibmqx5"), label="ibmqx5", marker="v",
        markerfacecolor='none', color=colors["exp"])

ax.set_xlabel(r"$\varphi$")
ax.set_ylabel("success rate")

ax.set_title("PEA performance $n = %d$"%n)

ax.legend()
# plt.plot(*run_phase(0.25, 0.5, 20, a=3))
plt.savefig("plots/pe_performance_ibmqx5_n=%d.pdf"%n, bbox_inches="tight", transparent=True)
