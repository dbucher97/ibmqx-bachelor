import os
import json

'''
qc.measure(qr, cr) doesn't map the measured qbit to the classical bit with the same index.

this script sets every qbit squentiually high and measures the outcome to provide a map how the measurements are mapped.
'''

results = []

def test(i):
    global results
    print("Qbit %d"%i)
    qp, qc, qr, cr = setup(16, login=True)
    qc.x(qr[i])
    qc.measure(qr, cr)
    result = execute(qp, backend="ibmqx5", meta="q%d"%i, unscramble=False)
    results += [result]
    print(result.get_counts("qbit_mapping"))


def num(s):
    return "".join(reversed(s)).find("1")


def print_mapping():
    mapping = {}
    for res in results:
        meta = get_meta_from_result(res)
        counts = res.get_counts(get_name())
        bitstr = max(counts.items(), key=lambda x: x[1])[0]
        mapping[meta] = bitstr
        #print(num(bitstr))
    mapping = {i: "c"+str(num(mapping[i])) for i in sorted(mapping, key=lambda x: int(x[1:]))}
    with open("qbit_mapping.txt", "w") as f:
        for k, v in mapping.items():
            print(k + "->" + v)
            f.write(k + "->" + v + "\n")


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
    print("unscramble counts ...")
    mapping = load_mapping()
    return {unscramble(key, mapping): value for key, value in counts.items()}


if __name__ == "__main__":
    from main import *
    print("Starting Qbit Test")
    for i in range(16):
        test(i)
    print_mapping()
