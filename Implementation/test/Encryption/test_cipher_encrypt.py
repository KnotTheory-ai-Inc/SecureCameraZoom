import random
import pytest
from Crypto.Util.Padding import pad
from common.constants import AES_256_KEY_SIZE, AES_BLOCK_SIZE, AES_128_KEY_SIZE
from Encryption.cipher_encrypt import cipher_encrypt


@pytest.mark.parametrize("plain_text_len", [1, 5, 16, 17, 32, 100])
@pytest.mark.parametrize("key_size", [AES_256_KEY_SIZE, AES_128_KEY_SIZE])
def test_ciphertext_length_equals_plaintext_length(plain_text_len, key_size):
    """ECB mode: ciphertext length must equal padded plaintext length (block-aligned)."""
    key = random.randbytes(key_size)
    plaintext = random.randbytes(plain_text_len)
    padded_plaintext = pad(plaintext, AES_BLOCK_SIZE)
    ciphertext = cipher_encrypt(padded_plaintext, key)
    assert len(ciphertext) == len(padded_plaintext)


def test_different_keys_same_plaintexts():
    """Same plaintext encrypted with different keys must produce different ciphertexts."""
    plaintext = random.randbytes(24)
    padded_plaintext = pad(plaintext, AES_BLOCK_SIZE)
    ciphertext1 = cipher_encrypt(padded_plaintext, random.randbytes(AES_256_KEY_SIZE))
    ciphertext2 = cipher_encrypt(padded_plaintext, random.randbytes(AES_256_KEY_SIZE))
    assert ciphertext1 != ciphertext2


