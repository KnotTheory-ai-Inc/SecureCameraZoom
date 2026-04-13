# Encryption Module

> See [Developer Guide](../../Developer_Guide.md) for the full system overview.

---

## Files

| File | Responsibility |
|---|---|
| `cipher_encrypt.py` | Level 1: AES/MHKC encryption & decryption |
| `steganography_encrypt.py` | Level 2: Grid generation and ciphertext embedding |

---

## `cipher_encrypt.py`

```python
def cipher_encrypt(plaintext: bytes, key_K: bytes) -> bytes:
    """
    Encrypt plaintext using AES or MHKC.
    - Input: plaintext (bytes, e.g. b"HELLO"), key_K (bytes)
    - Output: ciphertext as bytes
    """
```

---

## `steganography_encrypt.py`

```python
def generate_random_grid(rows: int, cols: int) -> Grid:
    """
    Fill a rows×cols grid with random byte values.
    - Input: rows (int), cols (int)
    - Output: Grid dataclass instance
    """

def embed_ciphertext(grid: Grid, ciphertext: str, secret_key: SecretKey) -> Grid:
    """
    Place each char of ciphertext into the grid using the Secret Key S from the paper.
    - Input: Grid, ciphertext (str), secret_key (SecretKey)
    - Output: modified Grid (rand bytes in Grid replaced with ciphertext bytes based on SecretKey).
    - Note: Grid size shall remain same
    """

def grid_to_bytestream(grid: Grid) -> bytes:
    """
    Flatten the 2D grid into a byte stream for transmission.
    - Input: grid (Grid, ciphertext-embedded)
    - Output: bytes object.
    - Implementation: b''.join(grid.data)  — each row is already a bytearray.
    - Note: Equivalent byte index: grid.data[row][col] == bytestream[row * cols + col]
    """
```

---

> For the full Sender Flow (how these functions are orchestrated end-to-end), see [stencil_app/Readme.md](../../../stencil_app/Readme.md).
