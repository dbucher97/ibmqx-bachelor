import random

def prep(qc, n, qr):
    s = "".join(reversed("{:b}".format(n)))
    for i in range(len(s)):
        if s[i] == "1":
            qc.x(qr[i])

def prep2(qc, n, qr, m):
    s = "{:b}".format(n)
    s = "0"*(m-len(s)) + s
    for i in range(m):
        if s[i] == "1":
            qc.x(qr[i])

def rand_prep(qc, qr):
    x = random.randint(0, 2**len(qr)-1)
    prep(qc, x, qr)
    return x

def max_count_to_int(counts):
    s = max(counts.items(), key=lambda x: x[1])[0]
    return int(s, 2)

def max_count_to_int2(counts, n):
    s = max(counts.items(), key=lambda x: x[1])[0]
    return int(s[-n:][::-1], 2)
