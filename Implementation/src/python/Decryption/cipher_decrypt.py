from Crypto.Cipher import AES
from common.classes import AESKey, CaesarKey, Key, VigenereKey


def cipher_decrypt(ciphertext: bytes, key: Key) -> bytes:
    """
    Decrypt ciphertext using the algorithm encoded in *key*.

    Args:
        ciphertext : bytes to decrypt.
        key        : A Key subclass instance that carries all algorithm-
                     specific parameters:
                       AESKey      — raw_key, mode, **mode_params (iv, nonce, ...)
                       CaesarKey   — shift (int, 0-255)
                       VigenereKey — keyword (bytes)

    Returns:
        Plaintext as bytes.
    """
    if isinstance(key, AESKey):
        return _aes_decrypt(ciphertext, key.raw_key, key.mode, key.mode_params)
    elif isinstance(key, CaesarKey):
        return _caesar_decrypt(ciphertext, key.shift)
    elif isinstance(key, VigenereKey):
        return _vigenere_decrypt(ciphertext, key.keyword)
    else:
        raise ValueError(f"Unsupported key type: {type(key).__name__}")


def _aes_decrypt(ciphertext: bytes, raw_key: bytes, mode: int, mode_params: dict) -> bytes:
    cipher = AES.new(raw_key, mode, **mode_params)
    return cipher.decrypt(ciphertext)


def _caesar_decrypt(ciphertext: bytes, shift: int) -> bytes:
    """
    Caesar cipher: each byte un-shifted by `shift` (mod 256).
    """
    if not isinstance(shift, int):
        raise TypeError("Caesar key must be an int.")
    return bytes((b - shift) % 256 for b in ciphertext)


def _vigenere_decrypt(ciphertext: bytes, key: bytes) -> bytes:
    """
    Vigenère cipher: byte[i] un-shifted by key[i % len(key)] (mod 256).
    """
    if not key:
        raise ValueError("Vigenère key must not be empty.")
    key_len = len(key)
    return bytes((b - key[i % key_len]) % 256 for i, b in enumerate(ciphertext))
