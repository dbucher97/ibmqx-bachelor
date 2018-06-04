from main import *
import numpy as np
import matplotlib.pyplot as plt

def iterative_phase_estimation(n, u, cu, backend="local_qiskit_simulator", m=""):
    phi = []
    countss = []
    for i in reversed(range(n)):
        qp, qc, qrs, cr = setup(1, additional_registers={"qr": {"ur": u}}, login=True)
        qr, ur = qrs

        qc.h(qr[0])
        #if i%2==0:
        #    qc.x(ur[0])
        # qc.rx(np.pi*0.5, ur[0])

        qc.x(ur[0])

        cu(qc, qr[0], ur, 2**i)

        if phi:
            c = 2
            phase = 0
            for p in reversed(phi):
                if p:
                    phase += 2**-c
                c += 1
            if not(phase%1 <= 1e-4 or 1-phase%1 <=1e-4):
                qc.u1(-2*np.pi*phase, qr[0])

        qc.h(qr[0])

        qc.measure(qr, cr)


        res = execute(qp, meta="ipea_%s_n=%d_i=%d"%(m, n, i), backend=backend)

        counts = res.get_counts(get_name())
        counts = {k: v for k, v in sorted(counts.items(), key=lambda x: x[1], reverse=True)}
        countss += [counts]
        vague = False
        print(counts)
        try:
            x, y = list(counts.items())[:2]
            if abs(x[1]-y[1])/(x[1]+y[1]) < 0.1:
                vague = True
        except ValueError:
            x = list(counts.items())[0]
        phi += [int(x[0])]
        print(phi[-1], vague)
    phase = 0
    c = 1
    for p in reversed(phi):
        phase += p*2**-c
        c+=1
    print(phase)
    return phi, phase, countss

def plot_countss(phi, phase, countss, offset, width, color, marg=0.05, text=False, label=None):
    c = 0
    for p, counts in zip(phi, countss):
        one, zero = 0, 0
        for k, v in counts.items():
            if k == "1".rjust(len(k), "0"):
                one = v/sum(counts.values())
            else:
                zero = v/sum(counts.values())
        if label and c > 0:
            label=None
        plt.bar(np.array([c, c])+offset, [one, -zero], width=width-marg, color=color, label=label)
        if text:
            plt.text(c-0.1, 1.1, str(p))
        c += 1

def plot_with_phase(org_phase, n):
    cu = lambda qc, ctl, ur, n: qc.cu1(2*np.pi*n*org_phase, ctl, ur[0])
    fig, ax = plt.subplots(figsize=(8, 2.5))
    width=0.2
    phi, phase, countss = iterative_phase_estimation(n, 1, cu, backend="local_qiskit_simulator",
                                                     m="u1(%f)"%(org_phase))
    plot_countss(phi, phase, countss, -width/2, width, colors["sim"], label="Simulation")
    phi, phase, countss = iterative_phase_estimation(n, 1, cu, backend="ibmqx5",
                                                     m="u1(%f)"%(org_phase))
    plot_countss(phi, phase, countss, width/2, width, colors["exp"], text=True, label="ibmqx5")

    ax.axhline(y=0, color="black", linewidth=0.8)
    ax.axhline(y=0.5, color="red", linestyle="dashed", alpha=0.7)
    ax.axhline(y=-0.5, color="red", linestyle="dashed", alpha=0.7)

    ax.set_title(r"IPEA $\varphi=%f$"%org_phase)

    # ax.text(10, 1, r"$\tilde{\varphi} = 0.%s = %f$" % ("".join(map(str, reversed(phi))), phase),
    #         rotation=90)

    ax.set_xlabel("Iteration\n"+r"$\tilde{\varphi} = 0.%s = %.10f$" %
                  ("".join(map(str,reversed(phi))), phase))
    ax.set_yticks([-0.75, -0.5, -0.25, 0, 0.25, 0.5, 0.75])
    ax.set_yticklabels(["", "0", "", "", "", "1", ""])
    ax.set_ylabel("Decision")

    ax.grid(linestyle="dotted")

    ax.set_xticks(range(0, n))
    ax.set_xticklabels(range(1, n+1))

    ax.set_ylim(ymax=1.3)
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    plt.savefig("plots/ipea.pdf", bbox_inches="tight")


if __name__ == "__main__":
    plot_with_phase(0.7, 10)
