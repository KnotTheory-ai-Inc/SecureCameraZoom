from Crypto.Cipher import AES
from common.classes import AESKey, CaesarKey, Key, VigenereKey


def cipher_encrypt(plaintext: bytes, key: Key) -> bytes:
    """
    Encrypt plaintext using the algorithm encoded in *key*.

    Args:
        plaintext : bytes to encrypt.
        key       : A Key subclass instance that carries all algorithm-
                    specific parameters:
                      AESKey      — raw_key, mode, **mode_params (iv, nonce, ...)
                      CaesarKey   — shift (int, 0-255)
                      VigenereKey — keyword (bytes)

    Returns:
        Ciphertext as bytes.
    """
    if isinstance(key, AESKey):
        return _aes_encrypt(plaintext, key.raw_key, key.mode, key.mode_params)
    elif isinstance(key, CaesarKey):
        return _caesar_encrypt(plaintext, key.shift)
    elif isinstance(key, VigenereKey):
        return _vigenere_encrypt(plaintext, key.keyword)
    else:
        raise ValueError(f"Unsupported key type: {type(key).__name__}")


def _aes_encrypt(plaintext: bytes, raw_key: bytes, mode: int, mode_params: dict) -> bytes:
    cipher = AES.new(raw_key, mode, **mode_params)
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


