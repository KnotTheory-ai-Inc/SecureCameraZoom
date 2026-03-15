import random
import pytest
from Crypto.Util.Padding import pad, unpad
from common.constants import AES_256_KEY_SIZE, AES_BLOCK_SIZE, AES_128_KEY_SIZE
from Encryption.cipher_encrypt import cipher_encrypt
from Decryption.cipher_decrypt import cipher_decrypt


@pytest.mark.parametrize("plain_text_len", [1, 5, 16, 17, 32, 100])
@pytest.mark.parametrize("key_size", [AES_256_KEY_SIZE, AES_128_KEY_SIZE])
def test_decrypt_recovers_original_plaintext(plain_text_len, key_size):
    """Round-trip: decrypt(encrypt(pad(plaintext))) must equal original plaintext."""
    key = random.randbytes(key_size)
    plaintext = random.randbytes(plain_text_len)
    padded_plaintext = pad(plaintext, AES_BLOCK_SIZE)
    ciphertext = cipher_encrypt(padded_plaintext, key)
    decrypted = unpad(cipher_decrypt(ciphertext, key), AES_BLOCK_SIZE)
    assert decrypted == plaintext
