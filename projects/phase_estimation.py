from main import *
from fourier_transform import iqft
import math
import numpy as np

qp, qc, qr, cr = setup(3, login=True)

qc.h(qr[0])
qc.h(qr[1])
#qc.h(qr[2])

qc.x(qr[2])

u = lambda x, y: qc.cu1(1*math.pi/2, x, y)

u(qr[0], qr[2])
u(qr[1], qr[2])
u(qr[1], qr[2])
# u(qr[2], qr[3])
# u(qr[2], qr[3])
# u(qr[2], qr[3])
# u(qr[2], qr[3])

iqft(qc, [qr[1], qr[0]])

qc.barrier(qr)

qc.measure(qr[0], cr[0])
qc.measure(qr[1], cr[1])
#qc.measure(qr[2], cr[2])

result = execute(qp, backend="ibmqx5", info="2bit phase estimation S gate")
d = {}
for key, val in result.get_counts("phase_estimation").items():
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

