import subprocess
import sys
import os
import glob

_here = os.path.dirname(__file__)

# Tests run on the built wheel in build/dist/
_lib = glob.glob(os.path.join(_here, "build", "dist", "*.whl"))
if not _lib:
    raise RuntimeError("No wheel found — run `inv build` before running tests.")

# Install the wheel so sub-packages (common, Encryption, Decryption) are importable.
# --no-deps: only reinstall the wheel itself; stable deps (pycryptodome etc.) are
# managed once via `pip install -r requirements.txt` and must not be wiped on every run.
subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "--force-reinstall", "--no-deps", _lib[0]])

# Make test/utils/ importable (e.g. utils.classes, utils.constants)
sys.path.insert(0, os.path.join(_here, "test"))
