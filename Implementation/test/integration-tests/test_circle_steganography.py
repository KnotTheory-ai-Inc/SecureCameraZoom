"""
Integration test: full stencil system circle.

    keygen → random grid → embed ciphertext → extract ciphertext

Verifies that steganography_decrypt(steganography_encrypt(grid, ct, sk), sk) == ct
"""

import random
import pytest
import stencil_lib
from utils.classes import CaesarConfig
from stencil_lib import GridSize


@pytest.mark.parametrize("num_partitions", range(1, 15))
@pytest.mark.parametrize("byte_length", range(1, 64))
def test_steganography_algo_circle(byte_length, num_partitions):
    """Embed ciphertext into a random grid, then extract it — must recover original."""

    if num_partitions > byte_length:
        pytest.skip(f"num_partitions={num_partitions} > byte_length={byte_length}, invalid")

    # Step 1: ciphertext (simulate output of Level 1 cipher)
    ciphertext = random.randbytes(byte_length)

    # Step 2: generate secret key — `byte_length` bytes, `num_partitions` partitions, 20x20 grid
    grid_size = GridSize(rows=20, cols=20)
    secret_key = stencil_lib.keygen(
        total_bytes=len(ciphertext),
        num_partitions=num_partitions,
        grid_size=grid_size,
        cipher_cfg=CaesarConfig(shift=5),  # cipher_cfg required by SecretKey, not used here
    )

    # Step 3: generate obfuscation grid and embed
    grid = stencil_lib.generate_random_grid(20, 20)
    obfuscated_grid = stencil_lib.steganography_encrypt(grid, ciphertext, secret_key)

    # Step 4: extract and verify round-trip
    recovered = stencil_lib.steganography_decrypt(obfuscated_grid, secret_key)

    assert recovered == ciphertext, (
        f"Round-trip failed:\n  original : {ciphertext.hex()}\n  recovered: {recovered.hex()}"
    )
