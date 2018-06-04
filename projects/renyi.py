qfrom main import *

n = 6
k = 2

qp, qc, qr, cr = setup(n*k+1, classical=1, login=True)


ctl = qr[0]
qc.h(ctl)

phis = [[qr[i+j*n+1] for i in range(n)] for j in range(k)]

def spt(qr):
    for i in range(n):
        qc.h(qr[i])
    for i in range(n):
        qc.cz(qr[i], qr[(i+1)%n])

for phi in phis:
    spt(phi)

def perm(phis):
    for j in range(int(n/2)):
        for i in range(len(phis)-1):
            qc.cswap(ctl, phis[i][j], phis[i+1][j])

perm(phis)

qc.h(ctl)

qc.measure(ctl, cr[0])
plot_circuit(qc)
shots=1024
res = execute(qp, backend="ibmqx5", shots=shots)
counts = res.get_counts(get_name())

print(counts)

print(counts.get("1")/shots)
