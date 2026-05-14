import random
from common.classes import GridCoord, GridShape, Stencil, StencilCoord, StencilCoords


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
    # built once; refreshed only after each confirmed placement of stencil in Grid/subdomain
    free_list: list[GridCoord] = list(free)

    for p in partition_list:
        stencil_coords: StencilCoords = []

        for _ in range(MAX_ATTEMPTS):
            start: StencilCoord = random.choice(free_list)
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
        # refresh free_list after confirmed stencil placement outside of attempts loop
        free_list = list(free)
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
