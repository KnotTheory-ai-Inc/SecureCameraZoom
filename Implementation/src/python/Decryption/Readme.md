# Decryption Module

> Part of the SecureCameraZoom two-level crypto system.  
> See [Developer Guide](../../Developer_Guide.md) for the full system overview.

---

## Files

| File | Responsibility |
|---|---|
| `steganography_decrypt.py` | Level 1: Grid extraction and ciphertext recovery |
| `cipher_decrypt.py` | Level 2: AES/MHKC decryption |

---

## `steganography_decrypt.py`

```python

def bytestream_to_grid(bytestream: bytes, rows: int, cols: int) -> Grid:
    """
    Convert a byte stream back into a 2D grid.
    - Input: bytestream (bytes), rows (int), cols (int)
    - Output: Grid dataclass instance.
    """

def extract_ciphertext(grid: Grid, secret_key: SecretKey) -> bytes:
    """
    Extract ciphertext bytes from the grid using Secret Key S.
    - Input: grid (Grid), secret_key (SecretKey)
    - Output: ciphertext bytes recovered from grid based on SecretKey.
    """
```

---

## `cipher_decrypt.py`

```python
def cipher_decrypt(ciphertext: bytes, key_K: bytes) -> bytes:
    """
    Decrypt ciphertext using AES or MHKC.
    - Input: ciphertext (bytes), key_K (bytes)
    - Output: plaintext as bytes
    """
```

---
## Receiver Flow

Pseudo code for Decryption + Extraction

```python
# Step 1: Receive grid as bytestream
bytestream = receive_bytestream()

# Step 2: Reconstruct grid
rows, cols = get_grid_dimensions()
grid = bytestream_to_grid(bytestream, rows, cols)

# Step 3: Secret Key S (received securely)
secret_key = deserialize_secret_key(received_secret_key)

# Step 4: Extract ciphertext from grid
ciphertext = extract_ciphertext(grid, secret_key)

# Step 5: Level 2 decryption
plaintext = cipher_decrypt(ciphertext, secret_key.crypto_key_K)
```