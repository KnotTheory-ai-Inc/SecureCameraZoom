import os
import random
import pytest
from Crypto.Cipher import AES as _AES
from Crypto.Util.Padding import pad
import stencil_lib
from utils.classes import AESConfig, CaesarConfig, VigenereConfig
from utils.constants import AES_128_KEY_SIZE, AES_256_KEY_SIZE, AES_BLOCK_SIZE
from stencil_lib import StencilConfig

cipher_encrypt = stencil_lib.cipher_encrypt


@pytest.mark.parametrize("plain_text_len", [1, 16, 17, 64])
@pytest.mark.parametrize("key_size", [AES_128_KEY_SIZE, AES_256_KEY_SIZE])
def test_aes_encrypt_output_length(plain_text_len, key_size):
    """AES ECB: ciphertext length equals padded plaintext length."""
    plaintext = pad(random.randbytes(plain_text_len), AES_BLOCK_SIZE)
    ciphertext = cipher_encrypt(plaintext, AESConfig(random.randbytes(key_size)))
    assert len(ciphertext) == len(plaintext)


@pytest.mark.parametrize("plain_text_len", [1, 16, 64])
@pytest.mark.parametrize("shift", [1, 13, 128, 255])
def test_caesar_encrypt_output_length(plain_text_len, shift):
    """Caesar: ciphertext length equals plaintext length."""
    plaintext = random.randbytes(plain_text_len)
    assert len(cipher_encrypt(plaintext, CaesarConfig(shift))) == len(plaintext)


@pytest.mark.parametrize("plain_text_len", [1, 16, 64])
@pytest.mark.parametrize("kw", [b"K", b"SECRET"])
def test_vigenere_encrypt_output_length(plain_text_len, kw):
    """Vigenere: ciphertext length equals plaintext length."""
    plaintext = random.randbytes(plain_text_len)
    assert len(cipher_encrypt(plaintext, VigenereConfig(kw))) == len(plaintext)


@pytest.mark.parametrize("mode, mode_params, needs_padding", [
    pytest.param(_AES.MODE_ECB, {},                        True,  id="ECB"),
    pytest.param(_AES.MODE_CBC, {"iv": os.urandom(16)},    True,  id="CBC"),
    pytest.param(_AES.MODE_CTR, {"nonce": os.urandom(8)},  False, id="CTR"),
])
def test_aes_encrypt_modes_output_length(mode, mode_params, needs_padding):
    """AES: ciphertext length equals (padded) plaintext length across ECB, CBC, CTR."""
    plaintext = random.randbytes(random.randint(1, 2048))
    if needs_padding:
        plaintext = pad(plaintext, AES_BLOCK_SIZE)
    cfg = AESConfig(random.randbytes(AES_256_KEY_SIZE), mode, **mode_params)
    assert len(cipher_encrypt(plaintext, cfg)) == len(plaintext)
