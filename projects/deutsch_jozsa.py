from main import *
import sys
import matplotlib.pyplot as plt


def balanced(qr, ar):
    for i in range(len(qr)-1):
        qc.cx(qr[i], qr[i+1])
    qc.cx(qr[len(qr)-1], ar[0])
    for i in reversed(range(len(qr)-1)):
        qc.cx(qr[i], qr[i+1])


def constant(i, ar):
    if i == 1:
        qc.x(ar[0])

n = 8

modes = {"balanced": balanced, "constant_0": lambda qr, ar: constant(0, ar), "constant_1": lambda qr,
         ar: constant(1, ar)}

gate = modes.get(sys.argv[-1])

qp, qc, qrs, cr = setup(n, additional_registers={"qr": {"ar": 1}}, login=True)
qr, ar = qrs

qc.h(qr)
qc.x(ar)
qc.h(ar)

gate(qr, ar)

qc.h(qr)

qc.barrier(qr)
qc.measure(qr, cr)

meta = "deutsch_jozsa_n=%d_%s"%(n, sys.argv[-1])
def counts_percentage(counts, offset=0):
    c = [0, 0]
    for key, val in counts.items():
        if key == "0"*len(key):
            c[0] = val
        else:
            c[1] += val
    return [0+offset, 1+offset], [x/sum(c) for x in c]



fig, ax = plt.subplots(figsize=(2.5,4))

bwidth = 0.3
baropts = {"width": bwidth}


result = execute(qp, backend="ibmqx5", meta=meta)
# tex_calibration(result.get_job_id())
counts = result.get_counts(get_name())
ax.bar(*counts_percentage(counts, offset=-bwidth/2), label="Experiment", color=colors["exp"],
       **baropts)

result = execute(qp)
counts = result.get_counts(get_name())
ax.bar(*counts_percentage(counts, offset=bwidth/2), label="Simulation", color=colors["sim"],
       **baropts)


ax.set_xticks([0, 1])
ax.set_xticklabels(["0\n(constant)", "rest\n(balanced)"])
ax.set_ylabel("Percentage")

ax.legend(bbox_to_anchor=(0, 1.2, 1, 0))

plt.savefig("plots/%s.pdf"%meta, bbox_inches="tight")


