from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import random
from common.constants import AES_256_KEY_SIZE, AES_BLOCK_SIZE


def cipher_encrypt(plaintext: bytes, key_K: bytes, mode: int = AES.MODE_ECB) -> bytes:
    """
    Encrypt plaintext using AES.
    - Input: plaintext (bytes), key_K (AES-key), mode (AES-mode)
    - Output: ciphertext (bytes)
    """
    cipher = AES.new(key_K, mode)
    ciphertext = cipher.encrypt(plaintext)
    return ciphertext


