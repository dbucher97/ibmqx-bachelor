from main import *

qp, qc, qr, cr = setup(2, login=True)

def constant_0(efficient=True):
    if not efficient:
        qc.h(qr[0])
        qc.cx(qr[0], qr[1])
        qc.h(qr[0])

def constant_1(efficient=True):
    if not efficient:
        qc.h(qr[0])
        qc.x(qr[0])
        qc.cx(qr[0], qr[1])
        qc.x(qr[0])
        qc.h(qr[0])
    else:
        qc.x(qr[1])

def identity():
    qc.cx(qr[0], qr[1])

def fnot():
    qc.x(qr[0])
    qc.cx(qr[0], qr[1])
    qc.x(qr[0])

qc.x(qr[1])

# |psi_0>

qc.h(qr[0])
qc.h(qr[1])

# |psi_1>

#constant_0(efficient=False)
#constant_1(efficient=False)
#constant_0(efficient=True)
#constant_1(efficient=True)
#identity()
fnot()

# |psi_2>

qc.h(qr[0])

# |psi_3>

qc.measure(qr, cr)

result = execute(qp, backend="ibmqx5", sav=0)
print(result)
print(result.get_counts("deutsch"))
save(result, "ibmqx5", info="not")
visualize(result, ntk=15)
