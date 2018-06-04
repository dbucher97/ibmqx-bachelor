from main import *
from fourier_transform import iqft
from phase_estimation import phase_estimation, handle_counts, print_handled_counts, setup_phase_counts_plot, plot_phase_counts
import matplotlib.pyplot as plt
import numpy as np
n = 3
m = 4

qp, qc, qrs, crs = setup(n, additional_registers={"qr": {"a": m}}, login=True)

qr, ar = qrs
cr = crs


# qc.x(qr[1])


def cmodexp7(qc, ctl, qr):
    for i in range(n):
        qc.cx(ctl, qr[i])
    qc.cswap(ctl, qr[1], qr[2])
    qc.cswap(ctl, qr[2], qr[3])
    qc.cswap(ctl, qr[0], qr[3])

def cmodexp72(qc, ctl, qr):
    qc.cswap(ctl, qr[0], qr[2])
    qc.cswap(ctl, qr[1], qr[3])


def x7mod15(qc, ctl, qr):
    qc.cx(ctl, qr[1])
    qc.cx(ctl, qr[2])

def x72mod15(qc, ctl, qr):
    qc.cx(qr[3], qr[1])
    qc.ccx(ctl, qr[1], qr[3])
    qc.cx(qr[3], qr[1])
    qc.cx(qr[0], qr[2])
    qc.ccx(ctl, qr[2], qr[0])
    qc.cx(qr[0], qr[2])

def modexp15(qc, ctl, qr, n):
    if n == 1:
        x7mod15(qc, ctl, qr)
    elif n == 2:
        x72mod15(qc, ctl, qr)

# from iterative_phase_estimation import iterative_phase_estimation

#iterative_phase_estimation(7, 4, modexp15, backend="ibmqx5")
#cmodexp7(qc, qr[0], ar)
#cmodexp72(qc, qr[1], ar)

qc.x(ar[0])

phase_estimation(qc, qr, ar, modexp15)

# qc.x(qr[0])

qc.optimize_gates()
qc.barrier(qr)
qc.measure(qr, cr)

# register()
# qobj = qp.compile([get_name()], backend="ibmqx5")
# qasm = qp.get_compiled_qasm(qobj, get_name())
# qp.load_qasm_text(qasm, name="qasm")
# plot_circuit(qp.get_circuit("test"))
# qc.measure(ar, acr)
#
result = execute(qp, meta="shor_n=%d"%n, backend="ibmqx5")
# print(result.get_counts(get_name()))


#for 3 skip [0]
skip = []
if n == 3:
    skip = [0]
hc = handle_counts(result.get_counts(get_name()), n, skip=skip)
print_handled_counts(hc)

res_sim = execute(qp)
hcs = handle_counts(res_sim.get_counts(get_name()), n)
print_handled_counts(hcs)

ax = setup_phase_counts_plot(plt, n, top=0.3, r=0.1)
plot_phase_counts(ax, hcs, width=0.12, offset=0.06, color=colors["sim"], label="Simulation")
plot_phase_counts(ax, hc, width=0.12, offset=-0.06, color=colors["exp"], label="ibmqx5")
if n == 3:
    ax.plot(np.linspace(0, 1*2*np.pi, 1000), 0.5+np.ones(1000)*0.097, linestyle="dashed", color="red")
# ax.plot(np.linspace(0, 1*2*np.pi, 1000), 0.5+np.ones(1000)*1/8, linestyle="dotted", color="red", alpha=0.6)
ax.legend(loc="upper right", bbox_to_anchor=(1.1, 0))
ax.set_title("Shor's algorithm N=15, m=%d\n"%n)
ax.set_xlabel(r"$\varphi$")

plt.savefig("plots/shor_%d.pdf"%n, bbox_inches="tight")
