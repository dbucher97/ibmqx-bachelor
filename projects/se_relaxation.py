from simulation_errors import gen_noise_params, coupling_map, basis_gates, run_pe_circuit,create_binary_phase_str
from phase_estimation import *
import matplotlib.pyplot as plt
import numpy as np
from main import colors


def relax_plot_run(n, l, rmax=0.08, phase=None):
    if not phase:
        phase=2**-n


    axes = setup_phase_counts_plot(plt, n, subplots=(1, l), top=1, step=0.2)

    for rel, ax in zip(np.linspace(0, rmax, l), axes):
        counts = run_pe_circuit(phase, n, relaxation=rel)
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

    plt.savefig("plots/se_relax_n=%d_l=%d_rmax=%.2f.pdf"%(n ,l , rmax), bbox_inches="tight")

def run_various(ns, rmax=0.1, N=40):
    try:
        y = np.load("bin/se_relax_ns=%s_rmax=%.2f_N=%d.npy"%("-".join(map(str, ns)), rmax, N))
    except FileNotFoundError:
        y = []
        for n in ns:
            phase = 2**-n
            res = []
            x = np.linspace(0, rmax, N)
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
        np.save("bin/se_relax_ns=%s_rmax=%.2f_N=%d.npy"%("-".join(map(str, ns)), rmax, N),
                np.array(y))

    fig, ax = plt.subplots(figsize=(4, 3))
    ax.grid()
    for n, res in zip(ns, y):
        ax.plot(*res)
    plt.savefig("plots/se_relax.pdf", bbox_inches="tight")


if __name__ == "__main__":
    relax_plot_run(5, 5, phase=0.5, rmax=1/100)
    # run_various([2, 3, 4], rmax=0.05)
