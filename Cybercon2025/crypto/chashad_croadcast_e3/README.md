# Writeup – hashad_croadcast_e3

## Challenge Analysis
The file `public.txt` provides:
- Three RSA moduli \(n_1, n_2, n_3\), pairwise coprime.
- A common public exponent \(e = 3\).
- Three ciphertexts \(c_1, c_2, c_3\).

The challenge note says: **Classic Håstad Broadcast (e=3)**.  
This is the classic setting: if the same message \(m\) is encrypted with the same small exponent \(e=3\) under different moduli, then an attacker can recover the plaintext without needing the private key.


## Background Knowledge
RSA encryption:  
\[
c_i \equiv m^e \pmod{n_i}
\]

For \(i=1,2,3\), we have the system:  
\[
m^3 \equiv c_1 \pmod{n_1}, \quad m^3 \equiv c_2 \pmod{n_2}, \quad m^3 \equiv c_3 \pmod{n_3}
\]

If \(n_1,n_2,n_3\) are pairwise coprime, we can use the **Chinese Remainder Theorem (CRT)** to combine them into:  
\[
m^3 \equiv C \pmod{N}, \quad N = n_1 n_2 n_3
\]

As long as \(m^3 < N\) (true here since the flag is small compared to 3 × 1024‑bit moduli), then \(C = m^3\) holds as an integer, not just modulo.  
=> We can recover \(m\) by taking the integer cube root of \(C\).

---

## Special Observation
In the given data, we notice:
```
c1 == c2 == c3
```
This indicates that the generator chose very large primes, and since the flag is relatively small, computing \(m^3 \mod n_i\) never wrapped around.  
Thus:  
\[
c_1 = c_2 = c_3 = m^3
\]

=> The problem reduces to computing the integer cube root of a single value \(c\).

---

## Exploit
We use **integer cube root** via Newton’s method to compute \(m = \sqrt[3]{c}\).

### Solver
```python
from math import isclose

c = 249852220826328268464079521149028429732542389684864045421419630232819243189078213538649881453539435545506592859573314001551027168608367029227262514781078331946300046128367329461011963286878775900794308905136067987815473113124922565154424809354590715075511840615579243086815115150112954559875918789431663439644231541908947737781956329891053126380286330089104606816291055380135189392023982390677889987729120266373602221753706482268496731476961560543324585175800481622781866934794233049819311765651546138140895410674116216001113852568677

def icbrt(n: int) -> int:
    x = 1 << ((n.bit_length() + 2) // 3) 
    while True:
        y = (2*x + n // (x*x)) // 3
        if y >= x:
            return x
        x = y

m = icbrt(c)
assert m**3 == c

msg = m.to_bytes((m.bit_length()+7)//8, 'big')
print(msg.decode())
```


