from main import *
from fourier_transform import iqft2, qft2
from utils import rand_prep, max_count_to_int, prep2, max_count_to_int2
import math

def cR(qc, ctl, tgt, k):
    qc.cu1(2*math.pi/2**k, ctl, tgt)

def qft_add(qc, ar, br):
    qft2(qc, br, swap=False)
    m = len(br)
    for i in range(m):
        n = i+1
        for j in range(len(ar)-i):
            cR(qc, ar[j], br[i+j], n)
            # print((j)*"\t"+"o"+"-"*(8*(m-j+i+j)-1)+"R%d"%n)
            print((i+j)*"\t"+"R%d"%n+"-"*(8*(m-i)-2)+"o")

    iqft2(qc, br, swap=False)

if __name__ == "__main__":
    n = 4
    m = 4
    qp, qc, qrs, cr = setup(n, additional_registers={"qr": {"ar": m}}, login=False)
    br, ar = qrs

    #print(rand_prep(qc, br), rand_prep(qc, ar))
    prep2(qc, 1, ar, m)
    prep2(qc, 1, br, n)

    qft_add(qc, ar, br)
    qc.measure(br, cr)

    res = execute(qp)
    counts = res.get_counts(get_name())
    print(counts)
    print(max_count_to_int2(counts, n))

