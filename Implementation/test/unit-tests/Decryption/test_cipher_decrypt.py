import os
import random
import pytest
from Crypto.Cipher import AES as _AES
from Crypto.Util.Padding import pad
import stencil_lib as cryptolib

AES_256_KEY_SIZE = cryptolib.AES_256_KEY_SIZE
AES_128_KEY_SIZE = cryptolib.AES_128_KEY_SIZE
AES_BLOCK_SIZE = cryptolib.AES_BLOCK_SIZE
AESConfig = cryptolib.AESConfig
CaesarConfig = cryptolib.CaesarConfig
VigenereConfig = cryptolib.VigenereConfig
cipher_encrypt = cryptolib.cipher_encrypt
cipher_decrypt = cryptolib.cipher_decrypt


@pytest.mark.parametrize("plain_text_len", [1, 16, 17, 64])
@pytest.mark.parametrize("key_size", [AES_128_KEY_SIZE, AES_256_KEY_SIZE])
def test_aes_decrypt(plain_text_len, key_size):
    """AES ECB: decrypt(encrypt(pt)) == pt."""
    cfg = AESConfig(random.randbytes(key_size))
    plaintext = pad(random.randbytes(plain_text_len), AES_BLOCK_SIZE)
    assert cipher_decrypt(cipher_encrypt(plaintext, cfg), cfg) == plaintext


@pytest.mark.parametrize("plain_text_len", [1, 16, 64])
@pytest.mark.parametrize("shift", [1, 13, 128, 255])
def test_caesar_decrypt(plain_text_len, shift):
    """Caesar: decrypt(encrypt(pt)) == pt."""
    plaintext = random.randbytes(plain_text_len)
    cfg = CaesarConfig(shift)
    assert cipher_decrypt(cipher_encrypt(plaintext, cfg), cfg) == plaintext


@pytest.mark.parametrize("plain_text_len", [1, 16, 64])
@pytest.mark.parametrize("kw", [b"K", b"SECRET"])
def test_vigenere_decrypt(plain_text_len, kw):
    """Vigenere: decrypt(encrypt(pt)) == pt."""
    plaintext = random.randbytes(plain_text_len)
    cfg = VigenereConfig(kw)
    assert cipher_decrypt(cipher_encrypt(plaintext, cfg), cfg) == plaintext


@pytest.mark.parametrize("mode, mode_params, needs_padding", [
    pytest.param(_AES.MODE_ECB, {},                        True,  id="ECB"),
    pytest.param(_AES.MODE_CBC, {"iv": os.urandom(16)},    True,  id="CBC"),
    pytest.param(_AES.MODE_CTR, {"nonce": os.urandom(8)},  False, id="CTR"),
])
def test_aes_decrypt_modes(mode, mode_params, needs_padding):
    """AES: decrypt(encrypt(pt)) == pt across ECB, CBC, and CTR modes."""
    plaintext = random.randbytes(random.randint(1, 2048))
    if needs_padding:
        plaintext = pad(plaintext, AES_BLOCK_SIZE)
    cfg = AESConfig(random.randbytes(AES_256_KEY_SIZE), mode, **mode_params)
    assert cipher_decrypt(cipher_encrypt(plaintext, cfg), cfg) == plaintext

