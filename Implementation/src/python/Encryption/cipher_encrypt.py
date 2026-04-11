from Crypto.Cipher import AES
from common.classes import AESConfig, CaesarConfig, CipherConfig, VigenereConfig


def cipher_encrypt(plaintext: bytes, cfg: CipherConfig) -> bytes:
    """
    Encrypt plaintext using the algorithm encoded in *key*.

    Args:
        plaintext : bytes to encrypt.
        key       : A CipherConfig subclass instance that carries all algorithm-
                    specific parameters:
                      AESConfig      — raw_key, mode, **mode_params (iv, nonce, ...)
                      CaesarConfig   — shift (int, 0-255)
                      VigenereConfig — keyword (bytes)

    Returns:
        Ciphertext as bytes.
    """
    if isinstance(cfg, AESConfig):
        return _aes_encrypt(plaintext, cfg.raw_key, cfg.mode, cfg.mode_params)
    elif isinstance(cfg, CaesarConfig):
        return _caesar_encrypt(plaintext, cfg.shift)
    elif isinstance(cfg, VigenereConfig):
        return _vigenere_encrypt(plaintext, cfg.keyword)
    else:
        raise ValueError(f"Unsupported config type: {type(cfg).__name__}")


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


