import random  # TODO: replace with DRBG implementation
from math import prod
from common.classes import CipherConfig, GridCoord, GridShape, SecretKey, Stencil, StencilCoord, StencilCoords, StencilConfig


def generate_partition_list(total_bytes: int, num_partitions: int) -> list[int]:
    """
    Generate a partition of length n for stencil key.

    Args:
        total_bytes : the cipher text length
        num_partitions := number of partitions to create.

    Returns:
        Partitioned Cipher Text.
    """
    partition_list = []

    if num_partitions < 1 or num_partitions > total_bytes:
        raise ValueError(
            f"num_partitions={num_partitions} must be between 1 and total_bytes={total_bytes}."
        )

    remaining = total_bytes
    for i in range(num_partitions - 1):
        # max_chunk: leave at least 1 for each of the remaining partitions after this one
        max_chunk = remaining - (num_partitions - 1 - i)
        partition_len = random.randint(1, max_chunk)
        partition_list.append(partition_len)
        remaining -= partition_len
    partition_list.append(remaining)

    return partition_list


def generate_stencils_skewconnected(partition_list: list[int], grid_shape: GridShape) -> list[Stencil]:
    """
    For each partition group, place p coords using a skew-connected random walk:
    pick a random start, then step in a random cardinal or diagonal direction each time.

    Args:
        partition_list : list of group sizes, each >= 1.
        grid_shape     : Shape of Grid, used for bounds and neighbor logic.

    Returns:
        List of Stencil objects, one per partition group.

    Raises:
        ValueError: if placement fails after MAX_ATTEMPTS.
    """

    if sum(partition_list) > prod(grid_shape.shape):
        raise ValueError(
            f"Grid {grid_shape.shape} too small for {sum(partition_list)} total positions."
        )

    MAX_ATTEMPTS = 10000

    free: set = grid_shape.all_coords()
    all_stencils: list[Stencil] = []

    for p in partition_list:
        stencil_coords: StencilCoords = []

        for _ in range(MAX_ATTEMPTS):
            start: StencilCoord = grid_shape.get_random_coord()
            if start not in free:
                continue
            stencil_coords = [start]

            current_coord: StencilCoord = start
            for _ in range(p - 1):  # add (p-1) more coords one step at a time
                # get_neighbors handles bounds + all directions for any N-D grid
                valid_neighbors = [
                    nb for nb in grid_shape.get_neighbors(current_coord)
                    if nb in free and nb not in stencil_coords
                ]
                if not valid_neighbors:
                    stencil_coords = []
                    break
                next_coord: StencilCoord = random.choice(valid_neighbors)
                stencil_coords.append(next_coord)
                current_coord = next_coord

            if len(stencil_coords) == p:
                break

        if not stencil_coords:
            raise ValueError(
                f"Could not place stencil of size {p} after {MAX_ATTEMPTS} attempts."
            )

        # remove placed coords from free
        free.difference_update(stencil_coords)
        all_stencils.append(Stencil(shape="skewconnected", len=len(stencil_coords), coords=stencil_coords))

    # check that number of stencils matches num_partitions = len(partition_list)
    assert len(all_stencils) == len(partition_list), (
        f"Expected {len(partition_list)} stencil groups, got {len(all_stencils)}."
    )

    # check that each stencil's len matches the partition size
    for i, stencil in enumerate(all_stencils):
        assert stencil.len == partition_list[i], (
            f"Stencil {i}: expected len={partition_list[i]}, got {stencil.len}."
        )

    return all_stencils


def keygen(
    stencil_cfg: StencilConfig,
    cipher_cfg: CipherConfig,
    partition_list: list[int] | None = None,
    stencils: list[Stencil] | None = None,
    ) -> SecretKey:
    """
    Bundle all stencil key material into a SecretKey.


    Args:
        stencil_cfg    : StencilConfig instance (encapsulates total_bytes, num_partitions, grid_shape)
        cipher_cfg     : CipherConfig subclass (user-defined cipher parameters)
        partition_list : Optional pre-computed partition list. If None, generated internally.
        stencils       : Optional pre-computed stencils. If None, generated internally.

    Returns:
        SecretKey dataclass bundling all key material.
    """

    if partition_list is None:
        partition_list = generate_partition_list(stencil_cfg.total_bytes, stencil_cfg.num_partitions)

    if stencils is None:
        stencils = generate_stencils_skewconnected(partition_list, stencil_cfg.grid_shape)
    
    if stencil_cfg.enable_cipher_permutation == True:
        cipher_permutation = list(range(stencil_cfg.total_bytes))
        random.shuffle(cipher_permutation)

    if stencil_cfg.enable_grid_permutation == True:
        grid_permutation = list(range(stencil_cfg.num_partitions))
        random.shuffle(grid_permutation)

    return SecretKey(
        partition_list=partition_list,
        stencils=stencils,
        cipher_cfg=cipher_cfg,
        cipher_permutation=cipher_permutation if stencil_cfg.enable_cipher_permutation else None,
        grid_permutation=grid_permutation if stencil_cfg.enable_grid_permutation else None,
    )

