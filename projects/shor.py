from main import *
from fourier_transform import iqft
n = 2
m = 4

qp, qc, qrs, cr = setup(n, additional_registers={"qr": {"a": m}}, login=False)

qr, a = qrs

qc.h(qr)

qc.x(a[0])

def cmodexp7(qc, ctl, qr):
    for i in range(n):
        qc.cx(ctl, qr[i])
    qc.cswap(ctl, qr[1], qr[2])
    qc.cswap(ctl, qr[2], qr[3])
    qc.cswap(ctl, qr[0], qr[3])

def cmodexp72(qc, ctl, qr):
    qc.cswap(ctl, qr[0], qr[2])
    qc.cswap(ctl, qr[1], qr[3])


cmodexp7(qc, qr[0], a)
cmodexp72(qc, qr[1], a)

iqft(qc, qr, swap=True)

qc.barrier(qr)
qc.measure(qr, cr)

result = execute(qp)

print(result.get_counts(get_name()))
