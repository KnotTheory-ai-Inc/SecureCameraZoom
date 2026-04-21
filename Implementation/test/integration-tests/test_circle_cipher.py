import random
import pytest
from Crypto.Util.Padding import pad, unpad
import stencil_lib
from utils.classes import AESConfig, CaesarConfig, VigenereConfig
from utils.constants import AES_128_KEY_SIZE, AES_256_KEY_SIZE, AES_BLOCK_SIZE

cipher_encrypt = stencil_lib.cipher_encrypt
cipher_decrypt = stencil_lib.cipher_decrypt


@pytest.mark.parametrize("key_size", [AES_128_KEY_SIZE, AES_256_KEY_SIZE])
@pytest.mark.parametrize("plain_text_len", [1, 15, 16, 17, 64, 200])
def test_aes_encrypt_decrypt_roundtrip(plain_text_len, key_size):
    """AES ECB: encrypt then decrypt recovers original plaintext."""
    cfg = AESConfig(random.randbytes(key_size))
    plaintext = random.randbytes(plain_text_len)

    padded_plaintext = pad(plaintext, AES_BLOCK_SIZE)
    ciphertext = cipher_encrypt(padded_plaintext, cfg)
    decrypted = cipher_decrypt(ciphertext, cfg)
    unpadded = unpad(decrypted, AES_BLOCK_SIZE)

    assert unpadded == plaintext


@pytest.mark.parametrize("shift", [0, 1, 13, 127, 255])
@pytest.mark.parametrize("plain_text_len", [1, 16, 100])
def test_caesar_encrypt_decrypt_roundtrip(plain_text_len, shift):
    """Caesar: encrypt then decrypt recovers original plaintext."""
    plaintext = random.randbytes(plain_text_len)
    cfg = CaesarConfig(shift)

    ciphertext = cipher_encrypt(plaintext, cfg)
    decrypted = cipher_decrypt(ciphertext, cfg)

    assert decrypted == plaintext


@pytest.mark.parametrize("kw", [b"K", b"SECRET", b"A" * 16, bytes(range(32))])
@pytest.mark.parametrize("plain_text_len", [1, 16, 100])
def test_vigenere_encrypt_decrypt_roundtrip(plain_text_len, kw):
    """Vigenere: encrypt then decrypt recovers original plaintext."""
    plaintext = random.randbytes(plain_text_len)
    cfg = VigenereConfig(kw)

    ciphertext = cipher_encrypt(plaintext, cfg)
    decrypted = cipher_decrypt(ciphertext, cfg)

    assert decrypted == plaintext
