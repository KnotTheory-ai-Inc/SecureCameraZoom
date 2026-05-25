# A stencil based crypto-scheme

## Table of Contents

1. [Introduction](#introduction)
2. [A detailed workflow example](#a-detailed-workflow-example)
3. [`stencil_lib` API Architecture](#stencil_lib-api-architecture)
4. [Installation and Usage](#installation-and-usage)
5. [Project Tooling Files](#project-tooling-files)
6. [Source Layout](#source-layout)
7. [Resources](#resources)

---

## Introduction

This project implements a **symmetric key encryption scheme** that combines a classical paper-pencil stencil cipher with a matrix-level cipher and camera zoom capabilities, as described in the research paper:

> *"A Camera Zoom-based Paper-Pencil Cipher Encryption Scheme atop Merkle-Hellman Knapsack Cryptosystem"*  
> Gopal Anantharaman, HP Inc., Palo Alto, CA, USA (June 12, 2024)

### How it works — two-level encryption

**Level 1 — Cipher encryption (`cipher_encrypt`):**

The plaintext is first encrypted with a conventional cipher to produce ciphertext bytes. The paper uses **MHKC** as its reference cipher, but the design is **cipher-agnostic** — any cipher (including relatively weak ones) can be plugged in here. The steganographic layer above provides independent security regardless of the strength of Level 1.

```
plaintext bytes  →  [Level 1: cipher_encrypt]  →  ciphertext bytes
```

**Level 2 — Steganographic encryption (`steganography_encrypt`):**

A random grid is generated and filled with pseudo-random noise bytes. The ciphertext bytes from Level 1 are then embedded at the stencil positions inside the grid. An optional permutation σ is applied to the ciphertext bytes before embedding.

```
ciphertext bytes  →  [permutation σ]  →  embedded into stencil positions in random grid
                                                            ↓
                                               obfuscated grid (transmitted)
```

The grid itself is **not encrypted** — the security comes from hiding the ciphertext among random noise and keeping the stencil positions secret.

**Decryption reverses both levels:**

```
obfuscated grid  →  [extract stencil positions]  →  [σ⁻¹]  →  ciphertext bytes
ciphertext bytes →  [Level 1: cipher_decrypt]   →  plaintext bytes
```

**Transmission:** The obfuscated grid is transmitted as a bytestream over a network or as a physical image read back by camera zoom + OCR.

### Security properties

- **Cipher-agnostic + layered obfuscation:** Any cipher can be used at Level 1 (MHKC is the paper's reference). Even if Level 1 is fully broken, the adversary only recovers a flat byte sequence — without the stencil subset $SR_l$, permutation σ, and partition $R_l$, the plaintext remains hidden.
- **IND-CPA reconciliation:** The random decoy fill and stencil randomisation make the ciphertext computationally indistinguishable from random noise.

### Secret key (`SecretKey`)

| Field | Description |
|-------|-------------|
| `stencils` | List of `Stencil` objects — the chosen stencil subset $SR_l$ |
| `partition_list` | Partition sizes $R_l$ (e.g. `[1, 1, 3]`) — how ciphertext bytes are split across stencils |
| `cipher_cfg` | `CipherConfig` subclass bundling the Level 1 cipher algorithm + key material |
| `cipher_permutation` | *(optional)* byte-index shuffle applied to ciphertext before stencil placement |
| `grid_permutation` | *(optional)* stencil-slot shuffle applied after natural ciphertext splitting |

### Stencil configuration (`StencilConfig`) — used by `keygen` to produce a `SecretKey`

| Field | Description |
|-------|-------------|
| `total_bytes` | Ciphertext length (bytes) |
| `num_partitions` | Number of stencil groups to generate |
| `grid_shape` | `GridShape` specifying grid dimensions |
| `enable_cipher_permutation` | If `True`, generate and apply `cipher_permutation` |
| `enable_grid_permutation` | If `True`, generate and apply `grid_permutation` |
| `enable_subdomain_partitioning` | If `True`, place stencils within defined grid subdomains |

![The Dataflow](docs/Paper-Pencil-Block-Diag.jpeg)

## A detailed workflow example

See [docs/Workflow_Example.md](docs/Workflow_Example.md) for a step-by-step walkthrough of the encryption and decryption process.

## `stencil_lib` API Architecture

See [docs/Stencil_System_Architecture.md](docs/Stencil_System_Architecture.md) for the architecture diagram.

---

## Installation and Usage

### 0. Clone the repo and navigate to project root

```bash
git clone <repo-url>
cd SecureCameraZoom
```

### 1. Create and activate a virtual environment (optional)

```bash
python -m venv .venv
```

Note: `venv` is built into Python 3.3+. Some Ubuntu/Debian systems may require `sudo apt install python3-venv`.

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

### 2. Install dependencies (one-time / when changed)

```bash
pip install -r requirements.txt
```

If `pip` is not on PATH:

```bash
python -m pip install -r requirements.txt
```

### 3. Build and run tests

```bash
inv build   # build .whl -> build/dist/
inv test    # run all tests (unit + integration + sw)
inv clean   # remove build output
```

Individual test targets: `inv test_unit`, `inv test_integration`, `inv test_sw`

---

## Project Tooling Files

### `pyproject.toml` - package definition

Defines project metadata and build backend.
For more details, see the [Python Packaging User Guide on pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/).

```
pyproject.toml
|-- [build-system]    (build backend, setuptools)
|-- [project]         (name, version, python version, dependencies)
`-- [tool.setuptools] (source package location: src/python)
```

### `tasks.py` - task runner (`inv` commands)

Defines custom CLI tasks using [`invoke`](https://www.pyinvoke.org/).

### `conftest.py` - pytest configuration

Auto-loaded by pytest. Locates wheel in `build/dist/*.whl` and installs it for tests.
For more details, see [pytest documentation on conftest.py](https://docs.pytest.org/en/stable/reference/fixtures.html#conftest-py).

---

## Source Layout

### `src/` — `stencil_lib` library

The `src/python/` directory contains the source code that is built into the `stencil_lib` Python package (installed as a `.whl` via `inv build`). It exposes the core cryptographic APIs:

```
src/python/
|-- stencil_lib.py        (public API surface — re-exports all key functions)
|-- common/               (shared data classes: CipherConfig, SecretKey, Grid, etc.)
|-- Encryption/           (cipher_encrypt, steganography_encrypt, encrypt orchestration)
|-- Decryption/           (cipher_decrypt, steganography_decrypt, decrypt orchestration)
`-- Keygen/               (keygen, stencil coordinate and permutation generation)
```

### `stencil_system/` — Proof-of-concept application (`stencil_system`)

`stencil_system` is a standalone proof-of-concept that demonstrates a full end-to-end cryptographic system built using `stencil_lib`. It is **not** part of the installable library; it depends on `stencil_lib` being built first (`inv build`).

```
stencil_system/
|-- python/
|   |-- stencil_system_MODE_A_Bytestream.ipynb   (end-to-end demo notebook)
|   |-- CommunicationProtocol/                   (bytestream grid transmission protocol)
|   `-- KeyExchange/                             (secret key serialization and exchange)
`-- Readme.md
```

The notebook `stencil_system_MODE_A_Bytestream.ipynb` walks through the full sender → receiver flow: key generation, encryption, steganographic embedding, bytestream transmission, extraction, and decryption.

---

## Resources

### Cryptography
1. https://www.geeksforgeeks.org/computer-networks/cryptography-tutorial/

### Git setup and usage
1. https://www.atlassian.com/git/tutorials/what-is-git
