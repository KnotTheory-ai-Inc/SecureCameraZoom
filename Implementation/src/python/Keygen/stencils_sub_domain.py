import random
from common.classes import GridCoord, GridShape, Stencil
from Keygen.stencils_skewconnected import generate_stencils_skewconnected


def _is_disjoint(subdomain_coord_list: list[list]) -> bool:
    """Return True if all subdomain coordinate sets are pairwise disjoint, False otherwise."""
    seen_coords: set = set()
    for coords in subdomain_coord_list:
        coord_set = set(coords)
        if seen_coords & coord_set:
            return False
        seen_coords |= coord_set
    return True


def _validate_assignment(
    subdomain_assignment: list[int],
    partition_list: list[int],
    subdomain_capacity_list: list[int],
    num_of_subdomains: int,
) -> None:
    """Validate that subdomain_assignment is well-formed and fits within subdomain capacities.

    Performs two checks in order:

    1. Length check — subdomain_assignment must have one entry per partition:
           len(subdomain_assignment) == len(partition_list)
       Each entry subdomain_assignment[i] is the subdomain index that partition i
       will be placed into.

    2. Capacity check — simulates the placement in partition order and verifies that
       each subdomain has enough remaining coordinates to absorb its assigned partitions.
       Remaining capacity is decremented as each partition is "consumed", so earlier
       partitions reduce the available space seen by later ones in the same subdomain.

    Args:
        subdomain_assignment : User-supplied assignment list (Case B). Length must equal
                               len(partition_list). Each value must be in [0, num_of_subdomains).
        partition_list       : Sizes of each ciphertext chunk (bytes per stencil group).
        subdomain_capacity_list : Number of available grid coordinates per subdomain,
        num_of_subdomains     : Total number of subdomains.

    Raises:
        ValueError: if len(subdomain_assignment) != len(partition_list).
        ValueError: if any subdomain_assignment[i] is outside [0, num_of_subdomains).
        ValueError: if any subdomain's cumulative load exceeds its coordinate capacity.

    Example:
        partition_list       = [3, 2, 4]
        subdomain_assignment = [0, 1, 0]   
        # partition 0 of len 3 → sub0,
        # partition 1 of len 2 → sub1,
        # partition 2 of len 4 → sub0
        subdomain_capacity_list = [6, 5],  
        num_of_subdomains = 2  => 2 subdomains: sub0 has capacity 6, sub1 has capacity 5.

        iteration 0: size=3, s_idx=0 → remaining=[6,5], 6 >= 3 ✓ → remaining=[3,5]
        iteration 1: size=2, s_idx=1 → remaining=[3,5], 5 >= 2 ✓ → remaining=[3,3]
        iteration 2: size=4, s_idx=0 → remaining=[3,3], 3 >= 4 ✗ → raises ValueError
    """
    if len(subdomain_assignment) != len(partition_list):
        raise ValueError(
            f"subdomain_assignment length ({len(subdomain_assignment)}) must match "
            f"partition_list length ({len(partition_list)})."
        )
    remaining = subdomain_capacity_list.copy()
    for i, (size, s_idx) in enumerate(zip(partition_list, subdomain_assignment)):
        if not (0 <= s_idx < num_of_subdomains):
            raise ValueError(
                f"subdomain_assignment[{i}]={s_idx} is out of range [0, {num_of_subdomains})."
            )
        if remaining[s_idx] < size:
            raise ValueError(
                f"Subdomain {s_idx} has insufficient capacity for partition {i} "
                f"of size {size}. Remaining: {remaining[s_idx]}."
            )
        remaining[s_idx] -= size


def _random_assignment(
    partition_list: list[int],
    subdomain_capacity_list: list[int],
    num_of_subdomains: int,
) -> list[int]:
    """ Randomly assign each partition to a subdomain with enough remaining capacity - Case A, 
    where user provides only the selector function as subdomain definition.

    For each partition, shuffles subdomain indices and picks the first one with enough space,
    then decrements that subdomain's remaining capacity.

    Example:
        partition_list = [4, 2, 3, 1, 1, 1],  
        subdomain_capacity_list = [15, 16] and num_of_subdomains = 2 => sub domains: sub0 has capacity 15, sub1 has capacity 16.
        
        → partition 0 (size 4): shuffle → try subdomain 1 (cap 16 ≥ 4) → assign 1, remaining = [15, 12]
        → partition 1 (size 2): shuffle → try subdomain 0 (cap 15 ≥ 2) → assign 0, remaining = [13, 12]
        → partition 2 (size 3): shuffle → try subdomain 1 (cap 12 ≥ 3) → assign 1, remaining = [13, 9]
        → partition 3 (size 1): shuffle → try subdomain 0 (cap 13 ≥ 1) → assign 0, remaining = [12, 9]
        → partition 4 (size 1): shuffle → try subdomain 1 (cap 9 ≥ 1) → assign 1, remaining = [12, 8]
        → partition 5 (size 1): shuffle → try subdomain 0 (cap 12 ≥ 1) → assign 0, remaining = [11, 8]
        returns [1, 0, 1, 0, 1, 0]
    """
    subdomain_assignment_list: list[int] = []
    remaining = subdomain_capacity_list.copy()
    for idx, size in enumerate(partition_list):
        indices = list(range(num_of_subdomains))
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
        subdomain_assignment_list.append(chosen_subdomain)
        remaining[chosen_subdomain] -= size
    return subdomain_assignment_list


def generate_stencils_across_subdomains(
    partition_list: list[int],
    grid_shape: GridShape,
    subdomain_assignment: list[int] | None = None,
) -> list[Stencil]:
    """
    Distribute partitions across subdomains and place each group via a skew-connected walk.
    Supports two subdomain definition modes:
        Mode A — define by selector function: GridShape.subdomain_selectors shall be set; the library
            computes and caches the coord sets. Assignment is random (subdomain_assignment shall be None).
        Mode B — define by Grid coordinates: GridShape.subdomain_coord_list is set directly by
            the user. subdomain_assignment shall be user-defined.

    Args:
        partition_list        : list of group sizes, each >= 1.
        grid_shape            : GridShape with either subdomain_selectors or subdomain_coord_list set.
        subdomain_assignment  : Optional list of length len(partition_list).
                                subdomain_assignment[i] = j means partition i goes into subdomain j.
                                If None, assignment is chosen randomly.

    Returns:
        List of Stencil objects in original partition_list order.

    Raises:
        ValueError: if no subdomains are defined, assignment is invalid, or placement fails.
    """
    # Step 1: Resolve coord list.
    if grid_shape.subdomain_selectors and not grid_shape.subdomain_coord_list:
        # Case A (selector-based): user supplied subdomain_selectors; derives and stores coord sets.
        grid_shape.subdomain_coord_list = [
            list(grid_shape.get_subdomain_coords(sel))
            for sel in grid_shape.subdomain_selectors
        ]

    # Case B (explicit lists):  user supplied subdomain_coord_list directly
    num_of_subdomains = len(grid_shape.subdomain_coord_list)
    if num_of_subdomains == 0:
        raise ValueError(
            "No subdomains defined. Set subdomain_selectors or subdomain_coord_list on GridShape."
        )

    # Calculate and update free-coordinate sets from subdomain_coord_list.
    # Reason 1: And also handles the scenario where subdomain_coord_list(Case B) or subdomain_selectors(Case A) 
    # was set after construction without initialising free_subdomain_coord_list.
    # Reason 2: Additionally when multiple keygen calls are made with the same GridShape, 
    # ensures that free_subdomain_coord_list is updated to reflect consumed coordinates from previous calls.
    grid_shape.free_subdomain_coord_list = [set(coords) for coords in grid_shape.subdomain_coord_list]

    # Validate that subdomain coordinate sets are pairwise disjoint.
    if not _is_disjoint(grid_shape.subdomain_coord_list):
        raise ValueError(
            "Subdomain coordinate sets must be pairwise disjoint. "
            "One or more subdomains share coordinates with another."
        )

    # Calculate available free capacity for every sub-domain using the co-ordinates
    subdomain_capacity_list = [len(c) for c in grid_shape.subdomain_coord_list]

    # Step 2: Subdomain choice for each partition - Case A or Case B
    if subdomain_assignment is None:
        # Case A: randomly shuffle subdomains and greedily pick the first with enough space
        subdomain_assignment_list = _random_assignment(partition_list, subdomain_capacity_list, num_of_subdomains)
    else:
        # Case B: validate the user-provided assignment, then use it directly
        _validate_assignment(subdomain_assignment, partition_list, subdomain_capacity_list, num_of_subdomains)
        subdomain_assignment_list = subdomain_assignment

    # Verify partition list and subdomain_assignment_list are of same length
    assert len(partition_list) == len(subdomain_assignment_list), (
        f"Partition list and subdomain assignment list must be the same length. "
        f"Got {len(partition_list)} and {len(subdomain_assignment_list)}."
    )

    # Step 3: Generate a stencil for every partition, within the assigned subdomain
    stencils: list[Stencil] = []
    for stencil_len, subdomain_id in zip(partition_list, subdomain_assignment_list):
        [stencil] = generate_stencils_skewconnected([stencil_len], grid_shape, allowed_coords=grid_shape.free_subdomain_coord_list[subdomain_id])
        grid_shape.free_subdomain_coord_list[subdomain_id].difference_update(stencil.coords)
        stencils.append(stencil)

    return stencils