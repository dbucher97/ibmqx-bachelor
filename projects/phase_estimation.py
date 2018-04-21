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

def dummy_phase_estimation(phase, n=3, ancilla=0, precision=None, config=None,
                           backend="local_qiskit_simulator"):
    from main import setup, execute, get_name
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

    cu = lambda qc, ctl, ur, n: qc.cu1(n*2*np.pi*phase, ctl, ur[0])

    phase_estimation(qc, creg, ur, cu)

    qc.barrier(qr)
    qc.measure(qr, cr)

    res = execute(qp, meta="QPE(%d+%d)-1 U1(%f)"%(n,ancilla,phase), config=config, backend=backend)

    print("N: %d\tAncilla: %d"%(n, ancilla))
    res = handle_counts(res.get_counts(get_name()), n)
    print_handled_counts(res)
    return res




if __name__ == "__main__":
    dummy_phase_estimation(0.7, n=8, precision=0.1)
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


