from simulation_errors import gen_noise_params, coupling_map, basis_gates, run_pe_circuit,create_binary_phase_str
from phase_estimation import *
import matplotlib.pyplot as plt
import numpy as np
from main import colors


def depol_plot_run(n, l, dmax=0.08):
    phase=2**-n


    axes = setup_phase_counts_plot(plt, n, subplots=(1, l), top=1, step=0.2)

    for dep, ax in zip(np.linspace(0, dmax, l), axes):
        counts = run_pe_circuit(phase, n, depol=dep)
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

    plt.savefig("plots/se_depol_n=%d_l=%d_dmax=%.2f.pdf"%(n ,l , dmax), bbox_inches="tight")

def run_various(ns, dmax=0.1, N=40):
    try:
        y = np.load("bin/se_depol_ns=%s_dmax=%.2f_N=%d.npy"%("-".join(map(str, ns)), dmax, N))
    except FileNotFoundError:
        y = []
        for n in ns:
            phase = 2**-n
            res = []
            x = np.linspace(0, dmax, N)
            for dep in x:
                counts = run_pe_circuit(phase, n, depol=dep)
                hc = handle_counts(counts, n)
                print_handled_counts(hc)
                s = "".join(list(reversed(create_binary_phase_str(phase, n))))
                try:
                    res += [hc[s].get("percentage")/100]
                except KeyError:
                    res += [0]
            res = np.array(res)
            y += [np.array([x, res])]
        np.save("bin/se_depol_ns=%s_dmax=%.2f_N=%d.npy"%("-".join(map(str, ns)), dmax, N),
                np.array(y))

    fig, ax = plt.subplots(figsize=(4, 3))
    ax.grid()
    for n, res in zip(ns, y):
        ax.plot(*res)
    plt.savefig("plots/se_depol.pdf", bbox_inches="tight")


if __name__ == "__main__":
    run_various([2, 3, 4, 5], N=10)
