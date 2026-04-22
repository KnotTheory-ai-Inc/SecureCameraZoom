from common.classes import SecretKey, Grid, GridSize
from Encryption.cipher_encrypt import cipher_encrypt
from Encryption.steganography_encrypt import generate_random_grid, steganography_encrypt


def encrypt(plaintext: bytes, secret_key: SecretKey, grid_size: GridSize, grid: Grid = None) -> Grid:
    """
    Encrypt API — runs Level 1(User implemented encryption) then Level 2(Steganographic encryption).

    Step 1 (Level 1): cipher_encrypt(plaintext, secret_key.cipher_cfg) -> ciphertext
    Step 2 (Level 2): embed ciphertext into a random rows * cols grid   -> Obfuscated Grid

    Args:
        plaintext  : raw bytes to encrypt
        secret_key : SecretKey type
        grid_size   : GridSize type
        grid       : 2D list of bytes, with same dimensions as grid_size (Optional)

    Returns:
        Obfuscated Grid with ciphertext hidden at stencil positions.
    """
    ciphertext = cipher_encrypt(plaintext, secret_key.cipher_cfg)
    if grid is None:
        grid = generate_random_grid(grid_size.rows, grid_size.cols)
    return steganography_encrypt(grid, ciphertext, secret_key)
