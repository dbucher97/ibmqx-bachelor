from simulation_errors import (gen_noise_params, coupling_map, basis_gates,
run_pe_circuit,create_binary_phase_str, pe_circuit_gate_counts)
from phase_estimation import *
import matplotlib.pyplot as plt
import numpy as np
from main import colors, count_gates


def depol_plot_run(n, l, dmax=0.08, k=1, phase=None):
    if not phase:
        phase=2**-n


    axes = setup_phase_counts_plot(plt, n, subplots=(k, l), top=1, step=0.2, phi=phase)

    for dep, ax in zip(np.linspace(0, dmax, l*k), axes):
        counts = run_pe_circuit(phase, n, depol=dep)
        hc = handle_counts(counts, n)
        t = list(hc.values())[0].get("percentage")/100
        set_top(ax, t*1.1)
        tr = 5
        x = np.ceil(-np.log10(t/tr))
        s = round((t/tr)*10**x)/10**x
        set_ticks(ax, s, t)
        ax.set_title("$p_{depol} = %.3f$\n"%dep)
        ax.plot(np.linspace(0, np.pi*2, 1000), np.ones(1000)*1/2**n+0.5, color=colors["exp1"],
                linestyle="dashed")
        plot_phase_counts(ax, hc, color=colors["exp"], width=0.12)

    plt.savefig("plots/se_depol_n=%d_l=%d_dmax=%.2f.pdf"%(n ,l*k , dmax), bbox_inches="tight", transparent = True)

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

    # g = []
    # for n in ns:
    #     phase = 2**-n
    #     g += [pe_circuit_gate_counts(phase, n)["single"]/2]
    g = [0]*len(ns)


    fig, ax = plt.subplots(figsize=(5, 3))
    ax.grid(linestyle="dotted")
    cols = [colors["exp"], colors["sim"], colors["exp1"], colors["exp2"]]
    ks = np.array(list(reversed([0.025, 0.075, 0.1, 0.15])))/0.2
    for n, res, c, gg, k in zip(ns, y, cols, g, ks):
        ax.plot(*res, color=c, label="n=%d"%n)
        ax.axhline(y=2**-n, color=c, linestyle="dashed", linewidth=1, xmin=k)
        # ax.plot(res[0], (1-res[0])**gg)
    ax.legend()
    ax.set_title("Depolarization")
    ax.set_xlabel("$p_{depol}$")
    ax.set_ylabel("success rate")
    plt.savefig("plots/se_depol_run.pdf", bbox_inches="tight", transparent=True)


if __name__ == "__main__":
    depol_plot_run(4, 3, dmax=0.1, k=2)
    run_various([2, 3, 4, 5], N=10, dmax=0.20)
