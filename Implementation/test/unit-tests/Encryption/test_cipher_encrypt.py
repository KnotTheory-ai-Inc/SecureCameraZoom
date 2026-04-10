import random
import pytest
from Crypto.Util.Padding import pad
import stencil_lib as cryptolib

Algo = cryptolib.Algo
AES_256_KEY_SIZE = cryptolib.AES_256_KEY_SIZE
AES_128_KEY_SIZE = cryptolib.AES_128_KEY_SIZE
AES_BLOCK_SIZE = cryptolib.AES_BLOCK_SIZE
cipher_encrypt = cryptolib.cipher_encrypt


@pytest.mark.parametrize("plain_text_len", [1, 5, 16, 17, 32, 100])
@pytest.mark.parametrize("key_size", [AES_256_KEY_SIZE, AES_128_KEY_SIZE])
def test_aes_ciphertext_length_equals_padded_plaintext(plain_text_len, key_size):
    """AES ECB: ciphertext length must equal padded plaintext length (block-aligned)."""
    key = random.randbytes(key_size)
    plaintext = random.randbytes(plain_text_len)
    padded = pad(plaintext, AES_BLOCK_SIZE)
    ciphertext = cipher_encrypt(padded, key, algo=Algo.AES)
    assert len(ciphertext) == len(padded)


def test_aes_different_keys_produce_different_ciphertexts():
    """AES: same plaintext + different keys must produce different ciphertexts."""
    plaintext = pad(random.randbytes(24), AES_BLOCK_SIZE)
    ct1 = cipher_encrypt(plaintext, random.randbytes(AES_256_KEY_SIZE), algo=Algo.AES)
    ct2 = cipher_encrypt(plaintext, random.randbytes(AES_256_KEY_SIZE), algo=Algo.AES)
    assert ct1 != ct2


def test_aes_same_key_same_plaintext_same_ciphertext():
    """AES ECB: deterministic — same inputs always produce same output."""
    key = random.randbytes(AES_256_KEY_SIZE)
    plaintext = pad(random.randbytes(16), AES_BLOCK_SIZE)
    assert cipher_encrypt(plaintext, key, algo=Algo.AES) == cipher_encrypt(plaintext, key, algo=Algo.AES)


@pytest.mark.parametrize("shift", [0, 1, 13, 127, 255])
def test_caesar_output_length_equals_input(shift):
    """Caesar: ciphertext length must equal plaintext length."""
    plaintext = random.randbytes(32)
    assert len(cipher_encrypt(plaintext, shift, algo=Algo.CAESAR)) == len(plaintext)


def test_caesar_shift_zero_is_identity():
    """Caesar with shift=0 must return the plaintext unchanged."""
    plaintext = random.randbytes(20)
    assert cipher_encrypt(plaintext, 0, algo=Algo.CAESAR) == plaintext


@pytest.mark.parametrize("key", [b"K", b"SECRET", bytes(range(16))])
def test_vigenere_output_length_equals_input(key):
    """Vigenere: ciphertext length must equal plaintext length."""
    plaintext = random.randbytes(32)
    assert len(cipher_encrypt(plaintext, key, algo=Algo.VIGENERE)) == len(plaintext)


def test_vigenere_different_keys_produce_different_ciphertexts():
    """Vigenere: different keys must produce different ciphertexts."""
    plaintext = random.randbytes(20)
    ct1 = cipher_encrypt(plaintext, b"KEY1", algo=Algo.VIGENERE)
    ct2 = cipher_encrypt(plaintext, b"KEY2", algo=Algo.VIGENERE)
    assert ct1 != ct2