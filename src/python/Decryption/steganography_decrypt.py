from common.classes import Grid, SecretKey, StencilConfig


def steganography_decrypt_preconditions(stencils, partition_list: list[int]) -> None:
    """
    Validate that stencil lengths and partition list are compatible.

    Args:
        stencils       : stencil groups used for extraction.
        partition_list : partition sizes for each stencil.

    Raises:
        ValueError: if the number of stencils does not match partition list length,
                    or if any stencil length mismatches its partition size.
    """
    if len(stencils) != len(partition_list):
        raise ValueError(
            f"Number of stencils ({len(stencils)}) must equal number of partition sizes ({len(partition_list)})"
        )

    for i, stencil in enumerate(stencils):
        if stencil.len != partition_list[i]:
            raise ValueError(
                f"Stencil {i} length ({stencil.len}) does not match partition size ({partition_list[i]})"
            )


def steganography_decrypt(obfuscated_grid: Grid, secret_key: SecretKey, stencil_cfg: StencilConfig) -> bytes:
    """
    Extract ciphertext bytes from the grid using Secret Key S.

    Args:
        obfuscated_grid : Grid containing the hidden ciphertext.
        secret_key      : SecretKey with stencils and partition.
        stencil_cfg     : StencilConfig with permutation settings.

    Returns:
        Ciphertext bytes recovered from the grid.
    """
    stencils = secret_key.stencils
    partition_list = secret_key.partition_list

    steganography_decrypt_preconditions(stencils, partition_list)

    if stencil_cfg.enable_grid_permutation:
        # Apply inverse grid permutation to the stencils and partition list
        inverse_grid_permutation = [0] * len(secret_key.grid_permutation)
        for i, p in enumerate(secret_key.grid_permutation):
            inverse_grid_permutation[p] = i
        stencils = [stencils[i] for i in inverse_grid_permutation]
        partition_list = [partition_list[i] for i in inverse_grid_permutation]

    extracted_ciphertext = bytearray()
    for stencil in stencils:
        for coord in stencil.coords:
            coord_value = obfuscated_grid.get_value(coord)
            if coord_value == -1:
                raise ValueError(f"Grid coordinate {coord} is unset (value -1) during decryption.")
            extracted_ciphertext.append(coord_value)
    return bytes(extracted_ciphertext)