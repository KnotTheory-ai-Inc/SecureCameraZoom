import sys
import os
import glob

_here = os.path.dirname(__file__)

# Tests run on the built wheel in build/dist/
_lib = glob.glob(os.path.join(_here, "build", "dist", "*.whl"))
if not _lib:
    raise RuntimeError("No wheel found — run `inv build --lib` before running tests.")
sys.path.insert(0, _lib[0])
