# SecureCameraZoom — Developer Guide

> **For the conceptual algorithm walkthrough and examples, see [Readme.md](Readme.md).**  
> This guide defines file structuring and the abstract function definitions.

---

## System Overview

A two-level cryptographic system:
1. **Level 1 – Crypto:** Plaintext → encrypted with AES-256 (or MHKC) → ciphertext
2. **Level 2 – Steganography:** Ciphertext chars are embedded at stencil-defined positions inside a large random character grid

Decryption reverses this: extract chars from the grid using the stencil key → decrypt.

---

## Two Implementation Modes

Both modes share all modules **except** the extraction step.

| | **Mode A: Byte Stream** | **Mode B: OCR (Camera)** |
|---|---|---|
| Grid format | `byte[]` / `char[][]` in memory | Printed paper or displayed image |
| Extraction | `grid[row * cols + col]` — direct array indexing | Camera zoom + OCR per coordinate |
| Use case | Network communication | Air-gapped / paper-based systems / Image transfer systems |

---

## Folder Structure

```
src/
  common/
    classes.py                 # dataclasses for encrypt and decrypt
    .
    .
  Encryption/
    cipher_encrypt.py          # Level 1: AES/MHKC encryption
    steganography_encrypt.py   # Level 2: Grid generation and ciphertext embedding
    .
    .
  keygen/
    keygen.py                  # SecretKey generation
    .
    .
  Decryption/
    extract_bytes.py           # Mode A: byte-stream extraction
    decrypt.py                 # Full decryption pipeline
    .
    .
test/
  Encryption/
    test_cipher_encrypt.py
    test_steganography_encrypt.py
    .
    .
  keygen/
    test_keygen.py
    .
    .
  Decryption/
    test_extract_bytes.py
    test_decrypt.py
    .
    .
```

## Modules description

- Classes and data structures [src/common/Readme.md](src/common/Readme.md)
- Encryption modules [src/Encryption/Readme.md](src/Encryption/Readme.md) 

---



