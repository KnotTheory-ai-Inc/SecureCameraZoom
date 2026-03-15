from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import random
from common.constants import AES_256_KEY_SIZE, AES_BLOCK_SIZE

def cipher_decrypt(ciphertext: bytes, key_K: bytes, mode: int = AES.MODE_ECB) -> bytes:
    """
    Decrypt ciphertext using AES.
    - Input: ciphertext (bytes), key_K (AES key), mode (AES.MODE_ECB)
    - Output: plaintext (bytes)
    """
    cipher = AES.new(key_K, mode)
    plaintext = cipher.decrypt(ciphertext)
    return plaintext
