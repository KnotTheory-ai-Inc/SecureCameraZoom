# SecureCameraZoom

## The Overall Dataflow of the Paper-Pencil Crypto-scheme

![The Dataflow](Paper-Pencil-Block-Diag.jpeg)

## Detailed Workflow with an Example

### Step 1: Encrypt the Plaintext First (Level 1 encryption)

Using classical encryption schemes: MHKC/AES with crypto secret key K.

```
"HELLO" -> [Encryption] -> "Xk9mP"
```

### Step 2: Steganographic Encryption (Level 2 encryption)

Security through obscurity / grid hiding technique.

Fill a grid with random letters and hide encrypted text from Step 1:

```
X Q Z M P T R N S V B W K D F G C Y A I U E
K R X N A D M L P Q S Z T Z B F Y W C V G U  <- 'X' hidden here
F Y k W S C Q N B M K P R T Z A D V L G I H  <- 'k' hidden here
J U 9 m P I V N T Q R S W V X B A F D C H T  <- '9mP' hidden here
Z M K P N S T Q R W X B A D F C V Y G U E I
Q T W R S B N K M P L A X Z Y D F V G C H U
... (assume 100 more rows of random letters)
```

### Step 3: Generate Secret Key S

According to the paper, the secret key contains:

```
Secret Key S = {
	1. Stencil Set SRl (chosen shapes)
	2. Bijection function g (maps partitions to stencils)
	3. MHKC/AES crypto secret key K
	4. Permutation sigma
	5. Starting position
	...
}
```

For this example:

```
Secret Key S = {
	1. Stencil Set SRl = {"L-shape"}
	2. Starting_coordinates: {(2,3)}
	3. Partition: [1, 1, 3]  --> 'X', 'k', '9mP'
	4. Reading_order: "Top-to-bottom, left-to-right"
	5. MHKC/AES crypto secret key K
}
```

### Step 4: Transmission/Reception Channel - Communication Network

The grid can be transmitted as:
- Byte stream over network (byte-stream implementation)
- Physical paper through fax/OCR (OCR implementation)

### Step 5: Steganographic Decryption (Level 1 decryption)

Input:
1. Obscured grid
2. Receiver already has secret key S (stencil indices/coordinates + crypto key)

Camera zoom based OCR technique:

```
Camera uses those coordinates to zoom to specific grid positions
OCR reads characters at each position -> collects "Xk9mP"
```

Byte-stream implementation:
The grid is stored in memory and classical array/pointer mechanisms are used to recover ciphertext.

Output ciphertext:

```
"Xk9mP"
```

### Step 6: Decrypt the Ciphertext (Level 2 decryption)

Using classical decryption schemes: MHKC/AES with crypto secret key K.

```
"Xk9mP" -> [Decryption] -> "HELLO"
```

---

## Detailed Architecture for Implementation

<p align="center">
	<img src="Stencil_system_architecture.jpeg" alt="Centered image" style="max-width: 150%;">
</p>

---

## Dependencies

| Library | Purpose |
|---|---|
| `PyCryptodome` (Python) | AES encryption/decryption for PoC implementation |
| `pytest` | Unit and integration testing |
| `invoke` | Task runner (`inv build`, `inv test`, `inv clean`) |

---

### Crypto-library Choice for Python Implementation

Possible open source crypto-libraries: `PyCryptodome` and `cryptography` (PyCA).

- `cryptography` (PyCA): backed by OpenSSL and uses `cffi`; useful for Python wrappers around C in final library direction.
- `PyCryptodome`: cleaner API/readability (`pad`/`unpad`, compact encrypt/decrypt), a good fit for reference implementation used by tests.
- Final decision: `PyCryptodome` for the Python proof-of-concept/reference implementation.

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

For the phased roadmap and task checklist, see [Implementation_checklist.md](Implementation_checklist.md).

## Resources

### Cryptography
1. https://www.geeksforgeeks.org/computer-networks/cryptography-tutorial/

### Git setup and usage
1. https://www.atlassian.com/git/tutorials/what-is-git
