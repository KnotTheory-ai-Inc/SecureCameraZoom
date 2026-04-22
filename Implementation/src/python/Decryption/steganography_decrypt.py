from typing import List
from common.classes import Grid, SecretKey


def steganography_decrypt_preconditions(stencils, partition_list: List[int]) -> None:
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


def steganography_decrypt(obfuscated_grid: Grid, secret_key: SecretKey) -> bytes:
    """
    Extract ciphertext bytes from the grid using Secret Key S.

    Args:
        obfuscated_grid : Grid containing the hidden ciphertext.
        secret_key      : SecretKey with stencils and partition.

    Returns:
        Ciphertext bytes recovered from the grid.
    """
    stencils = secret_key.stencils
    partition_list = secret_key.partition_list

    steganography_decrypt_preconditions(stencils, partition_list)

    extracted_ciphertext = bytearray()
    for stencil in stencils:
        for (row, col) in stencil.coords:
            extracted_ciphertext.append(obfuscated_grid.data[row][col])
    return bytes(extracted_ciphertext)