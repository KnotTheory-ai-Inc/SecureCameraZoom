import random  # TODO: replace with DRBG implementation
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


def generate_stencils_skewconnected(
    partition_list: list[int],
    grid_shape: GridShape,
    allowed_coords: set[GridCoord] | None = None,
) -> list[Stencil]:
    """
    For each partition group, place p coords using a skew-connected random walk:
    pick a random start, then step in a random cardinal or diagonal direction each time.

    Args:
        partition_list : list of group sizes, each >= 1.
        grid_shape     : Shape of Grid, used for bounds and neighbor logic.
        allowed_coords : Optional set of coords to restrict placement to (e.g. a subdomain).
                         If None, the entire grid is used.

    Returns:
        List of Stencil objects, one per partition group.

    Raises:
        ValueError: if placement fails after MAX_ATTEMPTS.
    """

    free: set = allowed_coords.copy() if allowed_coords is not None else grid_shape.all_coords()

    if sum(partition_list) > len(free):
        raise ValueError(
            f"Available space ({len(free)} coords) too small for {sum(partition_list)} total positions."
        )

    MAX_ATTEMPTS = 10000
    all_stencils: list[Stencil] = []

    for p in partition_list:
        stencil_coords: StencilCoords = []

        for _ in range(MAX_ATTEMPTS):
            start: StencilCoord = random.choice(list(free))
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


def generate_stencils_across_subdomains(
    partition_list: list[int],
    grid_shape: GridShape,
) -> list[Stencil]:
    """
    Distribute partitions randomly across user-defined subdomains, then run a
    skew-connected walk within each subdomain's coordinate set.

    Args:
        partition_list : list of group sizes, each >= 1.
        grid_shape     : GridShape with subdomain_predicates already set.

    Returns:
        List of Stencil objects in original partition_list order.

    Raises:
        ValueError: if any partition cannot be assigned because no subdomain has
                    enough remaining space for it.
    """
    predicates = grid_shape.subdomain_predicates
    k = len(predicates)

    # Compute coordinate set and capacity for each subdomain(predicate)
    subdomain_coords: list[set[GridCoord]] = []
    capacity: list[int] = []
    for pred in predicates:
        coords = grid_shape.get_subdomain_coords(pred)
        subdomain_coords.append(coords)
        capacity.append(len(coords))

    # Assign each partition to a subdomain: randomly pick one, retry if it lacks space
    # assigned_subdomain[i] = subdomain index that partition i was assigned to
    assigned_subdomain: list[int] = []
    for idx, size in enumerate(partition_list):
        subdomain_indices = list(range(k))
        random.shuffle(subdomain_indices)

        chosen_subdomain = None
        for subdomain_idx in subdomain_indices:
            if capacity[subdomain_idx] >= size:
                chosen_subdomain = subdomain_idx
                break

        if chosen_subdomain is None:
            raise ValueError(
                f"No subdomain has enough remaining space for partition of size {size}. "
                f"Remaining capacities per subdomain: {capacity}."
            )

        assigned_subdomain.append(chosen_subdomain)
        capacity[chosen_subdomain] -= size

    # Generate stencils per subdomain and record them by original partition index
    stencil_map: dict[int, Stencil] = {}
    for s_idx, coords in enumerate(subdomain_coords):
        part_indices = [i for i, s in enumerate(assigned_subdomain) if s == s_idx]
        if not part_indices:
            continue
        sub_sizes = [partition_list[j] for j in part_indices]
        sub_stencils = generate_stencils_skewconnected(sub_sizes, grid_shape, allowed_coords=coords)
        for original_idx, stencil in zip(part_indices, sub_stencils):
            stencil_map[original_idx] = stencil

    # Return stencils in partition_list order
    return [stencil_map[i] for i in range(len(partition_list))]


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
        grid_shape = stencil_cfg.grid_shape
        if grid_shape.subdomain_predicates != []:
            # generate stencils across subdomains defined by grid_shape.subdomain_predicates
            stencils = generate_stencils_across_subdomains(partition_list, grid_shape)
        else:
            # generate stencils across entire grid without subdomain constraints
            stencils = generate_stencils_skewconnected(partition_list, grid_shape)
    
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




