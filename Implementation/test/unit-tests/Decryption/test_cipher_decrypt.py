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

@pytest.mark.parametrize("plain_text_len", [1, 5, 16, 17, 32, 100])
@pytest.mark.parametrize("key_size", [AES_256_KEY_SIZE, AES_128_KEY_SIZE])
def test_aes_decrypt_output_length_equals_ciphertext(plain_text_len, key_size):
    """AES ECB: decrypted output length must equal ciphertext length."""
    key = random.randbytes(key_size)
    padded = pad(random.randbytes(plain_text_len), AES_BLOCK_SIZE)
    ciphertext = cipher_encrypt(padded, key, algo=Algo.AES)
    assert len(cipher_decrypt(ciphertext, key, algo=Algo.AES)) == len(ciphertext)


def test_aes_wrong_key():
    """AES: decrypting with a wrong key must not recover the original plaintext."""
    key1 = random.randbytes(AES_256_KEY_SIZE)
    key2 = random.randbytes(AES_256_KEY_SIZE)
    plaintext = pad(random.randbytes(16), AES_BLOCK_SIZE)
    ciphertext = cipher_encrypt(plaintext, key1, algo=Algo.AES)
    assert cipher_decrypt(ciphertext, key2, algo=Algo.AES) != plaintext


def test_aes_decrypt_same_key():
    """AES: decrypting the same ciphertext twice with same key returns same result."""
    key = random.randbytes(AES_256_KEY_SIZE)
    plaintext = pad(random.randbytes(16), AES_BLOCK_SIZE)
    ct = cipher_encrypt(plaintext, key, algo=Algo.AES)
    assert cipher_decrypt(ct, key, algo=Algo.AES) == cipher_decrypt(ct, key, algo=Algo.AES)


@pytest.mark.parametrize("shift", [0, 1, 13, 127, 255])
def test_caesar_decrypt_output_length_equals_input(shift):
    """Caesar: decrypted length must equal ciphertext length."""
    ct = cipher_encrypt(random.randbytes(20), shift, algo=Algo.CAESAR)
    assert len(cipher_decrypt(ct, shift, algo=Algo.CAESAR)) == len(ct)


def test_caesar_shift_zero_decrypt_is_identity():
    """Caesar shift=0: decrypt must return ciphertext unchanged."""
    ct = random.randbytes(20)
    assert cipher_decrypt(ct, 0, algo=Algo.CAESAR) == ct


def test_caesar_wrong_shift():
    """Caesar: wrong shift must not recover the original plaintext."""
    plaintext = random.randbytes(20)
    ct = cipher_encrypt(plaintext, 13, algo=Algo.CAESAR)
    assert cipher_decrypt(ct, 14, algo=Algo.CAESAR) != plaintext


@pytest.mark.parametrize("key", [b"K", b"SECRET", bytes(range(16))])
def test_vigenere_decrypt_output_length_equals_input(key):
    """Vigenere: decrypted length must equal ciphertext length."""
    ct = cipher_encrypt(random.randbytes(20), key, algo=Algo.VIGENERE)
    assert len(cipher_decrypt(ct, key, algo=Algo.VIGENERE)) == len(ct)


def test_vigenere_wrong_key():
    """Vigenere: wrong key must not recover the original plaintext."""
    plaintext = random.randbytes(20)
    ct = cipher_encrypt(plaintext, b"RIGHTKEY", algo=Algo.VIGENERE)
    assert cipher_decrypt(ct, b"WRONGKEY", algo=Algo.VIGENERE) != plaintext

