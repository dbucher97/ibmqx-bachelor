import os
import json
from main import *

'''
qc.measure(qr, cr) doesn't map the measured qbit to the classical bit with the same index.

this script sets every qbit squentiually high and measures the outcome to provide a map how the measurements are mapped.
'''

def test(i):
    qp, qc, qr, cr = setup(16)  # , login=True)
    qc.x(qr[i])
    qc.measure(qr, cr)
    result = execute(qp, backend="ibmqx5", sav=0)
    print(i, result.get_counts("qbit_mapping"))
    save(result, "ibmqx5", info="q%d" % i)

# for i in range(9, 16):
#    test(i)

def num(s):
    return "".join(reversed(s)).find("1")


def print_mapping():
    mapping = {}
    for f in os.listdir("qbit_mapping"):
        with open("qbit_mapping/"+f, "r") as ff:
            j = json.load(ff)
        info = j.get("info")
        counts = j.get("data").get("counts")
        bitstr = max(counts.items(), key=lambda x: x[1])[0]
        mapping[info] = bitstr
        #print(num(bitstr))
    mapping = {i: "c"+str(num(mapping[i])) for i in sorted(mapping, key=lambda x: int(x[1:]))}
    for k, v in mapping.items():
        print(k + "->" + v)

def load_mapping():
    mapping = {}
    with open("qbit_mapping.txt", "r") as f:
        for line in f:
            q, c = line.strip().split("->")
            q = int(q[1:])
            c = int(c[1:])
            mapping[c] = q
    return mapping

def unscramble(key, mapping):
    nk = ["0" for i in range(len(key))]
    key = list(reversed(key))
    for i in range(len(key)):
        nk[mapping[i]] = key[i]
    return "".join(reversed(nk))

def unscramble_counts(counts):
    mapping = load_mapping()
    return {unscramble(key, mapping): value for key, value in counts.items()}
