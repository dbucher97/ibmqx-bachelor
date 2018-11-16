from simulation_errors import gen_noise_params, coupling_map, basis_gates, run_pe_circuit,create_binary_phase_str
from phase_estimation import *
import matplotlib.pyplot as plt
import numpy as np
from main import colors


def relax_plot_run(n, l, rmax=0.08, phase=None, k=1, rs=None):
    if not phase:
        phase=2**-n

    axes = setup_phase_counts_plot(plt, n, subplots=(k, l), top=1, step=0.2, phi=phase)
    if rs==None:
        rs = np.linspace(0, rmax, l*k)
    for rel, ax in zip(rs, axes):
        counts = run_pe_circuit(phase, n, relaxation=rel)
        hc = handle_counts(counts, n)
        t = list(hc.values())[0].get("percentage")/100
        set_top(ax, t*1.1)
        tr = 5
        x = np.ceil(-np.log10(t/tr))
        s = round((t/tr)*10**x)/10**x
        set_ticks(ax, s, t)
        ax.plot(np.linspace(0, np.pi*2, 1000), np.ones(1000)*1/2**n+0.5, color=colors["exp1"],
                linestyle="dashed")
        plot_phase_counts(ax, hc, color=colors["exp"], width=0.1)
        try:
            ax.set_title("$T_{1,2}=%d\,\Delta t$\n"%(int(1/rel)))
        except (OverflowError, ZeroDivisionError):
            ax.set_title("$T_{1,2}=\infty$\n")

    plt.savefig("plots/se_relax_n=%d_l=%d_rmax=%.2f.pdf"%(n ,l*k ,-1 if rs else rmax), bbox_inches="tight", transparent=True)


def run_various(ns, rmax=0.1, N=40):
    try:
        y = np.load("bin/se_relax_ns=%s_rmax=%.2f_N=%d.npy"%("-".join(map(str, ns)), rmax, N))
    except FileNotFoundError:
        y = []
        for n in ns:
            phase = 2**-n
            res = []
            x = np.linspace(0, rmax, N)
            for rel in x:
                counts = run_pe_circuit(phase, n, relaxation=rel)
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

    fig, ax = plt.subplots(figsize=(5, 3))
    ax.grid(linestyle="dotted")
    ax.set_xlabel("relaxation rate $\Delta t/T_{1, 2}$")
    ax.set_ylabel("success rate")
    for n, res in zip(ns, y):
        ax.plot(*res)
    plt.savefig("plots/se_relax_run.pdf", bbox_inches="tight", transparent=True)

def run_various_time(ns, tmax, N=40):
    try:
        y = np.load("bin/se_relax_ns=%s_tmax=%.2f_N=%d.npy"%("-".join(map(str, ns)), tmax, N))
    except FileNotFoundError:
        y = []
        for n in ns:
            phase = 2**-n*(2**n-1)
            res = []
            ts = np.linspace(1, tmax, N)
            x = 1/ts
            for rel in x:
                counts = run_pe_circuit(phase, n, relaxation=rel)
                hc = handle_counts(counts, n)
                print_handled_counts(hc)
                s = "".join(list(reversed(create_binary_phase_str(phase, n))))
                try:
                    res += [hc[s].get("percentage")/100]
                except KeyError:
                    res += [0]
            res = np.array(res)
            y += [np.array([ts, res])]
        np.save("bin/se_relax_ns=%s_tmax=%.2f_N=%d.npy"%("-".join(map(str, ns)), tmax, N),
                np.array(y))

    fig, ax = plt.subplots(figsize=(5, 3))
    ax.grid(linestyle="dotted")
    ax.set_xlabel("relaxation time $T_{1, 2}/\Delta t$")
    ax.set_ylabel("success rate")
    cols = [colors["exp"], colors["sim"], colors["exp1"], colors["exp2"], colors["exp3"]]
    for n, res, c in zip(ns, y, cols[:len(ns)]):
        ax.plot(*res, label="n=%d"%n, color=c)
    ax.legend()
    ax.set_title("Decoherence")
    plt.savefig("plots/se_relax_run_time.pdf", bbox_inches="tight", transparent=True)

if __name__ == "__main__":
    relax_plot_run(4, 3, rs=[0, 1/100, 1/50, 1/20, 1/5, 1], k=2, phase=15/16)
    run_various_time([2, 3, 4, 5], tmax=1000, N=20)
