"""
Diffie-Hellmann

Algorithm for Key Exchange

Code is created following the tutorial on:
https://www.codeproject.com/articles/70330/implementation-of-diffie-hellman-algorithm-of-key
"""
import random
from fractions import gcd
from math import sqrt

# Prime Testing Functions
def IsPrime(n):
    if n == 1:
        return False
    if n == 2:
        return True
    for i in range(2, n-1):
        if n % i == 0: # divideable by i?
            return False # no prime
    return True
def IsPrime2(n):
    for entry in SievePrimes:
        if n % entry == 0:
            return False
        if entry >= n:
            break
    return True
def Fermat(n):
    if n == 2:
        return True
    if not n & 1:
        return False
    return pow(2, n-1, n) == 1
def SievePrime(upto):
    arr, bool_arr = list(), list()
    for i in range(2, upto):
        arr.append(i)
        bool_arr.append(True)
    for scope in range(0, int(sqrt(upto))):
        if bool_arr[scope]:
            divisor = arr[scope]
            for i in range(1+scope, len(arr)):
                if arr[i] % divisor == 0:
                    bool_arr[i] = False
    res = list()
    for i in range(len(arr)):
        if bool_arr[i]:
            res.append(arr[i])
    return res

# Prime Generators
def NextPrime(n, check=Fermat):
    for i in range(n+1, int(n+(n//1024)), 1):
        test = check(i)
        if test: return i
    emsg = "No next prime in given number range found (" + str(n) + " to " + str(n+n) + ")"
    raise Exception(emsg)
def NextPrime_while(n, check=Fermat):
    maybeprime = n+1
    while not check(maybeprime):
        maybeprime += 1
    return maybeprime
def NextSafePrime(n, check=Fermat):
    prime = NextPrime_while(n, check=check)
    safe = check((prime-1)//2)
    while not safe:
        prime = NextPrime(prime, check=check)
        safe = check((prime-1)//2) #  Prime is safe, if prime-1/2 is also prime
    return prime
def NextSchnorrPrime(n, check=Fermat):
    prime_q = NextPrime_while(n, check)
    for k in range(1, n):
        prime_p = (k * prime_q) + 1
        if check(prime_p):
            return prime_q, prime_p
    return None

# Factorization Functions
def findFirstDivisor(n):
    for i in range(2, n+1):
        if n % i == 0:
            return i
def factorization(n):
    divisors = list()
    number = n
    while number != 1:
        print(number, end="")
        q = findFirstDivisor(number)
        print(" /", q, end="")
        divisors.append(q)
        number = int(number/q)
        print(" =", number)
    return divisors

# Prime list generator
def GeneratePrimeRange(first, last, check=IsPrime):
    res = []
    for i in range(first, last):
        if check(i):
            res.append(i)
    return res
# Time measurement for exec Functions
def TakeTime(func, *arg):
    import time
    s = time.time()
    retval = func(*arg)
    dif = time.time()-s
    print("Called", func, "in", dif, "Seconds")
    return retval
# Provides a Generator G
def GetGenerator(q, p):
    def insecurityTest(g, p, q):
        exp = (p-1)//q
        number = g**exp % p
        return number != 1 # True is secure
    secure = False
    g_test = 2
    while not secure:
        g_test = random.randint(2, p-1)
        secure = insecurityTest(g_test, p, q)
        if secure:            
            return g_test
        else:
            if g_test < p-1:
                g_test += 1
            else:
                return None

def DiffieHellman(KeySize=2**10):
    # Runtime Values
    PrimeSize = (2**KeySize)
    PrimeSize += random.randint(0, 2**(KeySize/4))
    PrimeSize = random.getrandbits(KeySize)
    PrimePrecision = 10**4
    PrimeCheck = Fermat # IsPrime, IsPrime2, Fermat

    # get a list of Sieve Primes for further Prime number generation
    SievePrimes = SievePrime(PrimePrecision) if PrimeCheck is IsPrime2 else None
    print("(Primes loaded)")

    # Steps for successful Diffie-Hellman
    # I.    Generate large Prime P
    #       Function: NextPrime(n)
    Q, P = NextSchnorrPrime(PrimeSize, PrimeCheck)
    G = GetGenerator(Q, P)
    print("P:\n", P)
    print("G:\n", G)
    # II.   Generate random big numbers as "private Keys"
    #       The Numbers are:
    #           Xa  -   Alice's Private Key
    #           Xb  -   Bob's Private Key
    Xa = random.getrandbits(KeySize)
    Xb = random.getrandbits(KeySize)
    print("Xa:\n", Xa)
    print("Xb:\n", Xb)
    # III.  Generate a one way Public Key from Private Key
    #           Ya  -   Alice's Public Key
    #           Yb  -   Bob's Private Key
    Ya = pow(G, Xa, P)
    Yb = pow(G, Xb, P)
    print("Ya:\n", Ya)
    print("Yb:\n", Yb)
    # IV.   Calculate the real Key (encryption Key)
    Ka = pow(Yb, Xa, P)
    Kb = pow(Ya, Xb, P)
    print("Ka:\n", Ka)
    print("Kb:\n", Kb)
    print("Ident?:", Ka == Kb)

if __name__ == '__main__':
    TakeTime(DiffieHellman, 2**11)
