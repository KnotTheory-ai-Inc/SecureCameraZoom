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

def extract_ciphertext(grid: Grid, secret_key: SecretKey) -> bytes:
    """
    Extract ciphertext bytes from the grid using Secret Key S.
    - Input: grid (Grid), secret_key (SecretKey)
    - Output: ciphertext bytes recovered from grid based on SecretKey.
    """
```


> For the full Receiver Flow (how these functions are orchestrated end-to-end), see [stencil_app/Readme.md](../../../stencil_app/Readme.md).