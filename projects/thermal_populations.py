from main import *
import matplotlib.pyplot as plt

y = []
for i in range(10):
    qp, qc, qr, cr = setup(1, login=True)
    qc.x(qr[0])
    for _ in range(20*i):
        qc.iden(qr[0])
        qc.barrier(qr[0])
    qc.measure(qr, cr)

    res = execute(qp, backend="ibmqx5")
    counts = res.get_counts(get_name())
    for k, v in counts.items():
        if "1" in k:
            y += [v/sum(counts.values())]


plt.plot(range(10), y)
plt.show()

