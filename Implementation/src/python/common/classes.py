from abc import ABC
from enum import Enum

from Crypto.Cipher import AES


class Algo(Enum):
    AES = "aes"
    CAESAR = "caesar"
    VIGENERE = "vigenere"

class Key(ABC):
    """Abstract base class for all cipher keys.

    Each concrete subclass bundles every algorithm-specific parameter so
    callers pass a single Key object to cipher_encrypt / cipher_decrypt.
    """


class AESKey(Key):
    """Key + mode config for AES encryption/decryption.

    mode_params captures any extra keyword arguments required by the
    chosen AES mode and is forwarded verbatim to AES.new():

        AES.MODE_ECB  — no extra params
        AES.MODE_CBC  — iv=<16-byte IV>
        AES.MODE_CTR  — nonce=<bytes>
        AES.MODE_GCM  — nonce=<bytes>

    Example::

        AESKey(key_bytes, AES.MODE_CBC, iv=os.urandom(16))
        AESKey(key_bytes, AES.MODE_CTR, nonce=os.urandom(8))

    Attributes:
        raw_key     : AES key bytes (16, 24, or 32 bytes).
        mode        : AES block-cipher mode constant.
        mode_params : Dict of mode-specific kwargs (iv, nonce, ...).
    """

    def __init__(self, raw_key: bytes, mode: int = AES.MODE_ECB, **mode_params):
        if len(raw_key) not in (16, 24, 32):
            raise ValueError("AES key must be 16, 24, or 32 bytes.")
        self.raw_key = raw_key
        self.mode = mode
        self.mode_params: dict = mode_params


class CaesarKey(Key):
    """Key for the Caesar byte-shift cipher.

    Attributes:
        shift : Integer shift in the range [0, 255].
    """

    def __init__(self, shift: int):
        if not isinstance(shift, int):
            raise TypeError("Caesar shift must be an int.")
        self.shift = shift


class VigenereKey(Key):
    """Key for the Vigenere byte-shift cipher.

    Attributes:
        keyword : Non-empty bytes used as the repeating key.
    """

    def __init__(self, keyword: bytes):
        if not keyword:
            raise ValueError("Vigenere keyword must not be empty.")
        self.keyword = keyword
