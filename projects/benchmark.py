from main import *
import matplotlib.pyplot as plt

def benchmark(qi, N=10, start=5, step=10):
    data = []
    for i in range(start, step*N+start, step):
        qp, qc, qr, cr = setup(16, login=True)
        qc.x(qr[qi])
        for j in range(i):
            qc.iden(qr[qi])
        qc.measure(qr, cr)

        res = execute(qp, backend="ibmqx5", meta="benchmark %d idle"%i)
        counts = res.get_counts(get_name())
        print(counts)
        p = 0

        for k, v in counts.items():
            if k[qi] == "1":
                p += v

        p/=1024
        data += [p]
    return range(start, step*N+start, step), data

if __name__ == "__main__":
    x, y = benchmark(0)
    plt.plot(x, y)
    plt.show()
