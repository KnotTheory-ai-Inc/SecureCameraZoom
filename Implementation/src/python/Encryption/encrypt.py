from common.classes import SecretKey, Grid
from Encryption.cipher_encrypt import cipher_encrypt
from Encryption.steganography_encrypt import generate_random_grid, embed_ciphertext


def encrypt(plaintext: bytes, secret_key: SecretKey, rows: int, cols: int) -> Grid:
    """
    Encrypt API — runs Level 1(User implemented encryption) then Level 2(Steganographic encryption).

    Step 1 (Level 1): cipher_encrypt(plaintext, secret_key.cipher_cfg) -> ciphertext
    Step 2 (Level 2): embed ciphertext into a random rows * cols grid   -> Obfuscated Grid

    Args:
        plaintext  : raw bytes to encrypt.
        secret_key : SecretKey carrying cipher_cfg + stencil coords + permutation σ.
        rows, cols : dimensions of the obfuscated grid to generate.

    Returns:
        Obfuscated Grid with ciphertext hidden at stencil positions.
    """
    ciphertext = cipher_encrypt(plaintext, secret_key.cipher_cfg)
    grid = generate_random_grid(rows, cols)
    return embed_ciphertext(grid, ciphertext, secret_key)
