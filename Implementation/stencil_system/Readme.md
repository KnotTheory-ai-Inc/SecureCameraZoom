# stencil_app — Application Layer

> See [Developer Guide](../Developer_Guide.md) for the full system overview.

---

## Purpose

This utility folder contains the **application-level orchestration** of the SecureCameraZoom cryptographic scheme.

This folder manifests/demonstrates the final steganographic based cybersecurity application using the cryptographic algorithms implemented in `src/` folder.

### Dependency on `src/`

`stencil_app` depends on the `securecamerazoom` library built from `src/`.  
Run `inv build` from `Implementation/` before running anything in `stencil_app/`.

---

## Files

| File | Responsibility |
|---|---|
| `python/sender.py` | Full sender flow: generate key → Level 1 encrypt → build grid → embed → transmit |
| `python/receiver.py` | Full receiver flow: receive bytestream → reconstruct grid → extract → Level 1 decrypt |
| `python/key_exchange.py` | Demo: serialization + secure transmission of SecretKey S (TODO: key exchange protocol) |
| `python/communication_protocol.py` | Demo: grid bytestream transmission + reception (TODO: transport mechanism) |

---

## `sender.py` — Sender Flow Demo

Pseudo code for Encryption + Transmission

```python
# Step 1: Key generation
key_K = generate_aes_key(AES_256_KEY_SIZE)              # derive AES key (HKDF + os.urandom)
stencil_coords = generate_stencil_coords(len(ciphertext), rows=r, cols=c)
sigma = generate_permutation(len(ciphertext))           # random permutation σ
secret_key = generate_secret_key(
    stencil_coords=stencil_coords,
    partition=[1, 1, 3],
    permutation=sigma,
    reading_order="top-bottom-left-right",
    crypto_key_K=key_K
)

# Step 2: Level 1 encryption
ciphertext = cipher_encrypt(b"HELLO", key_K)            # plaintext as bytes → ciphertext bytes

# Step 3: Build grid and embed using Secret Key S
grid = generate_random_grid(rows=r, cols=c)
grid = steganography_encrypt(grid, ciphertext, secret_key)

# Step 4: Convert to bytestream
byte_stream = grid_to_bytestream(grid)

```
## `key_exchange.py` — Key Exchange Demo

Isolated demo for securely transmitting `SecretKey S` to the receiver.

```python
# Serialize SecretKey S for transmission
serialized = serialize_secret_key(secret_key)           # JSON + base64 encoded bytes

# TODO: Key exchange protocol to be investigated
# Options: TLS channel, Diffie-Hellman pre-shared key, out-of-band delivery
key_exchange(serialized)
```
 
> For protocol research, see [src/python/KeyExchange/Readme.md](../src/python/KeyExchange/Readme.md).

---

## `communication_protocol.py` — Communication Protocol Demo

Isolated demo for transmitting and receiving the grid bytestream.

```python
# Sender side
transmit(byte_stream)                                   # send grid to receiver (Mode A)

# Receiver side
bytestream = receive_bytestream()                       # receive grid from sender
rows, cols = get_grid_sizeensions()                      # agree on grid dimensions
```

> For protocol related implementations, see [src/python/CommunicationProtocol/Readme.md](../src/python/CommunicationProtocol/Readme.md).

---

## `receiver.py` — Receiver Flow Demo

Pseudo code for Decryption + Extraction

```python
# Step 1: Receive grid as bytestream
bytestream = receive_bytestream()                       # see communication_protocol.py

# Step 2: Reconstruct grid
rows, cols = get_grid_sizeensions()                      # see communication_protocol.py
grid = bytestream_to_grid(bytestream, rows, cols)

# Step 3: Secret Key S (received securely)
secret_key = deserialize_secret_key(received_secret_key)

# Step 4: Extract ciphertext from grid
ciphertext = steganography_decrypt(grid, secret_key)

# Step 5: Level 1 decryption
plaintext = cipher_decrypt(ciphertext, secret_key.crypto_key_K)
```

---

> For the full phased Roadmap, see [Implementation_roadmap.md](../Implementation_roadmap.md).
