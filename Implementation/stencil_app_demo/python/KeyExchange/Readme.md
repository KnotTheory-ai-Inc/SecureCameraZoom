# KeyExchange Module

> See [Developer Guide](../../Developer_Guide.md) for the full system overview.

---

## Purpose

This module handles **serialization and transmission of the Secret Key S** — the foundational layer for key exchange research.

It is a dedicated research space for investigating and implementing different key exchange protocols (e.g., pre-shared key, Diffie-Hellman, TLS-based exchange). Each protocol gets its own file here.

---

## Files

| File | Responsibility |
|---|---|
| `secret_key_serializer.py` | Serialize / deserialize `SecretKey` to bytes for transmission |

> **Pattern for future protocols:** each new key exchange protocol adds its own `<protocol>_exchange.py` here.  
> e.g. `dh_exchange.py` (Diffie-Hellman), `tls_exchange.py`, `oob_exchange.py` (out-of-band)

---

## `secret_key_serializer.py`

```python
def serialize_secret_key(key: SecretKey) -> bytes:
    """
    Serialize SecretKey to bytes for secure transmission.
    - Strategy: JSON-encode all fields, then base64-wrap the result.
    - crypto_key_K is included in the serialized form — ensure the transmission
      channel is secure (TLS, pre-shared channel, etc.).
    - Output: bytes.
    """

def deserialize_secret_key(data: bytes) -> SecretKey:
    """
    Inverse of serialize_secret_key().
    - Decodes base64, parses JSON, reconstructs SecretKey dataclass.
    - Output: SecretKey.
    """
```

---

## Research Direction

The `key_exchange()` call in `stencil_app/key_exchange.py` is a placeholder — the mechanism for **securely transmitting the serialized SecretKey** to the receiver is an open research question:

| Protocol | File (future) | Notes |
|---|---|---|
| Pre-shared key (manual) | — | Baseline — both parties agree on key out-of-band |
| Diffie-Hellman | `dh_exchange.py` | Establish shared secret over insecure channel |
| TLS channel | `tls_exchange.py` | Piggyback key on existing TLS session |
| Out-of-band (QR / NFC) | `oob_exchange.py` | Physical or side-channel delivery |

---

> For how serialization is used in the application layer, see [stencil_app/key_exchange.py](../../../stencil_app/Readme.md#key_exchangepy--key-exchange-demo).  
> `SecretKey` data structure → [common/Readme.md](../common/Readme.md)
