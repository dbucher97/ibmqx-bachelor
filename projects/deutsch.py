from main import *


def constant_0(qc, qr, efficient=True):
    if not efficient:
        qc.h(qr[0])
        qc.cx(qr[0], qr[1])
        qc.h(qr[0])

def constant_1(qc, qr, efficient=True):
    if not efficient:
        qc.h(qr[0])
        qc.x(qr[0])
        qc.cx(qr[0], qr[1])
        qc.x(qr[0])
        qc.h(qr[0])
    else:
        qc.x(qr[1])

def identity(qc, qr):
    qc.cx(qr[0], qr[1])

def fnot(qc, qr):
    qc.x(qr[0])
    qc.cx(qr[0], qr[1])
    qc.x(qr[0])

d = {
    "constant 0 efficient": lambda qc, qr: constant_0(qc, qr, efficient=True),
    "constant 0 inefficient": lambda qc, qr: constant_0(qc, qr, efficient=False),
    "constant 1 efficient": lambda qc, qr: constant_1(qc, qr, efficient=True),
    "constant 1 inefficient": lambda qc, qr: constant_1(qc, qr, efficient=False),
    "identity": identity,
    "not": fnot
}

results = []

for key, fun in d.items():
    qp, qc, qr, cr = setup(2, login=True)

    qc.x(qr[1])

    # |psi_0>

    qc.h(qr[0])
    qc.h(qr[1])

    # |psi_1>

    fun(qc, qr)

    # |psi_2>

    qc.h(qr[0])

    # |psi_3>

    qc.measure(qr, cr)

    result = execute(qp, backend="ibmqx5", meta=key)
    print(key, result.get_counts(get_name()))
    results += [result]

