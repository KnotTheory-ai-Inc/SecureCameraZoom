import random  # TODO: replace with DRBG implementation
from common.classes import CipherConfig, GridCoord, GridShape, SecretKey, Stencil, StencilCoord, StencilCoords, StencilConfig
from Keygen.stencils_skewconnected import generate_stencils_skewconnected
from Keygen.stencils_sub_domain import generate_stencils_across_subdomains


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
        if  stencil_cfg.enable_subdomain_partitioning == True:
            # generate stencils across subdomains defined by grid_shape.subdomain_predicates or subdomain_coord_list
            stencils = generate_stencils_across_subdomains(partition_list, grid_shape, stencil_cfg.subdomain_assignment)
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




