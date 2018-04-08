from fourier_transform import iqft
import numpy as np


def phase_estimation(qc, qr, ur, cu):
    '''
    qc: Current Circuit
    qr: Computing Register
    ur: Register on wich the controlled unitary transform is performed (prepared in an eigenstate).
    cu: Controlled unitary transform. function of qc, ctl qubit, ur and n (number of performances).
    '''
    qc.h(qr)
    for i in range(len(qr)):
        cu(qc, qr[i], ur, 2**i)
    iqft(qc, qr, swap=False)

def handle_counts(counts, n):
    d = {}
    for key, val in counts.items():
        k = "".join(reversed(key[-n:]))
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

if __name__ == "__main__":
    from main import *
    n = 5
    qp, qc, qrs, cr = setup(n, additional_registers={"qr": {"ur": 1}}, login=True)
    qr, ur = qrs

    qc.x(ur[0])

    cu = lambda qc, ctl, ur, n: qc.cu1(n*2*np.pi*0.25, ctl, ur[0])

    phase_estimation(qc, qr, ur, cu)
    #qc.x(qr[2])

    qc.barrier(qr)
    qc.measure(qr, cr)

    res = execute(qp, meta="5-1 U1(0.25)", backend="ibmqx5")

    #print(res.get_counts(get_name()))
    res = handle_counts(res.get_counts(get_name()), n)
    print_handled_counts(res)

