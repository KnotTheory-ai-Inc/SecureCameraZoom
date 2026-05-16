"""
KPI test: wall-clock time for each stencil_lib API on an HD-ready 1280×720 grid.
    keygen → encrypt → decrypt
"""
import pytest
import random
from datetime import datetime
import stencil_lib
from stencil_lib import GridShape, StencilConfig
from utils.classes import AESConfigPadded
from utils.constants import AES_128_KEY_SIZE

# ── KPI budgets (milliseconds) ───────────────────────────────────────────
KEYGEN_KPI_MS  = 15000
ENCRYPT_KPI_MS =  5000
DECRYPT_KPI_MS =  1000

# ── Setup ──────────────────────────────────────────────────────────────────
GRID_SHAPE     = GridShape(n=2, shape=(1280, 720))
PLAINTEXT      = random.randbytes(32)
CIPHER_CFG     = AESConfigPadded(random.randbytes(AES_128_KEY_SIZE))
STENCIL_CFG    = StencilConfig(
    total_bytes    = len(CIPHER_CFG.encrypt(PLAINTEXT)),
    num_partitions = 8,
    grid_shape     = GRID_SHAPE,
)


# ── Fixtures ───────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def secret_key():
    """Run keygen once per test session; shared by encrypt and decrypt KPI tests."""
    return stencil_lib.keygen(STENCIL_CFG, cipher_cfg=CIPHER_CFG)


@pytest.fixture(scope="module")
def obfuscated_grid(secret_key):
    """Run encrypt once per test session; shared by the decrypt KPI test."""
    return stencil_lib.encrypt(PLAINTEXT, secret_key, STENCIL_CFG)


# ── Tests ──────────────────────────────────────────────────────────────────

def test_kpi_keygen_time():
    """keygen must complete within {KEYGEN_KPI_MS}ms on a 1280×720 grid."""
    t0 = datetime.now()
    stencil_lib.keygen(STENCIL_CFG, cipher_cfg=CIPHER_CFG)
    t_ms = (datetime.now() - t0).total_seconds() * 1000
    assert t_ms < KEYGEN_KPI_MS, f"keygen KPI exceeded: {t_ms:.1f}ms > {KEYGEN_KPI_MS}ms"


def test_kpi_encrypt_time(secret_key):
    """encrypt must complete within {ENCRYPT_KPI_MS}ms."""
    t0 = datetime.now()
    stencil_lib.encrypt(PLAINTEXT, secret_key, STENCIL_CFG)
    t_ms = (datetime.now() - t0).total_seconds() * 1000
    assert t_ms < ENCRYPT_KPI_MS, f"encrypt KPI exceeded: {t_ms:.1f}ms > {ENCRYPT_KPI_MS}ms"


def test_kpi_decrypt_time(secret_key, obfuscated_grid):
    """decrypt must complete within {DECRYPT_KPI_MS}ms and recover original plaintext."""
    t0 = datetime.now()
    recovered = stencil_lib.decrypt(obfuscated_grid, secret_key, STENCIL_CFG)
    t_ms = (datetime.now() - t0).total_seconds() * 1000
    assert t_ms < DECRYPT_KPI_MS, f"decrypt KPI exceeded: {t_ms:.1f}ms > {DECRYPT_KPI_MS}ms"
    assert recovered == PLAINTEXT, (
        f"Round-trip failed:\n  original : {PLAINTEXT.hex()}\n  recovered: {recovered.hex()}"
    )
