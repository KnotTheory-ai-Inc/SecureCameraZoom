# Decryption Module

> Part of the SecureCameraZoom two-level crypto system.  
> See [Developer Guide](../../Developer_Guide.md) for the full system overview.

---

## Files

| File | Responsibility |
|---|---|
| `steganography_decrypt.py` | Level 1: Grid extraction and ciphertext recovery |
| `cipher_decrypt.py` | Level 2: User chosen decryption |



> For the full Receiver Flow (how these functions are orchestrated end-to-end), see [stencil_app/Readme.md](../../../stencil_app/Readme.md).