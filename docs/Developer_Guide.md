# SecureCameraZoom — Developer Guide

> **For the conceptual algorithm walkthrough and examples, see [Readme.md](Readme.md).**  
> This guide defines file structuring and the links to abstract function definitions.

---

## System Overview

A two-level cryptographic system:
1. **Level 1 – Crypto:** Plaintext → encrypted with a existing encryption scheme (AES or MHKC) → ciphertext
2. **Level 2 – Steganography:** Ciphertext chars are embedded at stencil-defined positions inside a large random character grid

Decryption reverses this: extract chars from the grid using the stencil key → decrypt.

---

## Two Implementation Modes

Both modes share all modules **except** the extraction step.

| | **Mode A: Byte Stream** | **Mode B: OCR (Camera)** |
|---|---|---|
| Grid format | `byte[]` / `char[][]` in memory | Printed paper or displayed image |
| Grid delivery | Grid bytes arrive directly over the network | Camera scans image → OCR reconstructs grid bytes |
| Use case | Network communication | Air-gapped / paper-based systems / Image transfer systems |

* Note:  Both modes pass the grid bytes to `stencil_lib`, which extracts ciphertext from stencil positions (Level 2) then runs cipher decryption (Level 1)
---

## Folder Structure

```
src/python/                            # modules/units to build a library
  common/
    constants.py                       # general constants
    classes.py                         # Abstract class and other common class types
  Encryption/
    cipher_encrypt.py                  # Level 1: Run chosen algo: cipher_encrypt(plaintext, cfg)
    steganography_encrypt.py           # Level 2: Grid generation and ciphertext embedding (TODO)
  Keygen/
    # future: stencil_keygen.py
  Decryption/
    cipher_decrypt.py                  # Level 1: Run chosen algo: cipher_decrypt(ciphertext, cfg)
    steganography_decrypt.py           # Level 2: Byte-stream grid extraction and ciphertext

stencil_system/python/               # Application layer — orchestration of entire crypto system
  stencil_system.ipynb                    # Demo: end-to-end walkthrough notebook
  CommunicationProtocol/               # To be done
  KeyExchange/                         # To be done

test/
  unit-tests/
    Encryption/
      test_cipher_encrypt.py
    Decryption/
      test_cipher_decrypt.py
    Keygen/                            # (empty — tests to be added)
    KeyExchange/                       # (empty — tests to be added)
    CommunicationProtocol/             # (empty — tests to be added)
  integration-tests/
    test_circle.py
```

## Modules description

- Classes and data structures: [src/python/common/Readme.md](src/python/common/Readme.md)
- Encryption modules: [src/python/Encryption/Readme.md](src/python/Encryption/Readme.md)
- Decryption modules: [src/python/Decryption/Readme.md](src/python/Decryption/Readme.md)
- Key generation: [src/python/Keygen/Readme.md](src/python/Keygen/Readme.md) — one file per cipher, shared stencil keygen
- Key exchange: [src/python/KeyExchange/Readme.md](src/python/KeyExchange/Readme.md) — serialization + protocol research
- Communication protocol: [src/python/CommunicationProtocol/Readme.md](src/python/CommunicationProtocol/Readme.md) — grid transmission research
- Application layer: [stencil_app_demo/Readme.md](stencil_app_demo/Readme.md)

---



