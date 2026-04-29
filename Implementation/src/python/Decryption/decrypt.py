from common.classes import SecretKey, Grid, StencilConfig
from Decryption.cipher_decrypt import cipher_decrypt
from Decryption.steganography_decrypt import steganography_decrypt

def decrypt_preconditions(obfuscated_grid: Grid, secret_key: SecretKey, stencil_cfg: StencilConfig):
    """
    Preconditions for decryption.

     - Total stencil positions must equal the number of bytes hidden in the grid.
     - Number of stencils must equal number of partition sizes.
     - Each stencil's length must match its corresponding partition size.

     Args:
        obfuscated_grid : Obfuscated Grid received from the transmitter.
        secret_key : SecretKey
        stencil_cfg : StencilConfig type

    Raises:
        ValueError: if any precondition is violated.
    """
    total_length_all_stencils = sum(stencil.len for stencil in secret_key.stencils)
    if total_length_all_stencils != sum(secret_key.partition_list):
        raise ValueError(
            f"Total stencil positions ({total_length_all_stencils}) must equal total partition size ({sum(secret_key.partition_list)})"
        )

    if len(secret_key.stencils) != len(secret_key.partition_list):
        raise ValueError(
            f"Number of stencils ({len(secret_key.stencils)}) must equal number of partition sizes ({len(secret_key.partition_list)})"
        )

    for i, stencil in enumerate(secret_key.stencils):
        if stencil.len != secret_key.partition_list[i]:
            raise ValueError(
                f"Stencil {i} length ({stencil.len}) does not match partition size ({secret_key.partition_list[i]})"
            )

    expected_shape = stencil_cfg.grid_shape.shape
    out_of_bounds = [
        coord for coord in obfuscated_grid.data
        if len(coord) != len(expected_shape)
        or any(coord[i] >= expected_shape[i] for i in range(len(expected_shape)))
    ]
    if out_of_bounds:
        raise ValueError(
            f"Grid contains {len(out_of_bounds)} coordinate(s) out of bounds for expected shape {expected_shape}. "
            f"First offending coord: {out_of_bounds[0]}"
        )

def decrypt(obfuscated_grid: Grid, secret_key: SecretKey, stencil_cfg: StencilConfig) -> bytes:
    """
    Decrypt API — runs Level 2(Steganographic decryption) then Level 1(User implemented decryption).

    Step 1 (steganography_decryption): steganography_decrypt(obfuscated_grid, secret_key)        -> ciphertext
    Step 2 (cipher_decryption): cipher_decrypt(ciphertext, secret_key.cipher_cfg) -> plaintext

    Args:
        obfuscated_grid : Obfuscated Grid received from the transmitter.
        secret_key : SecretKey
        stencil_cfg : StencilConfig type

    Returns:
        Recovered plaintext as bytes.
    """
    decrypt_preconditions(obfuscated_grid, secret_key, stencil_cfg)
    ciphertext = steganography_decrypt(obfuscated_grid, secret_key, stencil_cfg)
    if stencil_cfg.enable_cipher_permutation:
        inverse_permutation = [0] * len(secret_key.cipher_permutation)
        for i, p in enumerate(secret_key.cipher_permutation):
            inverse_permutation[p] = i
        ciphertext = bytes(ciphertext[i] for i in inverse_permutation)
    return cipher_decrypt(ciphertext, secret_key.cipher_cfg)
