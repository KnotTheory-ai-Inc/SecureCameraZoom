import subprocess
import sys
import os
import glob

_here = os.path.dirname(__file__)

# Tests run on the built wheel in build/dist/
_lib = glob.glob(os.path.join(_here, "build", "dist", "*.whl"))
if not _lib:
    raise RuntimeError("No wheel found — run `inv build` before running tests.")

# Install the wheel so sub-packages (common, Encryption, Decryption) are importable
subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "--force-reinstall", _lib[0]])
