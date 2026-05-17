# A stencil based crypto-scheme

## Introduction

![The Dataflow](docs/Paper-Pencil-Block-Diag.jpeg)

## A detailed workflow example

See [docs/Workflow_Example.md](docs/Workflow_Example.md) for a step-by-step walkthrough of the encryption and decryption process.

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

## The Stencil System using stencil_lib containing APIs:

See [docs/Stencil_System_Architecture.md](docs/Stencil_System_Architecture.md) for the architecture diagram.

---

## Resources

### Cryptography
1. https://www.geeksforgeeks.org/computer-networks/cryptography-tutorial/

### Git setup and usage
1. https://www.atlassian.com/git/tutorials/what-is-git
