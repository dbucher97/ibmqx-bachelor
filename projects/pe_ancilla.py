from phase_estimation import *

if __name__ == "__main__":
    from main import setup, execute, get_name, plot_circuit

    n = 3
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

    meta="QPE(%d+%d)-1 U1(%f)"%(n,ancilla,phase)
    meta="Test_only"

    res = execute(qp, meta=meta, config=None, backend=backend)

    print("N: %d\tAncilla: %d"%(n, ancilla))
    counts = res.get_counts(get_name())

    print(counts)

