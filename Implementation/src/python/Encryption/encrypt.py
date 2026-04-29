from common.classes import SecretKey, Grid, GridShape, StencilConfig
from Encryption.cipher_encrypt import cipher_encrypt
from Encryption.steganography_encrypt import generate_random_grid, steganography_encrypt


def encrypt(plaintext: bytes, secret_key: SecretKey, stencil_cfg: StencilConfig, grid: Grid = None) -> Grid:
    """
    Encrypt API — runs Level 1(User implemented encryption) then Level 2(Steganographic encryption).

    Step 1 (Level 1): cipher_encrypt(plaintext, secret_key.cipher_cfg) -> ciphertext
    Step 2 (Level 2): embed ciphertext into a random rows * cols grid   -> Obfuscated Grid

    Args:
        plaintext  : raw bytes to encrypt
        secret_key : SecretKey type
        stencil_cfg : StencilConfig type
        grid       : Grid for steganography. If None, a random grid is generated internally.

    Returns:
        Obfuscated Grid with ciphertext hidden at stencil positions.
    """
    ciphertext = cipher_encrypt(plaintext, secret_key.cipher_cfg)
    if stencil_cfg.enable_cipher_permutation == True:
        permuted_ciphertext = bytes(ciphertext[i] for i in secret_key.cipher_permutation)
        ciphertext = permuted_ciphertext
    if grid is None:
        grid = generate_random_grid(stencil_cfg.grid_shape)
    return steganography_encrypt(grid, ciphertext, secret_key, stencil_cfg)
