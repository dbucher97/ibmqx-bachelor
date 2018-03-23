from main import *
from fourier_transform import iqft
import math
import numpy as np
from qbit_mapping import unscramble_counts
n = 5

qp, qc, qr, cr = setup(n, login=True)

rb = qr[n-1]
qc.x(rb)

for i in range(n-1):
    qc.h(qr[i])

u = lambda x, y: qc.cu1(-1*math.pi/2, x, y)

for i in range(n-1):
    for _ in range(2**i):
        u(qr[i], rb)


iqft(qc, [qr[i] for i in reversed(range(n-1))])

qc.barrier(qr)

qc.measure(qr[0], cr[0])
qc.measure(qr[1], cr[1])
#qc.measure(qr[2], cr[2])

#result = execute(qp, backend="ibmqx5", info="2bit phase estimation S gate (5 bit acc)")
d = {}

counts = load("phase_estimation").get("data").get("counts")
counts = unscramble_counts(counts)
for key, val in counts.items():
    k = key[-2:]
    if k in d:
        d[k] += val
    else:
        d[k] = val

print(d)
phase = []

for key in d:
    count = 1
    s = 0
    for c in key:
        s += int(c)/2**count
        count += 1
    phase += [s]

eigenvalue = []

for p in phase:
    eigenvalue += [np.exp(2*np.pi*1j*p)]

shots = sum(d.values())

print("\t".join(map(lambda x: "%.2f"%(x*100/shots), d.values())))
print("\t".join(map(str, phase)))
print("\t".join(map(lambda x: str(np.round(x, decimals=2)), eigenvalue)))
#avg = sum(list(map(lambda x: x[0]*x[1], zip(d.values(), phase))))/shots
#print("avg: "+str(avg))

