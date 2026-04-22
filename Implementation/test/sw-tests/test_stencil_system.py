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

# values for (in_byte_len,grid_size)
PARAMS = [
    (64,  (32, 32)),
    (64,  (50, 50)),
    (64,  (100, 100)),
    (128, (50, 50)),
    (128, (100, 100)),
    (256, (100, 100)),
    (512, (100, 100)),
    (640, (50, 50)),
    (1024, (100, 100)),
]

_CIPHER_CFGS = [
    CaesarConfig(shift=0),
    CaesarConfig(shift=13),
    CaesarConfig(shift=255),
    VigenereConfig(keyword=b"secretkey"),
    VigenereConfig(keyword=b"x"),
    AESConfig(key=_AES_KEY_128),                                    # ECB, 128-bit key
    AESConfig(key=_AES_KEY_256),                                    # ECB, 256-bit key
    AESConfig(key=_AES_KEY_128, mode=AES.MODE_CBC, iv=_AES_IV),    # CBC, 128-bit key
    AESConfig(key=_AES_KEY_128, mode=AES.MODE_CFB, iv=_AES_IV),    # CFB, 128-bit key
    AESConfig(key=_AES_KEY_128, mode=AES.MODE_OFB, iv=_AES_IV),    # OFB, 128-bit key
    AESConfig(key=_AES_KEY_128, mode=AES.MODE_CTR, nonce=_AES_NONCE),  # CTR, 128-bit key
    AESConfig(key=_AES_KEY_128, mode=AES.MODE_EAX, nonce=_AES_NONCE),  # EAX, 128-bit key
    AESConfig(key=_AES_KEY_128, mode=AES.MODE_GCM, nonce=_AES_NONCE),  # GCM, 128-bit key
]


@pytest.mark.parametrize("cipher_cfg", _CIPHER_CFGS, ids=["caesar0", "caesar13", "caesar255", "vigenere_long", "vigenere_short", "aes_ecb_128", "aes_ecb_256", "aes_cbc_128", "aes_cfb_128", "aes_ofb_128", "aes_ctr_128", "aes_eax_128", "aes_gcm_128"])
@pytest.mark.parametrize("in_byte_len,grid_size", PARAMS)
def test_stencil_system_circle(in_byte_len, cipher_cfg, grid_size):
    """Full system circle: keygen → encrypt → decrypt must recover original plaintext."""

    rows, cols = grid_size

    # Step 1: some constants
    plaintext = random.randbytes(in_byte_len)
    num_partitions = random.randint(in_byte_len // 4, in_byte_len * 3 // 4)
    grid_size = stencil_lib.GridSize(rows=rows, cols=cols)

    # Step 2: keygen
    secret_key = stencil_lib.keygen(
        total_bytes=in_byte_len,
        num_partitions=num_partitions,
        grid_size=grid_size,
        cipher_cfg=cipher_cfg,
    )

    # Step 3: encrypt (cipher + steganography)
    obfuscated_grid = stencil_lib.encrypt(plaintext, secret_key, grid_size)

    # Step 4: decrypt (steganography + cipher)
    recovered = stencil_lib.decrypt(obfuscated_grid, secret_key)

    assert recovered == plaintext, (
        f"Round-trip failed [length={in_byte_len}, partitions={num_partitions}, grid={grid_size}]:\n"
        f"  original : {plaintext.hex()}\n  recovered: {recovered.hex()}"
    )
