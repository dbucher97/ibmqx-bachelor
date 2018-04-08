import phase_estimation as pe
from fractions import Fraction

def x7mod15(qc, ctl, qr, n):
    if n == 1:
        for i in range(len(qr)):
            qc.cx(ctl, qr[i])
        qc.cswap(ctl, qr[1], qr[2])
        qc.cswap(ctl, qr[2], qr[3])
        qc.cswap(ctl, qr[0], qr[3])
    if n == 2:
        qc.cswap(ctl, qr[0], qr[2])
        qc.cswap(ctl, qr[1], qr[3])

def handle_counts(counts, n):
    res = pe.handle_counts(counts, n)
    for k, r in res.items():
        r["fraction"] = Fraction(r["phase_angle"])
        r["order"] = r["fraction"].denominator
    return res


def find_order(cu, n, m, simulation=True, verbouse=True):
    qp, qc, qrs, cr = setup(n, additional_registers={"qr": {"ur": m}}, login=not simulation)
    qr, ur = qrs

    qc.x(ur[0])

    pe.phase_estimation(qc, qr, ur, cu)

    qc.barrier(qr)
    qc.measure(qr, cr)

    result = execute(qp, backend="local_qiskit_simulator" if simulation else "ibmqx5")
    res = handle_counts(result.get_counts(get_name()), n)

    if verbouse:
        pe.print_handled_counts(res)

    d = {}
    for v in res.values():
        x = v["order"]
        if x in d:
            d[x] += v["counts"]
        else:
            d[x] = v["counts"]
    return d



if __name__ == "__main__":
    from main import *
    n = 4
    m = 4
    #for i in range(4):
    qp, qc, qrs, cr = setup(m, additional_registers={"qr": {"ur": m}}, login=True)
    qr, ur = qrs

    qc.x(qr[0])


    #x7mod15(qc, qr[0], qr, 1)
    #x7mod15(qc, qr[1], qr, 2)
    for i in range(len(qr)):
        qc.x(qr[i])
    qc.swap(qr[1], qr[2])
    qc.swap(qr[2], qr[3])
    qc.swap(qr[0], qr[3])

    qc.barrier(qr)
    qc.barrier(qr)
    qc.measure(qr, cr)

    res = execute(qp, backend="ibmqx5", meta="modexptest_one", unscramble=True)
    print(res.get_counts(get_name()))

    #res = find_order(x7mod15, n, m, simulation=False)
    print(res)

