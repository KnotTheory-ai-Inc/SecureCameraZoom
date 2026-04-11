# The Overall Workflow of the Paper-Pencil Crypto-scheme

![The Workflow](Paper-Pencil-Block-Diag.jpeg)

# Detailed Workflow with an example

### Step 1: **Encrypt the plain text First (Level 1 encryption)**

Using Classical encryption schemes: MHKC/AES with crypto secret key K
```
"HELLO" → [Encryption] → "Xk9mP"
```

### Step 2: ** Steganographic Encryption (Level 2 encryption)** 

Security through obscurity / Grid hiding technique

**Fill Grid with Random Letters encrypted text from Step 1**

```
X Q Z M P T R N S V B W K D F G C Y A I U E
K R X N A D M L P Q S Z T Z B F Y W C V G U  ← 'X' hidden here
F Y k W S C Q N B M K P R T Z A D V L G I H  ← 'k' hidden here  
J U 9 m P I V N T Q R S W V X B A F D C H T  ← '9mP' hidden here
Z M K P N S T Q R W X B A D F C V Y G U E I
Q T W R S B N K M P L A X Z Y D F V G C H U
... (assume 100 more rows of random letters!)
```

### Step 3: **Generate Secret Key S**

According to the paper, the secret key contains:

Secret Key S = {
  1. Stencil Set SRl (chosen shapes)
  2. Bijection function g (maps partitions to stencils)
  3. MHKC/AES crypto secret key K
  4. Permutation σ 
  5. Starting position
  ...
}

For this example,
```
Secret Key S = {
  1. Stencil Set SRl = {"L-shape"}
  2. Starting_coordinates: {(2,3)},
  3. Partition: [1, 1, 3], --> 'X', 'k', '9mP'
  4. Reading_order: "Top-to-bottom, left-to-right",
  5. MHKC/AES crypto secret key K
}
```

### Step 4: **Transmission/Reception channel - Communication network**
 **The grid** (as byte stream over network(Byte stream implementation) or as physical paper through fax (OCR implementation))


### Step 5: **Steganographic Decryption (Level 1 decryption) **
  Input: 
    1. Obscure Grid
    2. Assume the receiver already has : **The secret key S** (stencil indices/coordinates + crypto key)

  #### Camera zoom based OCR technique:
  Assume the Grid is printed on a paper, using Computer vision techniques, detect the overall grid and employ the camera to extract the cipher text.
  
  For this example:
  ```
  Camera uses those coordinates to zoom to specific grid positions

  OCR reads characters at each position → collects "Xk9mP"
  ```
  #### Byte stream implementation:
  The grid is stored in a memory region and we employ classical arrays/pointer mechanism and determine the cipher text.


  Output:
    Cipher text - "Xk9mP"

### Step 6: **Decrypt the Cipher text (Level 2 decryption) **

Using Classical decryption schemes: MHKC/AES with crypto secret key K

"Xk9mP" → [Decryption] → "HELLO"

---

## Dependencies

| Library | Purpose |
|---|---|
| `PyCryptodome` (Python) | AES encryption/decryption — for PoC implementation |
| `pytest` | Unit testing, Integration testing |
| `invoke` | Task runner (`inv build`, `inv test`, `inv clean`) |

---

### Crypto-libray choice for Python implementation

Possible open source crypto-libraries: `PyCryptodome` and `cryptography` (PyCA).

- **`cryptography` (PyCA)** : it is backed by OpenSSL. It also uses `cffi` as its C binding layer — making it a natural fit for Python based wrapping layers on C in the final library.

- **`PyCryptodome`** : The API is cleaner and more readable (`pad`/`unpad` built-in, compact one-liner encrypt/decrypt), hence good readability. Suits best for reference implementation as a part of test system to challenge the library. [PyCryptodome Documentation](https://pycryptodome.readthedocs.io/en/latest/)

- **Final decision:** `PyCryptodome` for the Python proof of concept/reference implementation.

---

### Installation and usage

**0. Clone the repo and navigate to Implementation**

```bash
git clone <repo-url>
cd SecureCameraZoom/Implementation
```

**1. Create and activate a virtual environment(optional)**

```bash
python -m venv .venv
```

> **Note:** `venv` is built into Python 3.3+ — no separate installation needed. Exception: Some Ubuntu/Debian Linux might require `sudo apt install python3-venv` first.

Windows:
```bash
.venv\Scripts\activate
```

Linux:
```bash
source .venv/bin/activate
```

**2. Install dependencies(To be executed first time and once)**

```bash
pip install -r requirements.txt
```

> If `pip` is not on PATH (System Environment variable), use:
> ```bash
> python -m pip install -r requirements.txt
> ```

**3. Build and run tests**

```bash
inv build   # build .whl → build/dist/ 
inv test    # run all tests (unit + integration) on built lib
inv clean   # remove build output
```

> Individual test targets: `inv test_unit`, `inv test_integration`

---

## Project tooling files

### `pyproject.toml` — Package definition

Tells `pip` the project config and how to build it.

For more details, see the [Python Packaging User Guide on pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/).

```
pyproject.toml
├── [build-system]    — which build backend to use (setuptools)
├── [project]         — name, version, python version, dependencies
└── [tool.setuptools] — where the source packages live (src/python)
```

---

### `tasks.py` — Task runner (`inv` commands)

Defines custom CLI commands using the [`invoke`](https://www.pyinvoke.org/) library.

---

### `conftest.py` — pytest configuration

Automatically loaded by pytest before any test runs. Locates the built wheel in `build/dist/*.whl` and makes it available for import in test files.

For more details, see the [pytest documentation on conftest.py](https://docs.pytest.org/en/stable/reference/fixtures.html#conftest-py).

---

> For the full phased Roadmap and task checklist, see [Implementation_checklist.md](Implementation_checklist.md).