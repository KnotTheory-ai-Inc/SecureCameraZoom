import random
import pytest
from Crypto.Cipher import AES
from utils.classes import CaesarConfig, VigenereConfig, AESConfig
from utils.constants import AES_128_KEY_SIZE, AES_256_KEY_SIZE
import stencil_lib

_AES_KEY_128 = random.randbytes(AES_128_KEY_SIZE)
_AES_KEY_256 = random.randbytes(AES_256_KEY_SIZE)
_AES_IV      = random.randbytes(16)
_AES_NONCE   = random.randbytes(8)


_CIPHER_CFGS = [
    CaesarConfig(shift=200),
    VigenereConfig(keyword=b"mysecretkey"),
    AESConfig(key=_AES_KEY_128, mode=AES.MODE_CBC, iv=_AES_IV),    # CBC, 128-bit key
    AESConfig(key=_AES_KEY_128, mode=AES.MODE_CTR, nonce=_AES_NONCE),  # CTR, 128-bit key
]


@pytest.mark.parametrize("cipher_cfg", _CIPHER_CFGS, ids=["caesar200", "vigenere_mysecretkey", "aes_cbc_128", "aes_ctr_128"])
@pytest.mark.parametrize("in_byte_len", [512, 640])
def test_stencil_system_circle(in_byte_len, cipher_cfg):
    """Full system circle: keygen → encrypt → decrypt must recover original plaintext."""

    # Use a fixed grid shape for all tests (e.g., 23x31x42)
    grid_shape = stencil_lib.GridShape(n=3, shape=(23, 31, 42))

    # Step 1: some constants
    plaintext = random.randbytes(in_byte_len)
    num_partitions = random.randint(in_byte_len // 4, in_byte_len * 3 // 4)

    # Step 2: keygen
    secret_key = stencil_lib.keygen(
        total_bytes=in_byte_len,
        num_partitions=num_partitions,
        grid_shape=grid_shape,
        cipher_cfg=cipher_cfg,
    )

    # Step 3: encrypt (cipher + steganography)
    obfuscated_grid = stencil_lib.encrypt(plaintext, secret_key, grid_shape)

    # Step 4: decrypt (steganography + cipher)
    recovered = stencil_lib.decrypt(obfuscated_grid, secret_key)

    assert recovered == plaintext, (
        f"Round-trip failed [length={in_byte_len}, partitions={num_partitions}, grid={grid_shape}]:\n"
        f"  original : {plaintext.hex()}\n  recovered: {recovered.hex()}"
    )
