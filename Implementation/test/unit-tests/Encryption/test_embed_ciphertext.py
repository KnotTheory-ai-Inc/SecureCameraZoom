#!/usr/bin/env python3
"""Quick verification of steganography_encrypt logic."""

import random
import pytest
from src.python.common.classes import Grid, Stencil, SecretKey, GridShape, CipherConfig
from src.python.Encryption.steganography_encrypt import steganography_encrypt

# Mock CipherConfig for testing
class MockConfig(CipherConfig):
    def __init__(self):
        self.parameters = {}
        self.algo = "mock"
    
    def encrypt(self, plaintext: bytes, *args, **kwargs) -> bytes:
        return plaintext
    
    def decrypt(self, ciphertext: bytes, *args, **kwargs) -> bytes:
        return ciphertext

# Common 20x20 grid — 400 cells, enough for all test sizes
GRID_ROWS, GRID_COLS = 20, 20


# Basic Test case
def test_steganography_encrypt_basic():

    # Stencil 0: 2 coords → ciphertext[0:2]
    # Stencil 1: 3 coords → ciphertext[2:5]
    stencil_0 = Stencil(shape="disconnected", len=2, coords=[(0, 0), (0, 1)])
    stencil_1 = Stencil(shape="disconnected", len=3, coords=[(1, 0), (1, 1), (1, 2)])
    stencils = [stencil_0, stencil_1]

    # Create ciphertext — random bytes, length must match sum(partition_list) = 5
    ciphertext = random.randbytes(5)

    # Create grid as dict-based for new Grid API
    grid_data = {(r, c): random.randint(0, 255) for r in range(GRID_ROWS) for c in range(GRID_COLS)}
    grid = Grid(data=grid_data)

    # Create secret key
    secret_key = SecretKey(
        stencils=stencils,
        partition_list=[2, 3],
        cipher_cfg=MockConfig()
    )

    # Embed
    result = steganography_encrypt(grid, ciphertext, secret_key)

    # Expected: each stencil coord holds the corresponding ciphertext byte
    assert result.data[(0, 0)] == ciphertext[0], f"Expected {ciphertext[0]} at (0,0), got {result.data[(0, 0)]}"
    assert result.data[(0, 1)] == ciphertext[1], f"Expected {ciphertext[1]} at (0,1), got {result.data[(0, 1)]}"
    assert result.data[(1, 0)] == ciphertext[2], f"Expected {ciphertext[2]} at (1,0), got {result.data[(1, 0)]}"
    assert result.data[(1, 1)] == ciphertext[3], f"Expected {ciphertext[3]} at (1,1), got {result.data[(1, 1)]}"
    assert result.data[(1, 2)] == ciphertext[4], f"Expected {ciphertext[4]} at (1,2), got {result.data[(1, 2)]}"


@pytest.mark.parametrize("num_partitions", [2, 3, 5])
@pytest.mark.parametrize("n", [5, 25, 70, 100])
def test_steganography_encrypt_parametrized(n, num_partitions):
    # Generate row-major coords from the common grid, take first n
    all_coords = [(r, c) for r in range(GRID_ROWS) for c in range(GRID_COLS)][:n]

    # Split n into num_partitions as evenly as possible
    base, remainder = divmod(n, num_partitions)
    partition_list = [base + (1 if i < remainder else 0) for i in range(num_partitions)]

    # Build stencils from partition_list
    stencils = []
    coord_offset = 0
    for size in partition_list:
        stencils.append(Stencil(shape="disconnected", len=size, coords=all_coords[coord_offset:coord_offset + size]))
        coord_offset += size

    ciphertext = random.randbytes(n)
    grid_data = {(r, c): random.randint(0, 255) for r in range(GRID_ROWS) for c in range(GRID_COLS)}
    grid = Grid(data=grid_data)
    secret_key = SecretKey(
        stencils=stencils,
        partition_list=partition_list,
        cipher_cfg=MockConfig()
    )

    result = steganography_encrypt(grid, ciphertext, secret_key)

    # Verify every embedded byte matches the ciphertext at its coord
    for idx, (row, col) in enumerate(all_coords):
        assert result.data[(row, col)] == ciphertext[idx], \
            f"n={n}, num_partitions={num_partitions}: Expected {ciphertext[idx]} at ({row},{col}), got {result.data[(row, col)]}"

