from common.classes import SecretKey, Grid
from Decryption.cipher_decrypt import cipher_decrypt
from Decryption.steganography_decrypt import steganography_decrypt


def decrypt(obfuscated_grid: Grid, secret_key: SecretKey) -> bytes:
    """
    Decrypt API — runs Level 2(Steganographic decryption) then Level 1(User implemented decryption).

    Step 1 (steganography_decryption): steganography_decrypt(obfuscated_grid, secret_key)        -> ciphertext
    Step 2 (cipher_decryption): cipher_decrypt(ciphertext, secret_key.cipher_cfg) -> plaintext

    Args:
        obfuscated_grid : Obfuscated Grid received from the transmitter.
        secret_key : SecretKey

    Returns:
        Recovered plaintext as bytes.
    """
    ciphertext = steganography_decrypt(obfuscated_grid, secret_key)
    return cipher_decrypt(ciphertext, secret_key.cipher_cfg)
