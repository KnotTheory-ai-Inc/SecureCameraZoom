from common.classes import Grid, SecretKey


def extract_ciphertext(obfuscated_grid: Grid, secret_key: SecretKey) -> bytes:
    """
    Extract ciphertext bytes from the grid using Secret Key S.
    - Input: obfuscated_grid (Grid), secret_key (SecretKey)
    - Output: ciphertext bytes recovered from grid based on SecretKey.
    """
    stencils = secret_key.stencils
    partition_list = secret_key.partition_list

    # Validate: each stencil's coord count must match its partition size
    for i, stencil in enumerate(stencils):
        if stencil.len != partition_list[i]:
            raise ValueError(
                f"Stencil {i} length ({stencil.len}) does not match partition size ({partition_list[i]})"
            )

    extracted_ciphertext = bytearray()
    for stencil in stencils:
        for (row, col) in stencil.coords:
            extracted_ciphertext.append(obfuscated_grid.data[row][col])
    return bytes(extracted_ciphertext)