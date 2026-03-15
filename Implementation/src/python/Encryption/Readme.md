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

## Sender Flow

Pseudo code for Encryption + Transmission

```python

# Step 1: Level 1 encryption
key_K = generate_aes_key()                              # 32-byte AES-256 key
ciphertext = cipher_encrypt(b"HELLO", key_K)            # plaintext as bytes → ciphertext bytes

# Step 2: Generate Secret Key S
stencil_coords = generate_stencil_coords(len(ciphertext), rows=r, cols=c)
sigma = generate_permutation(len(ciphertext)) # random permutations σ  
secret_key = generate_secret_key(
    stencil_coords=stencil_coords,
    partition=[1, 1, 3],
    permutation=sigma,
    reading_order="top-bottom-left-right",
    crypto_key_K=key_K
)

# Step 3: Build grid and embed using Secret Key S
grid = generate_random_grid(rows=r, cols=c)
grid = embed_ciphertext(grid, ciphertext, secret_key)

# Step 4: Transmit
# send grid to receiver as bytestream(Mode A)
byte_stream = grid_to_bytestream(grid)
# secure way of key exchange: TODO: Key exchange Protocol (or) secure key transmission to be investigated
key_exchange(serialize_secret_key(secret_key))
```
