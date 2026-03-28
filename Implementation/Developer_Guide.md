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
| Extraction | `grid[row * cols + col]` — direct array indexing | Camera zoom + OCR per coordinate |
| Use case | Network communication | Air-gapped / paper-based systems / Image transfer systems |

---

## Folder Structure

```
src/python/                            # modules/units to build a library
  common/
    constants.py                       # general constants
    classes.py                         # Grid + SecretKey dataclasses
  Encryption/
    cipher_encrypt.py                  # Level 1: Existing encryption schemes
    steganography_encrypt.py           # Level 2: Grid generation and ciphertext embedding
  Keygen/
    aes_keygen.py                      # AES key derivation (HKDF + os.urandom)
    stencil_keygen.py                  # stencil coord generation, permutation, SecretKey assembly
    # future: caesar_keygen.py, vigenere_keygen.py, ...
  Decryption/
    cipher_decrypt.py                  # Level 1: Existing decryption schemes
    steganography_decrypt.py           # Level 2: Byte-stream grid extraction and ciphertext recovery
  KeyExchange/
    secret_key_serializer.py           # serialize/deserialize SecretKey for transmission
    # future: dh_exchange.py, tls_exchange.py, oob_exchange.py, ...
  CommunicationProtocol/
    bytestream_protocol.py             # Mode A: transmit/receive grid as raw bytestream
    # future: ocr_protocol.py (Mode B), fax_protocol.py, qr_protocol.py, ...

stencil_app/python/                    # Application layer — orchestration only
  sender.py                            # Demo: Full sender flow: keygen + encrypt → embed → transmit
  receiver.py                          # Demo: Full receiver flow: receive → extract → decrypt
  key_exchange.py                      # Demo: SecretKey serialization + transmission (TODO: key exchange protocol)
  communication_protocol.py            # Demo: grid bytestream transmit/receive (TODO: transport mechanism)

test/
  unit-tests/
    Encryption/
      test_cipher_encrypt.py
      test_steganography_encrypt.py
    Decryption/
      test_cipher_decrypt.py
      test_steganography_decrypt.py
    Keygen/
      test_keygen.py
    KeyExchange/
      test_key_exchange.py
    CommunicationProtocol/
      test_bytestream_protocol.py
  integration-tests/
    test_circle.py
    test_full_pipeline.py
```

## Modules description

- Classes and data structures: [src/python/common/Readme.md](src/python/common/Readme.md)
- Encryption modules: [src/python/Encryption/Readme.md](src/python/Encryption/Readme.md)
- Decryption modules: [src/python/Decryption/Readme.md](src/python/Decryption/Readme.md)
- Key generation: [src/python/Keygen/Readme.md](src/python/Keygen/Readme.md) — one file per cipher, shared stencil keygen
- Key exchange: [src/python/KeyExchange/Readme.md](src/python/KeyExchange/Readme.md) — serialization + protocol research
- Communication protocol: [src/python/CommunicationProtocol/Readme.md](src/python/CommunicationProtocol/Readme.md) — grid transmission research
- Application layer: [stencil_app/Readme.md](stencil_app/Readme.md)

---



