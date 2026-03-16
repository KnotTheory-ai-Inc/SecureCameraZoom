import random
import pytest
from Crypto.Util.Padding import pad, unpad
from common.constants import AES_256_KEY_SIZE, AES_128_KEY_SIZE, AES_BLOCK_SIZE
from Encryption.cipher_encrypt import cipher_encrypt
from Decryption.cipher_decrypt import cipher_decrypt


@pytest.mark.parametrize("key_size", [AES_128_KEY_SIZE, AES_256_KEY_SIZE])
@pytest.mark.parametrize("plain_text_len", [1, 15, 16, 17, 64, 200])
def test_encrypt_decrypt_roundtrip(plain_text_len, key_size):
    """Encrypt and decrypt to recover original plaintext back."""
    key = random.randbytes(key_size)
    plaintext = random.randbytes(plain_text_len)

    padded_plaintext = pad(plaintext, AES_BLOCK_SIZE)
    ciphertext = cipher_encrypt(padded_plaintext, key)
    decrypted_text = cipher_decrypt(ciphertext, key)
    unpadded_text = unpad(decrypted_text, AES_BLOCK_SIZE)

    assert unpadded_text == plaintext
