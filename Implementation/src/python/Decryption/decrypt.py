from common.classes import SecretKey, Grid
from Decryption.cipher_decrypt import cipher_decrypt
from Decryption.steganography_decrypt import extract_ciphertext


def decrypt(grid: Grid, secret_key: SecretKey) -> bytes:
    """
    Decrypt API — runs Level 2(Steganographic decryption) then Level 1(User implemented decryption).

    Step 1 (Level 2): extract_ciphertext(grid, secret_key)            -> ciphertext
    Step 2 (Level 1): cipher_decrypt(ciphertext, secret_key.cipher_cfg) -> plaintext

    Args:
        grid       : Obfuscated Grid received from the transmitter.
        secret_key : SecretKey carrying cipher_cfg + stencil coords + permutation σ.

    Returns:
        Recovered plaintext as bytes.
    """
    ciphertext = extract_ciphertext(grid, secret_key)
    return cipher_decrypt(ciphertext, secret_key.cipher_cfg)
