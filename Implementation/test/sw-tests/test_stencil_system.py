import random
import pytest
from Crypto.Cipher import AES
from utils.classes import CaesarConfig, VigenereConfig
import stencil_lib
from stencil_lib import StencilConfig


_CIPHER_CFGS = [
    CaesarConfig(shift=200),
    VigenereConfig(keyword=b"mysecretkey"),
]


_GRID_SHAPES = [
    # 8-D hypercube: demonstrates n-dimensional generality ("n-Hypercube" concept).
    stencil_lib.GridShape(n=8, shape=tuple(random.randint(3, 12) for _ in range(8))),
    # Image-like grid: 640×480 image with 4 channels (RGBA).
    # coord (row, col, channel) → one byte
    stencil_lib.GridShape(n=3, shape=(480, 640, 4)),
]


@pytest.mark.parametrize("cipher_cfg", _CIPHER_CFGS)
@pytest.mark.parametrize("grid_shape", _GRID_SHAPES, ids=["hypercube_8d", "image_rgba_480x640x4"])
def test_stencil_system_circle(grid_shape, cipher_cfg):
    """Full system circle: keygen → encrypt → decrypt must recover original plaintext."""

    # Step 1: some constants
    in_byte_len      = random.randint(640, 1024)
    plaintext        = random.randbytes(in_byte_len)
    num_partitions   = random.randint(in_byte_len // 4, in_byte_len * 3 // 4)

    # Step 2: keygen
    stencil_cfg = stencil_lib.StencilConfig(
        total_bytes=in_byte_len,
        num_partitions=num_partitions,
        grid_shape=grid_shape,
    )
    secret_key = stencil_lib.keygen(
        stencil_cfg,
        cipher_cfg=cipher_cfg,
    )

    # Step 3: encrypt (cipher + steganography)
    obfuscated_grid = stencil_lib.encrypt(plaintext, secret_key, stencil_cfg)

    # Step 4: decrypt (steganography + cipher)
    recovered = stencil_lib.decrypt(obfuscated_grid, secret_key, stencil_cfg)

    assert recovered == plaintext, (
        f"Round-trip failed [length={in_byte_len}, partitions={num_partitions}, grid={grid_shape}]:\n"
        f"  original : {plaintext.hex()}\n  recovered: {recovered.hex()}"
    )
