from main import load_result, colors
import sys
import matplotlib.pyplot as plt
import numpy as np

def get_counts(n, typ, name="deutsch_jozsa"):
    res = load_result(name=name, meta="deutsch_jozsa_n=%s_%s"%(n, typ))
    return res.get_counts(name)

def perc_counts(counts):
    r = [0, 0]
    for k, v in counts.items():
        if k == "0"*len(k):
            r[0] += v
        else:
            r[1] += v
    return [x/sum(r) for x in r]

def plot_all(typ, theo=0):
    th = [0, 0]
    th[theo] = 1
    percs = [th]
    for n in sys.argv[1:]:
        percs+= [perc_counts(get_counts(n, typ))]

    fig, ax = plt.subplots(figsize=(3.2, 3))
    bwidth=0.6/len(sys.argv)
    marg = 0.04
    off = (len(sys.argv)/2-1/2)*bwidth
    cols = [colors["sim"], *[colors["exp%d"%d] for d in range(len(sys.argv)-1)]]
    c = 0
    for n, perc in zip(["Theory"]+list(map(lambda x: "ibmqx5 n=%s"%x, sys.argv[1:])), percs):
        ax.bar(np.array([0, 1])-off+c*bwidth, perc, width=bwidth-marg, label=n, color=cols[c])
        c+=1

    if theo == 0:
        ax.set_ylabel("Percentage")
    ax.set_title(typ)
    ax.set_xticks(range(2))
    ax.set_xticklabels(["all 0s\n(constant)", "rest\n(balanced)"])
    ax.grid(linestyle="dotted", color="black", alpha=0.4)
    if theo == 1: ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    plt.savefig("plots/dj_%s_%s.pdf"%("_".join(sys.argv[1:]), typ), bbox_inches="tight")



plot_all("balanced", theo=1)
plot_all("constant_0", theo=0)


