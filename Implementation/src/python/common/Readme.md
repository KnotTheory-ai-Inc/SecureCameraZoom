# Common — Shared Data Structures

> These classes could be shared across both `Encryption` and `Decryption` modules.  

---

## File

| File | Responsibility |
|---|---|
| `classes.py` | `SecretKey` and `Grid` dataclasses |

---

## `SecretKey`

SecretKey class to store the stencil data and the crypto key data

```python

@dataclass
class SecretKey:

    # Example: [(2,3), (3,3), (4,3), (4,4), (4,5)] for a 5-char ciphertext.
    stencil_coords : List[Tuple[int, int]]

    # Example: [1, 1, 3] means split cipher text to 3 partitions of lengths 1,1,3.
    partition : List[int]

    # σ — permutes cipher text
    # Example:
    #   ciphertext = bytes([0xAF, 0x3C, 0x72, 0x1E, 0xB5])
    #   If σ = [3, 0, 4, 1, 2]
    #   permuted_cipher_text = bytes([0x1E, 0xAF, 0xB5, 0x3C, 0x72])
    permutation : List[int]
    
    # Default scan direction used when extracting chars from the grid.
    # Example: "top-bottom-left-right" # TODO: Revisit the idea here during implementation
    reading_order : str

    # AES-256 key (32 bytes) used for Level 1 encryption/decryption.
    crypto_key_K : bytes
    
```

## `Grid`

Represents the obscuring Grid that hides the ciphertext among random characters.

```python
@dataclass
class Grid:
    # 2D byte Grid: data[row][col]
    # Each row is a bytearray of length `cols`.
    data : List[bytearray]

    # Grid size
    rows : int
    cols : int
```
