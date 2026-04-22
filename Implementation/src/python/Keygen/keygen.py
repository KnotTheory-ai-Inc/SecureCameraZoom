import secrets
import random  # TODO: replace with DRBG implementation
from typing import List, Tuple
from common.classes import CipherConfig, SecretKey, GridSize, Stencil, StencilCoord, StencilCoords


def generate_partition_list(total_bytes: int, num_partitions: int) -> List[int]:
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


def generate_stencils_skewconnected(partition_list: List[int], grid_size: GridSize) -> List[Stencil]:
    """
    For each partition group, place p coords using a skew-connected random walk:
    pick a random start, then step in a random cardinal or diagonal direction each time.

    Args:
        partition_list : list of group sizes, each >= 1.
        grid_size       : grid bounds.

    Returns:
        List of Stencil objects, one per partition group.

    Raises:
        ValueError: if placement fails after MAX_ATTEMPTS.
    """
    rows, cols = grid_size.rows, grid_size.cols
    if sum(partition_list) > rows * cols:
        raise ValueError(
            f"Grid ({rows}x{cols}) too small for {sum(partition_list)} total positions."
        )

    # 8-directional: cardinal + diagonal (skew connectivity)
    DIRECTIONS: List[StencilCoord] = [(0, 1), (0, -1), (1, 0), (-1, 0),
                                       (1, 1), (1, -1), (-1, 1), (-1, -1)]
    MAX_ATTEMPTS = 10000

    occupied: set = set()
    free: set = {(r, c) for r in range(rows) for c in range(cols)}
    all_stencils: List[Stencil] = []

    for p in partition_list:
        stencil_coords: StencilCoords = []

        for _ in range(MAX_ATTEMPTS):
            start: StencilCoord = random.choice(list(free))  # always unoccupied
            stencil_coords = [start]

            for _ in range(p - 1):  # add (p-1) more coords one step at a time
                last: StencilCoord = stencil_coords[-1]
                valid_dirs = [
                    (dr, dc) for dr, dc in DIRECTIONS
                    if (last[0] + dr, last[1] + dc) in free
                    and (last[0] + dr, last[1] + dc) not in stencil_coords
                ]
                if not valid_dirs:
                    stencil_coords = []
                    break
                dr, dc = random.choice(valid_dirs)
                next_coord: StencilCoord = (last[0] + dr, last[1] + dc)
                stencil_coords.append(next_coord)

            if len(stencil_coords) == p:
                break

        if not stencil_coords:
            raise ValueError(
                f"Could not place stencil of size {p} after {MAX_ATTEMPTS} attempts."
            )

        # add chosen stencil coord to occupied and remove from free
        occupied.update(stencil_coords)
        free -= set(stencil_coords)
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


def keygen( total_bytes: int,
            num_partitions: int,
            grid_size: GridSize,
            cipher_cfg: CipherConfig,
            partition_list:List[int] | None = None,
            stencils: List[Stencil] | None = None,
            ) -> SecretKey:
    """
    Bundle all stencil key material into a SecretKey.

    Args:
        total_bytes     : length of the ciphertext.
        num_partitions  : number of partitions to create.
        grid_size       : grid size.
        cipher_cfg      : CipherConfig subclass.
        partition_list  : optional pre-computed partition. Generated internally if None.
        stencils        : optional pre-computed stencils. Generated internally if None.

    Returns:
        SecretKey dataclass.
    """
    if partition_list is None:
        partition_list = generate_partition_list(total_bytes, num_partitions)

    if stencils is None:
        stencils = generate_stencils_skewconnected(partition_list, grid_size)

    return SecretKey(
        partition_list=partition_list,
        stencils=stencils,
        cipher_cfg=cipher_cfg,
    )

