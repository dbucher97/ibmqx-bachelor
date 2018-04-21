from phase_estimation import *

if __name__ == "__main__":
    from main import *
    t = []
    tc = []
    s = []
    sc = []
    c = []
    cc = []
    for n in range(2, 9):
        ancilla = 0

        phase = 0.25

        backend="ibmqx5"

        qp, qc, qrs, cr = setup(n, additional_registers={"qr": {"ur": 1}}, login=backend=="ibmqx5")
        qr, ur = qrs
        creg = [qr[i] for i in range(len(qr))]

        qc.x(ur[0])

        def cu(qc, ctl, ur, n):
            p = (n*phase)%1
            if not (p < 1e-4 or 1-p < 1e-4):
                qc.cu1(p*2*np.pi, ctl, ur[0])

        phase_estimation(qc, creg, ur, cu)


        qc.barrier(qr)
        qc.measure(qr, cr)


        g = count_gates(qc.qasm())
        gc = count_gates(get_compiled_qasm(qp, backend="ibmqx5"))
        t += [g["total"]]
        tc += [gc["total"]]
        s += [g["single"]]
        sc += [gc["single"]]
        c += [g["controlled"]]
        cc += [gc["controlled"]]

    import matplotlib.pyplot as plt
    x = range(2, 9)
    plt.plot(x, tc)
    plt.plot(x, sc)
    plt.plot(x, cc)
    plt.plot(np.array(x), 9*np.array(x)**2)
    plt.show()
