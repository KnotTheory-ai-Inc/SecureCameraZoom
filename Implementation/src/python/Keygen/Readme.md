# Keygen Module

> See [Developer Guide](../../Developer_Guide.md) for the full system overview.

---

## Files

| File | Responsibility |
|---|---|
| `stencil_keygen.py` | Stencil coordinate generation, permutation generation, `SecretKey` assembly |

> **Pattern for Key material:** for each new cipher (Caesar, Vigenère, etc.) user will provide encrypt impl, decrypt impl and parameters. `stencil_keygen.py` will generate key for steganographic crypto system.

---

## `stencil_keygen.py`

```python
def generate_stencil_coords(n: int,
                             rows: int,
                             cols: int,
                             existing_coords: List[Tuple[int, int]] = []
                             ) -> List[Tuple[int, int]]:
    """
    Randomly generate n unique (row, col) positions within grid bounds.
    - Use secrets/CSPRNG for position selection — do NOT use random.random().
    - Ensures no overlap with existing_coords (e.g. previously reserved cells).
    - Input: n (int) — number of ciphertext bytes to place,
             rows (int), cols (int) — grid dimensions,
             existing_coords — positions already occupied (default empty)
    - Output: list of n unique (row, col) tuples.
    - Raises ValueError if grid is too small to fit n unique positions.
    """

def generate_permutation(n: int) -> List[int]:
    """
    Generate a random permutation σ of length n using CSPRNG.
    - σ[i] = j means: place ciphertext[j] at stencil_coords[i].
    - Input: n (int) — length of ciphertext
    - Output: list of ints, a shuffle of [0, 1, ..., n-1].
    - Use secrets.SystemRandom().shuffle() or Fisher-Yates with secrets.
    - To get identity (no scrambling): return list(range(n)).
    """

def generate_secret_key(
    stencil_coords: List[Tuple[int, int]],
    partition: List[int],
    permutation: List[int],
    reading_order: str,
    crypto_key_K: bytes
) -> SecretKey:
    """
    Bundle all key material into a SecretKey struct.
    - partition   : e.g. [1, 1, 3] — sum must equal len(stencil_coords).
    - permutation : σ from generate_permutation(). Pass list(range(n)) for identity.
    - reading_order: default 'top-bottom-left-right' (only used when σ is identity).
    - crypto_key_K: AES key bytes — transmit separately from the grid.
    - Raises ValueError if sum(partition) != len(stencil_coords).
    """
```

> For SecretKey serialization and key exchange, see [KeyExchange/Readme.md](../KeyExchange/Readme.md).

---

## How permutation σ fits in

Quick summary:
- `generate_permutation(n)` → σ (random shuffle of `[0..n-1]`)
- σ[i] = j means: place `ciphertext[j]` at `stencil_coords[i]`
- Store σ in `SecretKey.permutation`
- Sender uses σ when calling `embed_ciphertext()`
- Receiver reconstructs: `ciphertext[σ[i]] = extracted[i]` (no inverse needed — σ is the direct index map)
- For no scrambling, pass `list(range(n))` as σ (identity permutation)

See [common/Readme.md](../common/Readme.md) for the full `SecretKey` data structure definition.

---

> For key derivation rationale (why HKDF + os.urandom over random.randbytes), see [Developer Guide](../../Developer_Guide.md).  
> For how these functions are called in the full system:
> - Key generation → [stencil_app/python/sender.py](../../../stencil_app/Readme.md#senderpy--sender-flow)
> - `SecretKey` data structure → [common/Readme.md](../common/Readme.md)
