import numpy as np
from scipy.optimize import fsolve
import matplotlib.pyplot as plt

es = []

def e(n, R):
    global es
    if len(es) > n:
        return es[n]
    if n == 0:
        ret = 1
    else:
        ret = 1/n*sum([(-1)**i*e(n-i-1, R)*R[i+1] for i in range(n)])
    es += [ret]
    return ret

def s(n, es, N):
    a = min(n, N)
    return lambda x : sum([(-1)**(n+k)*es[n-k]*x**k for k in range(a+1)])

def p(n, es, N):
    a = min(n, N)
    return list(reversed([(-1)**(n+k)*es[n-k] for k in range(a+1)]))

rho = np.load("state_tomography/rho.npy")
ev = np.linalg.eigvals(rho)

n = 7
N = 16
print(sum(ev))
# plt.plot(x, s(n, es, N)(x))
# plt.show()
R = [sum(ev**i) for i in range(n+1)]
print(R)
e(n, R)
x = np.linspace(-0.5, 1, 100)
# plt.plot(x, s(n, es, N)(x))
# plt.show()
r = np.roots(p(n, es, N))
print(r, sum(r))
# plt.plot(x, s(n, es, N)(x))
plt.bar(range(min(n, N)), r.real)
plt.show()

