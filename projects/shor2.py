import random
from fractions import Fraction

def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

def lcm(a, b):
    return int((a*b) / gcd(a, b))

def isPrime(p):
    return (p > 1) and all(f == p for f,e in factored(p))

def mult_order(x, n):
    if gcd(x, n) == 1:
        z = x%n
        c = 1
        while 1 != z:
            c += 1
            z = (x*z)%n
        return c

def get_random_ratio_estimate(a, x, n):
    r = mult_order(a, x)
    if r:
        k = random.randint(0, r-1)
        v = k/r
        l = int(v*2**n)
        h = l+1
        if abs(v-l/2**n) < abs(v-h/2**n):
            return l/2**n, r
        else:
            return h/2**n, r
    return None, r

def is_atotheb(n):
    if n == 1:
        return True

    for x in range(2, int(n**.5+1)):
        y = 2
        p = x**y

        while p <= n and p > 0:
            if p == n:
                return True
            y = y + 1
            p = x**y
    return False

def shor_algorithm(N, qubits=8):
    print("SHOR started: N=%d calculating factors...\n"%N)

    if N%2 == 0:
        print("even number")
        return 2, N/2

    terminate = False
    while not terminate:
        a = random.randint(1, N-1)
        print("Choosing a=%d"%a)

        n = qubits
        p1, rr = get_random_ratio_estimate(a, N, n)
        p2, rr = get_random_ratio_estimate(a, N, n)

        if p1!=None and p2!=None:
            r1 = Fraction(p1).limit_denominator(int(N**0.5))
            r2 = Fraction(p2).limit_denominator(int(N**0.5))
            print("Phases: %d/%d, %d/%d" % (r1.numerator, r1.denominator, r2.numerator,
                r2.denominator))
            r1 = r1.denominator
            r2 = r2.denominator
            r = lcm(r1, r2)
            print("Order: %d (actual %d)" % (r, rr))
            if r%2 == 0:
                if pow(a, int(r/2), N) != N-1:
                    fa, fb = gcd(N, pow(a, int(r/2), N)-1), gcd(N, pow(a, int(r/2), N)+1)
                    if fa*fb == N:
                        terminate = True
                    else:
                        print("\nFAILED!\twrong order found, retry...\n")
                else:
                    print("\nFAILED!\t-1modN, retry...\n")
            else:
                print("\nFAILED!\todd order, retry...\n")
                continue
        else:
            fa = gcd(a, N)
            fb = int(N/fa)
            terminate = True
    print("\nSUCCESS! %d = %d x %d\n"%(fa*fb, *list(sorted([fa, fb]))))
    return fa, fb


shor_algorithm(11*31)
