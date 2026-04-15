from common.classes import CipherConfig


def cipher_encrypt(plaintext: bytes, cfg: CipherConfig) -> bytes:
    """
    Encrypt plaintext using the algorithm encoded in *cfg*.

    Args:
        plaintext : bytes to encrypt.
        cfg       : A CipherConfig subclass instance that carries all algorithm-
                    specific parameters (e.g. key, mode, IV/nonce) and implements the encrypt() method.

    Returns:
        Ciphertext as bytes.
    """
    return cfg.encrypt(plaintext)


