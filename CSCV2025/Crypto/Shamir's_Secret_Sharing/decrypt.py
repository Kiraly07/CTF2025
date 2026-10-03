import base64
from Crypto.Cipher import AES

# AES key from previous step
key = b'thresh0ld_k3y_05'

# Read vault file
with open('ctf/ctf/final/vault.enc', 'r') as f:
    vault_data = f.read().strip()

decoded = base64.b64decode(vault_data)
iv = decoded[:16]
ciphertext = decoded[16:]

# Decrypt using AES-128-CBC
cipher = AES.new(key, AES.MODE_CBC, iv)
plaintext = cipher.decrypt(ciphertext)

# Remove null padding and decode
result = plaintext.rstrip(b'\x00').decode('ascii')
print(f"Flag: {result}")
