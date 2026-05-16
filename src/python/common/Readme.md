# Common — Shared Data Structures

> These types are shared across `Encryption`, `Decryption`, and `keygen` modules.  
> See [Developer Guide](../../Developer_Guide.md) for the full system overview.

---

## Files

| File | Responsibility |
|---|---|
| `constants.py` | AES key size and block size constants |
| `classes.py` | `SecretKey` and `Grid` dataclasses |

---

## `SecretKey`

SecretKey class to store the stencil data and other classes needed for crypto system.
