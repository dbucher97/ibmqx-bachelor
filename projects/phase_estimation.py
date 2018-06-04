from fourier_transform import iqft
import numpy as np


def phase_estimation(qc, qr, ur, cu, debug=False):
    '''
    qc: Current Circuit
    qr: Computing Register
    ur: Register on wich the controlled unitary transform is performed (prepared in an eigenstate).
    cu: Controlled unitary transform. function of qc, ctl qubit, ur and n (number of performances).
    '''
    for i in range(len(qr)):
        qc.h(qr[i])
    for i in range(len(qr)):
        cu(qc, qr[i], ur, 2**i)
    iqft(qc, qr, swap=False)


def handle_counts(counts, n, skip=[]):
    d = {}
    skip = sorted(skip)
    # print(skip)
    for key, val in counts.items():
        kl = list(key)
        for s in skip:
             del kl[len(key)-s-1]
        k = "".join(reversed(kl[-n:]))
        # print(key, k, kl)
        if k in d:
            d[k] += val
        else:
            d[k] = val
    res = {}
    shots = sum(d.values())

    for key, val in d.items():
        x = res[key] = {}
        x["counts"] = val
        x["percentage"] = (val*100/shots)
        x["phase_angle"] = int(key, 2)/2**len(key)
        x["phase_value"] = np.exp(2*np.pi*1j*x["phase_angle"])

    res = {k: v for k, v in sorted(res.items(), key=lambda x:x[1]["counts"], reverse=True)}
    return res

def print_handled_counts(res):
    from tabulate import tabulate
    def val_list(d):
        val = []
        for v in d.values():
            if isinstance(v, complex):
                v = str(np.round(v, decimals=2))
            val += [v]
        return val
    x = [[key, *val_list(value)] for key, value in res.items()]
    print(tabulate(x, headers=["result", *list(res.values())[0].keys()], tablefmt='orgtbl'))

def dummy_phase_estimation(phase, n=3, ancilla=0, precision=None, config=None,
                           backend="local_qiskit_simulator", skip=[], coupling_map=None,
                           basis_gates=None):
    from main import setup, execute, get_name, plot_circuit
    if precision:
        ancilla = int(np.ceil(np.log2(2+1/2/precision)))
    if ancilla:
        qp, qc, qrs, cr = setup(n, additional_registers={"qr": {"ur": 1, "ar": ancilla}},
                                login=backend=="ibmqx5")
        qr, ur, ar = qrs
        creg = [qr[i] for i in range(len(qr))]
        creg += [ar[i] for i in range(len(ar))]
    else:
        qp, qc, qrs, cr = setup(n, additional_registers={"qr": {"ur": 1}}, login=backend=="ibmqx5")
        qr, ur = qrs
        creg = [qr[i] for i in range(len(qr))]
    qc.x(ur[0])

    def cu(qc, ctl, ur, n):
        # if abs(n*phase-1) > 1e-3 and n*phase > 1e-3:
        qc.cu1(n*2*np.pi*phase, ctl, ur[0])
        # if n == 1:
            # qc.cz(ctl, ur[0])

    phase_estimation(qc, creg, ur, cu)
    # qc.optimize_gates()
    qc.barrier(qr)
    qc.barrier(ur)
    qc.measure(qr, cr)

    res = execute(qp, meta="QPE(%d+%d)-1 U1(%f)"%(n,ancilla,phase), config=config, backend=backend,
                  coupling_map=coupling_map, basis_gates=basis_gates)
    # print(res.get_ran_qasm(get_name()))
    # print(res.get_counts(get_name()))
    print("N: %d\tAncilla: %d"%(n, ancilla))
    hc = handle_counts(res.get_counts(get_name()), n, skip=skip)
    print_handled_counts(hc)
    return hc

def set_top(ax, top, bottom=0.5, r=0.1):
    xr = top*r/(1-r)
    ax.set_ylim(bottom-xr, bottom+top)

def set_ticks(ax, step, top, bottom=0.5):
    ax.set_yticks(np.arange(bottom+step, bottom+top, step))
    ax.set_yticklabels(map(lambda x: str(np.round(x, decimals=3)).rstrip("0"),
                           np.arange(step, top, step)))

def setup_phase_counts_plot(plt, n, bottom=0.5, width=None, top=0.25, r=0.1, step=0.1, fs=4,
                            phi=None, subplots=None):
    xr = top*r/(1-r)
    if subplots:
        fig, axes = plt.subplots(*subplots, figsize=(fs*subplots[1],
                                                     fs*subplots[0]),
                                 subplot_kw={"polar": True})
        fig.subplots_adjust(wspace=fs/10)
    else:
        fig, ax = plt.subplots(figsize=(fs, fs), subplot_kw={"polar": True})
        axes = [ax]

    for ax in axes:
        nn = min(n, 4)
        ax.set_xticks([x/2**nn*2*np.pi for x in range(2**nn)])
        ax.set_xticklabels([round(x/2**nn, 3) for x in range(2**nn)])
        ax.set_rlabel_position(68)
        set_ticks(ax, step, bottom, top)
        set_top(ax, top, bottom, r)
        # ax.set_ylabel("counts/shots")
        ax.yaxis.grid(True, color="black", alpha=0.5)
        ax.set_axisbelow(True)
        ax.xaxis.grid(False)
        ax.plot(np.linspace(0, 2*np.pi, 1000, endpoint=False), bottom*np.ones(1000), color="black",
                linewidth=.5)
        for p in [x/2**n*2*np.pi for x in range(2**n)]:
            ax.axvline(p, color="gray", ymin=r, linewidth=1, zorder=-1)
        if phi:
            ax.axvline(phi*2*np.pi, color="red", ymin=r, linestyle="dashed")
    if len(axes) == 1:
        return axes[0]
    return axes

def plot_phase_counts(ax, hc, label=None, color="b", bottom=0.5, width=0.1, offset=0):
    phi = np.array(list(map(lambda x: x["phase_angle"], hc.values())))
    prob = np.array(list(map(lambda x: x["percentage"], hc.values())))
    bars = ax.bar(phi*2*np.pi+offset, prob/100, width=width, bottom=bottom, color=color, label=label, zorder=-0.5)
    return bars

def run_phase_plot(n, phase):
    import matplotlib.pyplot as plt
    from main import colors
    coupling_map = [[1, 0], [1, 2], [2, 3], [3, 4], [3, 14], [5, 4], [6, 5], [6, 7], [6, 11], [7, 10],
                    [8, 7], [9, 8], [9, 10], [11, 10], [12, 5], [12, 11], [12, 13], [13, 4], [13, 14],
                    [15, 0], [15, 2], [15, 14]]
    basis_gates = "u1,u2,u3,cx,id"
    skip = []
    if n==4:
        skip=[0]
    hc = dummy_phase_estimation(phase, n=n, backend="ibmqx5", coupling_map=coupling_map,
                                basis_gates=basis_gates, skip=skip)
    hc_sim = dummy_phase_estimation(phase, n=n, coupling_map=coupling_map, basis_gates=basis_gates)
    ax = setup_phase_counts_plot(plt, n, top=1, step=0.2, fs=3, phi=phase)
    plot_phase_counts(ax, hc_sim, width = 0.15, offset=0.1, color=colors["sim"], label="Simulation")
    plot_phase_counts(ax, hc,     width = 0.15, offset=-0.1, color=colors["exp"], label="ibmqx5")
    if n == 1 and phase==0.5:
        ax.legend(loc="upper right", bbox_to_anchor=(1.1, 0.1))
    plt.savefig("plots/pe_n=%d_p=%.5f.pdf"%(n, phase))
    plt.cla()

if __name__ == "__main__":
    for i in range(1, 4):
        run_phase_plot(i, 0.5)
    for i in range(1, 4):
        run_phase_plot(i, 0.7)
    # if len(res) > 1:
    #     top2 = list(res.values())[:2]
    #     from scipy.optimize import minimize
    #
    #     def prob(x, p):
    #         return 1/4**n*np.sin(np.pi*2**n*(x-p))**2/np.sin(np.pi*(x-p))**2
    #
    #     def opt_fun(x):
    #         return (prob(x, top2[0]["phase_angle"])-top2[0]["percentage"]/100)**2 + (prob(x, top2[1]["phase_angle"])-top2[1]["percentage"]/100)**2
    #
    #     pa = [top2[0]["phase_angle"], top2[1]["phase_angle"]]
    #
    #     # import matplotlib.pyplot as plt
    #     # x = np.linspace(min(pa)+0.00001, max(pa), 10, endpoint=False)
    #     # print(opt_fun(x))
    #     # print(min(enumerate(opt_fun(x)), key=lambda x: x[1])[0])
    #     # phase = x[min(enumerate(opt_fun(x)), key=lambda x: x[1])[0]]
    #     # #plt.plot(x, opt_fun(x))
    #     # # plt.plot([top2[0]["phase_angle"], top2[1]["phase_angle"]], [top2[0]["percentage"]/100,
    #     # #                                                             top2[1]["percentage"]/100], "o")
    #     # #plt.show()
    #     # print(phase)
    #
    #     r=minimize(opt_fun, (pa[0]+pa[1])/2, bounds=((min(pa), max(pa)),))
    #     print(r.x[0])


