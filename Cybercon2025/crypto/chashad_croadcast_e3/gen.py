#!/usr/bin/env python3
import os, secrets, json

def bytes_to_long(b: bytes) -> int:
    return int.from_bytes(b, "big", signed=False)

def egcd(a, b):
    if b == 0:
        return (1, 0, a)
    x, y, g = 0, 1, b
    u, v, w = 1, 0, a
    while g != 0:
        q = w // g
        w, g = g, w - q*g
        u, x = x, u - q*x
        v, y = y, v - q*y
    return (u, v, w)

def invmod(a, m):
    a %= m
    x, y, g = egcd(a, m)
    if g != 1:
        raise ValueError("inverse does not exist")
    return x % m

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def is_probable_prime(n: int, rounds: int = 48) -> bool:
    if n < 2:
        return False
    small_primes = [2,3,5,7,11,13,17,19,23,29,31,37]
    for p in small_primes:
        if n % p == 0:
            return n == p
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for _ in range(rounds):
        a = secrets.randbelow(n-3) + 2
        x = pow(a, d, n)
        if x == 1 or x == n-1:
            continue
        skip = False
        for __ in range(s-1):
            x = pow(x, 2, n)
            if x == n-1:
                skip = True
                break
        if skip:
            continue
        return False
    return True

def gen_prime(bits: int, require_p_mod3_eq2: bool = False) -> int:
    assert bits >= 64
    while True:
        candidate = (1 << (bits - 1)) | secrets.randbits(bits - 1) | 1
        if require_p_mod3_eq2 and (candidate % 3) != 2:
            continue
        if is_probable_prime(candidate):
            return candidate

def gen_rsa_modulus(bits_each_prime: int, e: int):
    while True:
        p = gen_prime(bits_each_prime, require_p_mod3_eq2=(e==3))
        q = gen_prime(bits_each_prime, require_p_mod3_eq2=(e==3))
        if p == q:
            continue
        phi = (p-1)*(q-1)
        if gcd(e, phi) == 1:
            return p, q, p*q

def main():
    BASE = os.path.dirname(__file__)
    HANDOUT = os.path.join(BASE, "handout")
    ORGANIZER = os.path.join(BASE, "organizer")
    os.makedirs(HANDOUT, exist_ok=True)
    os.makedirs(ORGANIZER, exist_ok=True)

    e = 3
    bits_each = 1024
    FLAG = os.environ.get("FLAG", "cybercon{SNIP}").encode()

    p1,q1,n1 = gen_rsa_modulus(bits_each, e)
    p2,q2,n2 = gen_rsa_modulus(bits_each, e)
    p3,q3,n3 = gen_rsa_modulus(bits_each, e)

    assert gcd(n1, n2) == 1 and gcd(n1, n3) == 1 and gcd(n2, n3) == 1
    m = bytes_to_long(FLAG)
    c1 = pow(m, e, n1)
    c2 = pow(m, e, n2)
    c3 = pow(m, e, n3)

    Nprod = n1*n2*n3
    assert m**e < Nprod, "m^e must be < n1*n2*n3"

    with open(os.path.join(HANDOUT, "public.txt"), "w") as f:
        f.write("# Classic Håstad Broadcast (e=3)\n# Recover the flag string.\n")
        f.write(f"e = {e}\n")
        f.write(f"n1 = {n1}\n")
        f.write(f"n2 = {n2}\n")
        f.write(f"n3 = {n3}\n")
        f.write(f"c1 = {c1}\n")
        f.write(f"c2 = {c2}\n")
        f.write(f"c3 = {c3}\n")

    private = {
        "e": e,
        "p1": p1, "q1": q1, "n1": n1,
        "p2": p2, "q2": q2, "n2": n2,
        "p3": p3, "q3": q3, "n3": n3,
        "flag_str": FLAG.decode(),
        "flag_int": int.from_bytes(FLAG, "big"),
        "c1": c1, "c2": c2, "c3": c3
    }
    with open(os.path.join(ORGANIZER, "private.json"), "w") as f:
        json.dump(private, f, indent=2)

    print("Generated handout/public.txt and organizer/private.json")

if __name__ == "__main__":
    main()
