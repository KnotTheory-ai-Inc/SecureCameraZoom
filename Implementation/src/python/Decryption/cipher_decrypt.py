from Crypto.Cipher import AES
from common.classes import Algo


def cipher_decrypt(ciphertext: bytes, key_K, algo: Algo = Algo.AES, aes_mode: int = AES.MODE_ECB) -> bytes:
    """
    Decrypt ciphertext using the specified algorithm.

    Args:
        ciphertext : bytes to decrypt.
        key_K      : key material — type depends on algo:
                       AES      -> bytes (16/24/32 bytes)
                       MHKC     -> tuple (W: list[int], q: int, r: int) — private key
                       CAESAR   -> int (shift, 0-255)
                       VIGENERE -> bytes (repeating keyword)
        algo       : Algo enum member selecting the cipher.
        aes_mode   : AES block-cipher mode (ignored for non-AES algos).

    Returns:
        Plaintext as bytes.
    """
    if algo == Algo.AES:
        return _aes_decrypt(ciphertext, key_K, aes_mode)
    elif algo == Algo.CAESAR:
        return _caesar_decrypt(ciphertext, key_K)
    elif algo == Algo.VIGENERE:
        return _vigenere_decrypt(ciphertext, key_K)
    else:
        raise ValueError(f"Unsupported algorithm: {algo}")


# ---------------------------------------------------------------------------
# Private implementations
# ---------------------------------------------------------------------------

def _aes_decrypt(ciphertext: bytes, key_K: bytes, mode: int) -> bytes:
    cipher = AES.new(key_K, mode)
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
