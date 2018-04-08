import math


def qbit_name(qbit):
    return qbit[0].name+str(qbit[1])


def cR(qc, k, ctl, tgt):
    qc.cu1(2*math.pi/2**k, ctl, tgt)


def cRdag(qc, k, ctl, tgt):
    qc.cu1(-2*math.pi/2**k, ctl, tgt)


def qft(qc, qbits, swap=True, debug=False):
    n = len(qbits)
    if debug:
        print("\t".join([qbit_name(qbits[i]) for i in range(n)]))
    for i in range(n):
        qc.h(qbits[i])
        if debug:
            print("\t"*i+"H")
        for j in range(i+1, n):
            cR(qc, j-i+1, qbits[j], qbits[i])
            if debug:
                if i < j:
                    print("\t"*i+"o"+"-"*(8*(j-i)-1)+"R"+str(j-i+1))
                if j < i:
                    print("\t"*j+"R"+str(j-i+1)+"-"*(8*(j-i)-2)+"o")

    if swap==True:
        for i in range(int(n/2)):
            qc.swap(qbits[i], qbits[n-1-i])
            if debug:
                print("\t"*i+"x"+"-"*(8*(n-1-2*i)-1)+"x")

def qft2(qc, qr, swap=True):
    n = len(qr)
    for i in range(n):
        qc.h(qr[i])
        for j in range(n-i-1):
            cR(qc, j+2, qr[j+i+1], qr[i])
    if swap:
        for i in range(int(n/2)):
            qc.swap(qr[i], qr[n-i-1])

def iqft2(qc, qr, swap=True):
    n = len(qr)
    if swap:
        for i in range(int(n/2)):
            qc.swap(qr[i], qr[n-i-1])
    for i in reversed(range(n)):
        for j in reversed(range(n-i-1)):
            cRdag(qc, j+2, qr[j+i+1], qr[i])
        qc.h(qr[i])


def iqft(qc, qbits, swap=True, debug=False):
    n = len(qbits)
    if debug:
        print("\t".join([qbit_name(qbits[i]) for i in range(n)]))
    if swap==True:
        for i in range(int(n/2)):
            qc.swap(qbits[i], qbits[n-1-i])
            if debug:
                print("\t"*i+"x"+"-"*(8*(n-1-2*i)-1)+"x")
    for i in reversed(range(n)):
        for j in reversed(range(i+1, n)):
            cRdag(qc, j-i+1, qbits[j], qbits[i])
            if debug:
                if i < j:
                    print("\t"*i+"o"+"-"*(8*(j-i)-1)+"R+"+str(j-i+1))
                if j < i:
                    print("\t"*j+"R+"+str(j-i+1)+"-"*(8*(j-i)-3)+"o")
        qc.h(qbits[i])
        if debug:
            print("\t"*i+"H")


if __name__ == "__main__":
    from qiskit import QuantumProgram
    import matplotlib.pyplot as plt
    from qiskit.tools.qi.qi import qft as oqft

    qp = QuantumProgram()
    qr = qp.create_quantum_register("qr", 2)
    cr = qp.create_classical_register("cr", 4)
    qc = qp.create_circuit("fourier", [qr], [cr])

    iqft2( qc, list(reversed(qr)), swap=True )


    result = qp.execute(["fourier"], backend="local_unitary_simulator")
    mat = result.get_data("fourier").get("unitary")
    import numpy as np
    print(np.round(mat, decimals=2))
    plt.matshow(mat.real, cmap="RdBu")
    plt.show()
