from simulation_errors import gen_noise_params, coupling_map, basis_gates, run_pe_circuit,create_binary_phase_str
from phase_estimation import *
import matplotlib.pyplot as plt
import numpy as np
from main import colors

def qubit_run_depol(nmax=9, ds=[0], nmin=2, phase=None):
    try:
        ret = np.load("bin/se_qubit_n=%d-%d_ds=%s.npy" % (nmin, nmax, "-".join(list(map(str, ds)))))
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
                l = len(y)
                for v in hc.values():
                    if v["phase_angle"] == phase:
                        y += [v["percentage"]/100]
                        break
                if len(y) == l:
                    y += [0]
            ret += [(np.array(x), np.array(y))]
        np.save("bin/se_qubit_n=%d-%d_ds=%s.npy" % (nmin, nmax, "-".join(list(map(str, ds)))), ret)

    for x, y in ret:
        plt.plot(x, y)
    plt.show()

def qubit_run_relax(nmax=9, rs=[0], nmin=2, phase=None):
    try:
        ret = np.load("bin/se_qubit_n=%d-%d_rs=%s.npy" % (nmin, nmax, "-".join(list(map(str, rs)))))
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
        np.save("bin/se_qubit_n=%d-%d_rs=%s.npy" % (nmin, nmax, "-".join(list(map(str, rs)))), ret)

    for x, y in ret:
        plt.plot(x, y)
    plt.show()

if __name__ == "__main__":
    # qubit_run_depol(nmin=1, nmax=8, ds=[0.001, 0.005, 0.01, 0.05, 0.1])
    qubit_run_relax(nmax=8, nmin=1, rs=[1/1000, 1/500, 1/100, 1/50, 1/10])

