# Keygen Module

> See [Developer Guide](../../Developer_Guide.md) for the full system overview.

---

## Files

| File | Responsibility |
|---|---|
| `stencil_keygen.py` | Stencil coordinate generation, permutation generation, `SecretKey` assembly |

> **Pattern for Key material:** for each new cipher (Caesar, Vigenère, etc.) user will provide encrypt impl, decrypt impl and parameters. `stencil_keygen.py` will generate key for steganographic crypto system.


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
