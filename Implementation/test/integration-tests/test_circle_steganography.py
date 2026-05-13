"""
Integration test: full stencil system circle.

    keygen → random grid → embed ciphertext → extract ciphertext

Verifies that steganography_decrypt(steganography_encrypt(grid, ct, sk), sk) == ct
"""

import random
import pytest
import stencil_lib
from utils.classes import CaesarConfig
from stencil_lib import GridShape, StencilConfig


@pytest.mark.parametrize("grid_shape", [
    GridShape(n=5, shape=tuple(random.randint(3, 35) for _ in range(5))),
])
@pytest.mark.parametrize("num_partitions", [1, 5, 9, 15, 20])
@pytest.mark.parametrize("byte_length", [1, 5, 31])
def test_steganography_algo_circle(byte_length, num_partitions, grid_shape):
    """Embed ciphertext into a random grid, then extract it — must recover original."""

    if num_partitions > byte_length:
        pytest.skip(f"num_partitions={num_partitions} > byte_length={byte_length}, invalid")

    # Step 1: ciphertext (simulate output of Level 1 cipher)
    ciphertext = random.randbytes(byte_length)


    # Step 2: generate secret key — `byte_length` bytes, `num_partitions` partitions, grid_shape
    stencil_cfg = stencil_lib.StencilConfig(
        total_bytes=len(ciphertext),
        num_partitions=num_partitions,
        grid_shape=grid_shape,
    )
    secret_key = stencil_lib.keygen(
        stencil_cfg,
        cipher_cfg=CaesarConfig(shift=5),  # cipher_cfg required by SecretKey, not used here
    )

    # Step 3: generate obfuscation grid and embed
    grid = stencil_lib.generate_random_grid(grid_shape) 
    obfuscated_grid = stencil_lib.steganography_encrypt(grid, ciphertext, secret_key, stencil_cfg)

    # Step 4: extract and verify round-trip
    recovered = stencil_lib.steganography_decrypt(obfuscated_grid, secret_key, stencil_cfg)

    assert recovered == ciphertext, (
        f"Round-trip failed:\n  original : {ciphertext.hex()}\n  recovered: {recovered.hex()}"
    )


def test_steganography_algo_circle_7d_random():
    """Special test: 7D grid, random byte_length (256-1024), random num_partitions (10-40)."""
    grid_shape = GridShape(n=7, shape=tuple(random.randint(4, 18) for _ in range(7)))
    byte_length = random.randint(256, 1024)
    num_partitions = random.randint(10, 40)

    # Step 1: ciphertext (simulate output of Level 1 cipher)
    ciphertext = random.randbytes(byte_length)
    # Step 2: generate secret key
    stencil_cfg = stencil_lib.StencilConfig(
        total_bytes=len(ciphertext),
        num_partitions=num_partitions,
        grid_shape=grid_shape,
    )
    secret_key = stencil_lib.keygen(
        stencil_cfg,
        cipher_cfg=CaesarConfig(shift=5),
    )
    # Step 3: generate obfuscation grid and embed
    grid = stencil_lib.generate_random_grid(grid_shape)
    obfuscated_grid = stencil_lib.steganography_encrypt(grid, ciphertext, secret_key, stencil_cfg)
    # Step 4: extract and verify round-trip
    recovered = stencil_lib.steganography_decrypt(obfuscated_grid, secret_key, stencil_cfg)
    assert recovered == ciphertext, (
        f"7D random test failed:\n  original : {ciphertext.hex()}\n  recovered: {recovered.hex()}"
    )