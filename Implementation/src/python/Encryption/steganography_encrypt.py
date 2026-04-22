import random
from typing import List
from common.classes import Grid, SecretKey


def generate_random_grid(m: int, n: int) -> Grid:
    """
    Fill a (m*n) grid with random byte values.

    Args:
        m : number of rows.
        n : number of columns.

    Returns:
        data[row][col] : Grid
    """
    data = []
    for _ in range(m):
        rand_row = bytearray(random.randbytes(n))
        data.append(rand_row)
    return Grid(rows=m, cols=n, data=data)


def do_partitioning(ciphertext: bytes, partition: List[int]) -> List[bytes]:
    """
    Partition ciphertext into groups based on the partition list.

    Args:
        ciphertext : bytes to partition.
        partition  : list of integers specifying partition sizes 
        (e.g. [1, 1, 3] means first 2 groups are 1 byte each, last group is 3 bytes).

    Returns:
        List of groups, each group is a bytes slice.
    """
    partitioned_ciphertext = []
    index = 0
    for p in partition:
        partition_bytes = ciphertext[index:index+p]
        partitioned_ciphertext.append(partition_bytes)
        index += p
    return partitioned_ciphertext


def steganography_encrypt_preconditions(ciphertext: bytes, stencils, partition_list: List[int]) -> None:
    """
    Validate that ciphertext length and stencil partitions are compatible.

    Args:
        ciphertext    : bytes to embed.
        stencils      : stencil groups used for embedding.
        partition_list : partition sizes for each stencil.

    Raises:
        ValueError: if the total stencil length or per-stencil partition sizes are invalid.
    """
    total_length_all_stencils = sum(stencil.len for stencil in stencils)
    if total_length_all_stencils != len(ciphertext):
        raise ValueError(
            f"Total stencil positions ({total_length_all_stencils}) must equal ciphertext length ({len(ciphertext)})"
        )

    if len(stencils) != len(partition_list):
        raise ValueError(
            f"Number of stencils ({len(stencils)}) must equal number of partition sizes ({len(partition_list)})"
        )

    for i, stencil in enumerate(stencils):
        if stencil.len != partition_list[i]:
            raise ValueError(
                f"Stencil {i} length ({stencil.len}) does not match partition size ({partition_list[i]})"
            )


def steganography_encrypt(grid: Grid, ciphertext: bytes, secret_key: SecretKey) -> Grid:
    """
    Embed ciphertext bytes into the grid at stencil positions.

    For each stencil group i, place ciphertext bytes starting from offset sum(partition[:i]).
    Each stencil position (row, col) receives one byte of ciphertext.

    Args:
        grid       : Grid to embed into.
        ciphertext : bytes to embed.
        secret_key : SecretKey with stencils and partition.

    Returns:
        Modified Grid with ciphertext hidden at stencil positions.

    Raises:
        ValueError: if total stencil positions != len(ciphertext).
    """
    stencils = secret_key.stencils
    partition_list = secret_key.partition_list
    obfuscated_grid = Grid(rows=grid.rows, cols=grid.cols, data=[bytearray(row) for row in grid.data])

    steganography_encrypt_preconditions(ciphertext, stencils, partition_list)

    # TODO: add permutation logic while embedding ciphertext into grid based on secret_key.permutation

    partitioned_ciphertext = do_partitioning(ciphertext, partition_list)

    # Embed cipher text into the grid
    for i, stencil in enumerate(stencils):
        ciphertext_partition = partitioned_ciphertext[i]

        for j, (row, col) in enumerate(stencil.coords):
            obfuscated_grid.data[row][col] = ciphertext_partition[j]

    return obfuscated_grid

