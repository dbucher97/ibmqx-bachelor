from main import *
from simulation_errors import coupling_map, basis_gates, gen_noise_params
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

rs = []

x = np.arange(0, 300, 10)
for k in x:
    qp, qc, qr, cr = setup(1)

    qc.x(qr[0])
    # qc.h(qr[0])

    for i in range(k):
        qc.iden(qr[0])

    # qc.u1(np.pi*2*5/len(x), qr[0])
    # qc.h(qr[0])

    qc.measure(qr, cr)

    res = execute(qp, config={"noise_params": gen_noise_params(relaxation=1/100)},
                  coupling_map=coupling_map, basis_gates=basis_gates)
    counts = res.get_counts(get_name())
    rs += [counts["1"]/sum(counts.values())]

rs = np.array(rs)

f = lambda x, p: (np.exp(-x/p))
popt, cov = curve_fit(f, x, rs, p0=[1])
print(popt)

plt.plot(x, rs)
plt.plot(x, f(x, *popt))
plt.show()
