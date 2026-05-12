import random
from common.classes import GridCoord, GridShape, Stencil
from Keygen.stencils_skewconnected import generate_stencils_skewconnected


def _validate_assignment(
    subdomain_assignment: list[int],
    partition_list: list[int],
    capacity: list[int],
    k: int,
) -> None:
    """Validate that subdomain_assignment is well-formed and fits within subdomain capacities."""
    if len(subdomain_assignment) != len(partition_list):
        raise ValueError(
            f"subdomain_assignment length ({len(subdomain_assignment)}) must match "
            f"partition_list length ({len(partition_list)})."
        )
    remaining = capacity.copy()
    for i, (size, s_idx) in enumerate(zip(partition_list, subdomain_assignment)):
        if not (0 <= s_idx < k):
            raise ValueError(
                f"subdomain_assignment[{i}]={s_idx} is out of range [0, {k})."
            )
        if remaining[s_idx] < size:
            raise ValueError(
                f"Subdomain {s_idx} has insufficient capacity for partition {i} "
                f"of size {size}. Remaining: {remaining[s_idx]}."
            )
        remaining[s_idx] -= size


def _random_assignment(
    partition_list: list[int],
    capacity: list[int],
    k: int,
) -> list[int]:
    """ Randomly assign each partition to a subdomain with enough remaining capacity - Case A, 
    where user provides only the predicate function as subdomain definition.

    For each partition, shuffles subdomain indices and picks the first one with enough space,
    then decrements that subdomain's remaining capacity.

    Example:
        partition_list = [4, 2, 3],  capacity = [5, 6],  k = 2
        → partition 0 (size 4): shuffle → try subdomain 1 (cap 6 ≥ 4) → assign 1, remaining = [5, 2]
        → partition 1 (size 2): shuffle → try subdomain 0 (cap 5 ≥ 2) → assign 0, remaining = [3, 2]
        → partition 2 (size 3): shuffle → try subdomain 1 (cap 2 < 3) skip, 
        check with subdomain 0 (cap 3 ≥ 3) → assign to subdomain 0
        returns [1, 0, 0]
    """
    subdomain_choice_list: list[int] = []
    remaining = capacity.copy()
    for idx, size in enumerate(partition_list):
        indices = list(range(k))
        random.shuffle(indices)
        chosen_subdomain = None
        for s_idx in indices:
            if remaining[s_idx] >= size:
                chosen_subdomain = s_idx
                break
        if chosen_subdomain is None:
            raise ValueError(
                f"No subdomain has enough remaining space for partition {idx} of size {size}. "
                f"Remaining capacities per subdomain: {remaining}."
            )
        subdomain_choice_list.append(chosen_subdomain)
        remaining[chosen_subdomain] -= size
    return subdomain_choice_list


def generate_stencils_across_subdomains(
    partition_list: list[int],
    grid_shape: GridShape,
    subdomain_assignment: list[int] | None = None,
) -> list[Stencil]:
    """
    Distribute partitions across subdomains and place each group via a skew-connected walk.
    Supports two subdomain definition modes:
        Case A — predicate-based: GridShape.subdomain_predicates is set; the library
            computes and caches the coord sets. Assignment is random (subdomain_assignment=None).
        Case B — explicit coord lists: GridShape.subdomain_coord_list is set directly by
            the user. Assignment can be user-defined via subdomain_assignment.

    Args:
        partition_list        : list of group sizes, each >= 1.
        grid_shape            : GridShape with either subdomain_predicates or subdomain_coord_list set.
        subdomain_assignment  : Optional list of length len(partition_list).
                                subdomain_assignment[i] = j means partition i goes into subdomain j.
                                If None, assignment is chosen randomly.

    Returns:
        List of Stencil objects in original partition_list order.

    Raises:
        ValueError: if no subdomains are defined, assignment is invalid, or placement fails.
    """
    # Step 1: Resolve coord list.
    if grid_shape.subdomain_predicates and not grid_shape.subdomain_coord_list:
        # Case A (predicate-based): user supplied subdomain_predicates; derives and stores coord sets.
        grid_shape.subdomain_coord_list = [
            list(grid_shape.get_subdomain_coords(pred))
            for pred in grid_shape.subdomain_predicates
        ]

    # Case B (explicit lists):  user supplied subdomain_coord_list directly
    coord_list = grid_shape.subdomain_coord_list
    k = len(coord_list)
    if k == 0:
        raise ValueError(
            "No subdomains defined. Set subdomain_predicates or subdomain_coord_list on GridShape."
        )

    capacity = [len(c) for c in coord_list]

    # Step 2: Subdomain choice for each partition - Case A or Case B
    if subdomain_assignment is None:
        # Case A: randomly shuffle subdomains and greedily pick the first with enough space
        subdomain_choice_list = _random_assignment(partition_list, capacity, k)
    else:
        # Case B: validate the user-provided assignment, then use it directly
        _validate_assignment(subdomain_assignment, partition_list, capacity, k)
        subdomain_choice_list = subdomain_assignment

    # Step 3: Generate stencils per subdomain, place each into its original position.
    # Build (original_indices, sizes) groups per subdomain in one pass.
    subdomain_groups: list[tuple[list[int], list[int]]] = [([], []) for _ in range(k)]
    for partition_idx, (size, assigned_subdomain) in enumerate(zip(partition_list, subdomain_choice_list)):
        subdomain_groups[assigned_subdomain][0].append(partition_idx)
        subdomain_groups[assigned_subdomain][1].append(size)

    stencils: list[Stencil | None] = [None] * len(partition_list)
    for (partition_indices, subdomain_partition_list), subdomain_coords in zip(subdomain_groups, coord_list):
        if len(partition_indices) == 0:
            continue
        subdomain_stencils = generate_stencils_skewconnected(subdomain_partition_list, grid_shape, allowed_coords=set(subdomain_coords))
        for original_idx, stencil in zip(partition_indices, subdomain_stencils):
            stencils[original_idx] = stencil

    return stencils