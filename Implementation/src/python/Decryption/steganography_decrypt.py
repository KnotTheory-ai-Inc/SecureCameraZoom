def extract_ciphertext(grid: Grid, secret_key: SecretKey) -> bytes:
    """
    Extract ciphertext bytes from the grid using Secret Key S.
    - Input: grid (Grid), secret_key (SecretKey)
    - Output: ciphertext bytes recovered from grid based on SecretKey.
    """