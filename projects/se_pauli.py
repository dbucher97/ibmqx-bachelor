from simulation_errors import gen_noise_params, coupling_map, basis_gates, run_pe_circuit,create_binary_phase_str
from phase_estimation import *
import matplotlib.pyplot as plt
import numpy as np
from main import colors


def pauli_plot_run(n, l, pzmax=0.08, pxmax=0, phase=None):
    if not phase:
        phase=2**-n


    axes = setup_phase_counts_plot(plt, n, subplots=(1, l), top=1, step=0.2)

    for pz, px, ax in zip(np.linspace(0, pzmax, l), np.linspace(0, pxmax, l), axes):
        counts = run_pe_circuit(phase, n, pauli_x=px, pauli_z=pz)
        hc = handle_counts(counts, n)
        t = list(hc.values())[0].get("percentage")/100
        set_top(ax, t*1.1)
        tr = 5
        x = np.ceil(-np.log10(t/tr))
        s = round((t/tr)*10**x)/10**x
        set_ticks(ax, s, t)
        ax.plot(np.linspace(0, np.pi*2, 1000), np.ones(1000)*1/2**n+0.5, color="red",
                linestyle="dashed")
        plot_phase_counts(ax, hc, color=colors["exp"], width=0.1)

    plt.savefig("plots/simulations/se_pauli_n=%d_l=%d_pzmax=%.2f_pxmax=%.2f_phase=%.3f.pdf"%
                (n ,l , pzmax, pxmax, phase), bbox_inches="tight")

def run_various(ns, pmax=0.1, d="z", N=40):
    try:
        y = np.load("bin/se_pauli_ns=%s_pmax=%.2f_d=%s_N=%d.npy"%("-".join(map(str, ns)), pmax, d, N))
    except FileNotFoundError:
        y = []
        for n in ns:
            phase = 2**-n
            res = []
            x = np.linspace(0, dmax, N)
            for p in x:
                px, pz = (0, 0)
                if d=="z":
                    pz=p
                elif d=="x":
                    px=p
                counts = run_pe_circuit(phase, n, pauli_x=px, pauli_z=pz)
                hc = handle_counts(counts, n)
                print_handled_counts(hc)
                s = "".join(list(reversed(create_binary_phase_str(phase, n))))
                try:
                    res += [hc[s].get("percentage")/100]
                except KeyError:
                    res += [0]
            res = np.array(res)
            y += [np.array([x, res])]
        np.save("bin/se_pauli_ns=%s_pmax=%.2f_d=%s_N=%d.npy"%("-".join(map(str, ns)), pmax, d, N),
                np.array(y))

    fig, ax = plt.subplots(figsize=(4, 3))
    ax.grid()
    for n, res in zip(ns, y):
        ax.plot(*res)
    plt.savefig("plots/simulations/se_pauli_ns=%s_pmax=%.2f_d=%s_N=%d.npy"%("-".join(map(str, ns)),
                                                                          pmax, d, N),
                bbox_inches="tight")


if __name__ == "__main__":
    for i in range(2**5):
        pauli_plot_run(5, 5, pzmax=0, pxmax=0.05, phase=i*2**-5)
    # run_various([2, 3, 4, 5], N=10)
