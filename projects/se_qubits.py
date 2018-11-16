from simulation_errors import gen_noise_params, coupling_map, basis_gates, run_pe_circuit,create_binary_phase_str
from phase_estimation import *
import matplotlib.pyplot as plt
import numpy as np
from main import colors

def plot_ret(ret, labels=None, ylabel=None, paramstr=""):
    if labels == None:
        labels = [None]*len(ret)
    fig, ax = plt.subplots(figsize=(5, 2))
    markers = ["v", "o", "^", "D", "s"]
    cols = [colors["exp"], colors["sim"], colors["exp1"], colors["exp2"], colors["exp3"]]
    for (x, y), label, m, c in zip(ret, labels, markers[:len(ret)], cols[:len(ret)]):
        ax.plot(x, y, label=label, color=c, marker=m, markerfacecolor="None")

    ax.grid(linestyle="dotted", color="gray")
    ax.set_xlabel(r"number of qubits $n$")
    if ylabel:
        ax.set_ylabel(ylabel)
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))
    ax.set_title("fixed relaxation time" if "rs" in paramstr else "fixed depolarization probability")
    plt.savefig("plots/se_qubits2%s.pdf"%paramstr, bbox_inches="tight", transparent=True)

def phase_resolvable(phase, n):
    return phase in np.arange(0, 1, 2**-n)

def qubit_run_depol(nmax=9, ds=[0], nmin=2, phase=None):
    paramstr="_n=%d-%d_ds=%s" % (nmin, nmax, "-".join(list(map(str, ds))))
    if phase:
        paramstr += "_p=%.3f"%phase
    try:
        ret = np.load("bin/se_qubit%s.npy" % paramstr)
    except FileNotFoundError:
        ret = []
        for d in ds:
            x = range(nmin, nmax+1)
            y = []
            for n in x:
                if phase==None:
                    phase = 2**-n
                res = run_pe_circuit(phase, n, depol=d)
                hc = handle_counts(res, n)
                y += [0]
                for v in hc.values():
                    if phase_resolvable(phase, n):
                        if v["phase_angle"] == phase:
                            y[-1] += v["percentage"]/100
                            break
                    elif abs(v["phase_angle"]-phase) < 2**-n:
                        y[-1] += v["percentage"]/100
                    elif v["phase_angle"] == 0 and abs(1-phase) < 2**-n:
                        y[-1] += v["percentage"]/100
            ret += [(np.array(x), np.array(y))]
        np.save("bin/se_qubit%s.npy" % paramstr, ret)
    plot_ret(ret, paramstr=paramstr, labels=list(map(lambda x: r"$p_{depol}=%.3f$"%x, ds)),
             ylabel="success rate")


def qubit_run_relax(nmax=9, rs=[0], nmin=2, phase=None):
    paramstr="_n=%d-%d_rs=%s" % (nmin, nmax, "-".join(list(map(str, rs))))
    if phase:
        paramstr += "_p=%.3f"%phase
    try:
        ret = np.load("bin/se_qubit%s.npy"%paramstr)
    except FileNotFoundError:
        ret = []
        for r in rs:
            x = range(nmin, nmax+1)
            y = []
            for n in x:
                if phase==None:
                    phase = 2**-n
                res = run_pe_circuit(phase, n, relaxation=r)
                hc = handle_counts(res, n)
                l = len(y)
                for v in hc.values():
                    if v["phase_angle"] == phase:
                        y += [v["percentage"]/100]
                        break
                if len(y) == l:
                    y += [0]
            ret += [(np.array(x), np.array(y))]
        np.save("bin/se_qubit%s.npy" % paramstr, ret)
    plot_ret(ret, labels=list(map(lambda x: "$T_{1,2}=%d\,\Delta t$"%int(1/x), rs)),
             paramstr=paramstr, ylabel="success rate")

if __name__ == "__main__":
    qubit_run_depol(nmin=1, nmax=8, ds=[0.001, 0.003, 0.01, 0.03, 0.1])
    qubit_run_relax(nmax=8, nmin=1, rs=[1/1000, 1/375, 1/100, 1/30, 1/10])

