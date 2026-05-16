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

Per the paper (§3): *"The encrypted text is split among the stencils and permuted, attaining enough permutation to be indistinguishable from surrounding random letters."*  σ is the permutation of ciphertext bytes placed into stencil positions.

Quick summary (per paper §3 — order matters):

**Step 1 — Generate coords from partition:** `partition[i]` defines the size of stencil group `i`. For each group, `partition[i]` random grid positions are chosen → these become that group's slice of `stencil_coords`. So `stencil_coords` is a flat list of all positions, implicitly grouped by `partition`.

**Step 2 — Place ciphertext into stencil coords:** ciphertext bytes are assigned to the `stencil_coords` slots. Each slot `i` in the grid gets one ciphertext byte.

**Step 3 — Permute while placing:** σ scrambles *which* ciphertext byte goes into each slot as bytes are being placed onto the grid. `σ[i] = j` → `ciphertext[j]` is written at `stencil_coords[i]`. The surrounding cells are filled with random noise, so the placed bytes are indistinguishable from filler.

- `n = sum(partition) = len(stencil_coords)` — total ciphertext bytes (= `lmax` in the paper)
- `generate_permutation(n)` → σ, a random shuffle of ciphertext byte indices `[0..n-1]`
- `σ[i] = j` means: after splitting, place `ciphertext[j]` at `stencil_coords[i]`
- Store σ in `SecretKey.permutation`
- Sender uses σ when calling `steganography_encrypt()`
- Receiver reconstructs: `ciphertext[σ[i]] = extracted[i]` (no inverse needed — σ is the direct index map)
- For no scrambling, pass `list(range(n))` as σ (identity permutation)

See [common/Readme.md](../common/Readme.md) for the full `SecretKey` data structure definition.

---

> For key derivation rationale (why HKDF + os.urandom over random.randbytes), see [Developer Guide](../../Developer_Guide.md).  
> For how these functions are called in the full system:
> - Key generation → [stencil_app/python/sender.py](../../../stencil_app/Readme.md#senderpy--sender-flow)
> - `SecretKey` data structure → [common/Readme.md](../common/Readme.md)
