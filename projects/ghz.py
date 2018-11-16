from main import *
import matplotlib.pyplot as plt
import numpy as np

def bell(qc, qr, n):
    if n == 1 or n == 3:
        qc.x(qr[0])
    if n == 2 or n == 3:
        qc.x(qr[1])
    qc.h(qr[0])
    qc.cx(qr[0], qr[1])

def mint(v):
    try:
        return int(v)
    except TypeError:
        return 0

def fill_keys(keys, n=16):
    r = []
    for key in keys:
        r += ["0"*(n-len(key))+key]
    return r

def bell_perc(counts, offset, ibm=False):
    keys = ["00", "01", "10", "11"]
    if ibm:
        keys = fill_keys(keys)
    vals = []
    for key in keys:
        vals += [mint(counts.get(key))]
    return np.arange(4)+offset, [x/sum(vals) for x in vals]

def run_bell(n):
    qp, qc, qr, cr = setup(2, login=True)

    bell(qc, qr, n)

    qc.measure(qr, cr)

    meta = "bell_%d"%n

    fig, ax = plt.subplots(figsize=(1.5, 2.5))
    bwidth = 0.3
    marg = 0.05

    res = execute(qp)
    counts = res.get_counts(get_name())
    ax.bar(*bell_perc(counts, -bwidth/2), color=colors["sim"], width=bwidth-marg, label="Simulation")

    res = execute(qp, meta=meta, backend="ibmqx5")
    counts = res.get_counts(get_name())
    ax.bar(*bell_perc(counts, bwidth/2, ibm=True), color=colors["exp"], width=bwidth-marg,
           label="ibmqx5")

    if n == 0: ax.set_ylabel("probability")
    names = [r"$|\Phi^+\rangle$", r"$|\Phi^-\rangle$", r"$|\Psi^+\rangle$", r"$|\Psi^-\rangle$"]
    ax.set_title(names[n])
    ax.set_xticks(range(4))
    ax.set_xticklabels(["00", "01", "10", "11"])
    ax.grid(linestyle="dotted", color="black", alpha=0.4)
    if n == 3: ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    plt.savefig("plots/%s.pdf"%meta, bbox_inches="tight", transparent=True)

def ghz_perc(counts, n, offset):
    c = [0, 0, 0]
    for k, v in counts.items():
        if k[-n:] == "0"*n:
            c[0] += v
        elif k[-n:] == "1"*n:
            c[1] += v
        else:
            c[2] += v
    return np.arange(3)+offset, [x/sum(c) for x in c]

def ghz(qc, qr):
    qc.h(qr[0])
    for i in range(len(qr)-1):
        qc.cx(qr[i], qr[i+1])

def run_ghz(ns):
    fig, ax = plt.subplots(figsize=(2.5, 2))
    theo = {"1": 1, "0": 1}
    bwidth = 0.6/(len(ns)+1)
    marg = 0.04
    off = -((len(ns)+1)/2-1/2)*bwidth
    ax.bar(*ghz_perc(theo, 1, off), label="Theory", color=colors["sim"], width=bwidth-marg)
    c = 0
    for n in ns:
        c+=1
        qp, qc, qr, cr = setup(n, login=True)

        ghz(qc, qr)

        qc.barrier(qr)
        qc.measure(qr, cr)

        res = execute(qp, backend="ibmqx5", meta="ghz_%d"%n,
                      initial_layout=gen_linear_layout([["qr", n]]))
        counts = res.get_counts(get_name())
        ax.bar(*ghz_perc(counts, n, off+c*bwidth), label="ibmqx n=%d"%n, color=colors["exp%d"%(c-1)],
               width=bwidth-marg)

    meta = "ghz_"+"_".join(map(str, ns))
    ax.set_ylabel("probability")
    ax.set_title("GHZ")
    ax.set_xticks(range(3))
    ax.set_xticklabels(["all 0s", "all 1s", "rest"])
    ax.grid(linestyle="dotted", color="black", alpha=0.4)
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    plt.savefig("plots/%s.pdf"%meta, bbox_inches="tight", transparent=True)


def gen_linear_layout(regs):
    c = 0
    m = list(range(1, 16))+[0]
    ret = {}
    for reg in regs:
        c1 = 0
        for i in range(reg[1]):
            ret[(reg[0], c1)] = ("q", c)
            c1 += 1
            c += 1
    return ret

if __name__ == "__main__":
    run_bell(0)
    # run_bell(1)
    # run_bell(2)
    # run_bell(3)
    # for i in range( 4):
        # run_bell(i)
    # run_ghz([4, 8, 16])
