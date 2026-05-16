from common.classes import CipherConfig


def cipher_decrypt(ciphertext: bytes, cfg: CipherConfig) -> bytes:
    """
    Decrypt ciphertext using the algorithm choice in cfg.

    Args:
        ciphertext : bytes to decrypt.
        cfg        : A CipherConfig subclass instance that carries all algorithm-
                     specific parameters (e.g. key, mode, IV/nonce) and implements the decrypt() method.
    Returns:
        Plaintext as bytes.
    """
    return cfg.decrypt(ciphertext)

