from main import *

qp, qc, qr, cr = setup(16, login=True)
for i in range(16):
    qc.h(qr[i])

qc.measure(qr, cr)

result = execute(qp, backend="ibmqx5")
#print(result)
visualize(result, ntk=15)
