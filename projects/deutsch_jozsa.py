from main import *
from qbit_mapping import unscramble_counts
EXEC = 0
LOAD = 1

mode = LOAD

n = 16

if mode == EXEC:
    qp, qc, qr, cr = setup(n, login=True)

    def balanced():
        for i in range(n-2):
            qc.cx(qr[i], qr[i+1])

        qc.cx(qr[n-2], a)

        for i in reversed(range(n-2)):
            qc.cx(qr[i], qr[i+1])


    def constant(i):
        if i == 1:
            qc.x(a)

    a = qr[n-1]

    qc.x(a)
    qc.h(qr)

    constant(1)

    for i in range(n-1):
        qc.h(qr[i])
    qc.barrier(qr)
    qc.measure(qr, cr)

    result = execute(qp, backend="ibmqx5", info="constant 0 15")
    counts = result.get_counts("deutsch_jozsa")

elif mode == LOAD:
    ld = load("deutsch_jozsa", h=1)
    print("Info:", ld.get("info"))
    counts = ld.get("data").get("counts")


counts = unscramble_counts(counts)

zerocount = 0
bfcount = 0
shots = 1024
for bs, count in counts.items():
    bs = bs[-n:]
    if bs[1:].count("1") == 0:
        zerocount += count
    if bs[1:].count("1") <= 1:
        bfcount += count

print("constant: %.2f%%, balanced: %.2f%%" % (zerocount*100/shots, 100-(zerocount*100)/shots))

print("constant: %.2f%%, balanced: %.2f%%" % (bfcount*100/shots, 100-(bfcount*100)/shots), "1 Bitflip")
# visualize(result)
