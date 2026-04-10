from Crypto.Cipher import AES
from common.classes import Algo


def cipher_encrypt(plaintext: bytes, key_K, algo: Algo = Algo.AES, aes_mode: int = AES.MODE_ECB) -> bytes:
    """
    Encrypt plaintext using the specified algorithm.

    Args:
        plaintext : bytes to encrypt.
        key_K     : key material — type depends on algo:
                      AES      -> bytes (16/24/32 bytes)
                      CAESAR   -> int (shift, 0-255)
                      VIGENERE -> bytes (repeating keyword)
        algo      : Algo enum member selecting the cipher.
        aes_mode  : AES block-cipher mode (ignored for non-AES algos).

    Returns:
        Ciphertext as bytes.
    """
    if algo == Algo.AES:
        return _aes_encrypt(plaintext, key_K, aes_mode)
    elif algo == Algo.CAESAR:
        return _caesar_encrypt(plaintext, key_K)
    elif algo == Algo.VIGENERE:
        return _vigenere_encrypt(plaintext, key_K)
    else:
        raise ValueError(f"Unsupported algorithm: {algo}")


def _aes_encrypt(plaintext: bytes, key_K: bytes, mode: int) -> bytes:
    cipher = AES.new(key_K, mode)
    return cipher.encrypt(plaintext)


def _caesar_encrypt(plaintext: bytes, shift: int) -> bytes:
    """
    Caesar cipher: each byte shifted by `shift` (mod 256).
    """
    if not isinstance(shift, int):
        raise TypeError("Caesar key must be an int.")
    return bytes((b + shift) % 256 for b in plaintext)


def _vigenere_encrypt(plaintext: bytes, key: bytes) -> bytes:
    """
    Vigenère cipher: byte[i] shifted by key[i % len(key)] (mod 256).
    """
    if not key:
        raise ValueError("Vigenère key must not be empty.")
    key_len = len(key)
    return bytes((b + key[i % key_len]) % 256 for i, b in enumerate(plaintext))


