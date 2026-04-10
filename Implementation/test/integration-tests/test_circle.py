import random
import pytest
from Crypto.Util.Padding import pad, unpad
import stencil_lib as cryptolib

Algo = cryptolib.Algo
AES_256_KEY_SIZE = cryptolib.AES_256_KEY_SIZE
AES_128_KEY_SIZE = cryptolib.AES_128_KEY_SIZE
AES_BLOCK_SIZE = cryptolib.AES_BLOCK_SIZE
cipher_encrypt = cryptolib.cipher_encrypt
cipher_decrypt = cryptolib.cipher_decrypt


@pytest.mark.parametrize("key_size", [AES_128_KEY_SIZE, AES_256_KEY_SIZE])
@pytest.mark.parametrize("plain_text_len", [1, 15, 16, 17, 64, 200])
def test_aes_encrypt_decrypt_roundtrip(plain_text_len, key_size):
    """AES ECB: encrypt then decrypt recovers original plaintext."""
    key = random.randbytes(key_size)
    plaintext = random.randbytes(plain_text_len)

    padded_plaintext = pad(plaintext, AES_BLOCK_SIZE)
    ciphertext = cipher_encrypt(padded_plaintext, key, algo=Algo.AES)
    decrypted = cipher_decrypt(ciphertext, key, algo=Algo.AES)
    unpadded = unpad(decrypted, AES_BLOCK_SIZE)

    assert unpadded == plaintext


@pytest.mark.parametrize("shift", [0, 1, 13, 127, 255])
@pytest.mark.parametrize("plain_text_len", [1, 16, 100])
def test_caesar_encrypt_decrypt_roundtrip(plain_text_len, shift):
    """Caesar: encrypt then decrypt recovers original plaintext."""
    plaintext = random.randbytes(plain_text_len)

    ciphertext = cipher_encrypt(plaintext, shift, algo=Algo.CAESAR)
    decrypted = cipher_decrypt(ciphertext, shift, algo=Algo.CAESAR)

    assert decrypted == plaintext


@pytest.mark.parametrize("key", [b"K", b"SECRET", b"A" * 16, bytes(range(32))])
@pytest.mark.parametrize("plain_text_len", [1, 16, 100])
def test_vigenere_encrypt_decrypt_roundtrip(plain_text_len, key):
    """Vigenère: encrypt then decrypt recovers original plaintext."""
    plaintext = random.randbytes(plain_text_len)

    ciphertext = cipher_encrypt(plaintext, key, algo=Algo.VIGENERE)
    decrypted = cipher_decrypt(ciphertext, key, algo=Algo.VIGENERE)

    assert decrypted == plaintext
