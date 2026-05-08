from abc import ABC, abstractmethod
from collections.abc import Callable
from itertools import product as _iter_product
import random

# Type aliases for stencil coordinates
StencilCoord = tuple[int, ...]  # e.g. (row, col) for 2-D, (x, y, z) for 3-D
StencilCoords = list[StencilCoord]       # list of co-ordinate pairs

# N-D array of ints, e.g. [row, col] for 2-D, [x, y, z] for 3-D.
GridCoord = tuple[int, ...]
class CipherConfig(ABC):
    """Abstract base class for all cipher keys.

    Each concrete subclass bundles every algorithm-specific parameter so
    callers pass a single Key object to cipher_encrypt / cipher_decrypt.
    """
    parameters: dict
    algo: str

    @abstractmethod
    def encrypt(self, plaintext: bytes, *args, **kwargs) -> bytes:
        pass

    @abstractmethod
    def decrypt(self, ciphertext: bytes, *args, **kwargs) -> bytes:
        pass


class GridShape:
    """N-D grid shape with validation and neighbor/coordinate utilities.
    
    Attributes:
        n: Number of dimensions (e.g., 2 for 2-D, 3 for 3-D)
        shape: Size along each dimension (e.g., (num of rows, num of cols) for 2-D)
    """
    def __init__(self, n: int, shape: tuple[int, ...], subdomain_predicates: list[Callable] = None):
        if n != len(shape):
            raise ValueError(f"GridShape: n ({n}) must match len(shape) ({len(shape)})")
        if not all(isinstance(dim, int) and dim > 0 for dim in shape):
            raise ValueError(f"GridShape: all dimensions in shape must be positive integers, got {shape}")
        self.n = n
        self.shape = shape
        self.subdomain_predicates = subdomain_predicates if subdomain_predicates is not None else []

    def get_neighbors(self, coord: GridCoord) -> list[GridCoord]:
        # Return all neighbors reachable by moving -1/0/+1 in each dimension (3^n - 1 total)
        neighbors = []
        ndim = len(coord)
        zero_delta = (0,) * ndim
        for deltas in _iter_product([-1, 0, 1], repeat=ndim):
            # skip (0, 0, ..., 0) — that's the coord itself, not a neighbor
            if deltas == zero_delta:
                continue

            # check bounds for i-th neighbor - coord[i] + deltas[i]
            in_bounds = all(0 <= coord[i] + deltas[i] < self.shape[i] for i in range(ndim))
            if not in_bounds:
                continue

            # if i-th neighbor - coord[i] + deltas[i] is in bounds, add to neighbors list
            neighbor = tuple(coord[i] + deltas[i] for i in range(ndim))
            neighbors.append(neighbor)
        return neighbors

    def get_random_coord(self) -> GridCoord:
        """
        Return a random coordinate within the grid bounds.
        Samples each dimension independently to avoid materializing all coordinates.
        """
        return tuple(random.randrange(dimension_size) for dimension_size in self.shape)

    def all_coords(self) -> set:
        """
        Return the set of all valid coordinates in this grid.
        Example:
            If self.shape = (2, 3), returns:
                {(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)}
        """
        return set(_iter_product(*map(range, self.shape)))

    def get_subdomain_coords(self, predicate: Callable) -> set[GridCoord]:
        """
        Return the set of coordinates in this grid that satisfy the given predicate function.
        The predicate function takes a coordinate tuple as input and returns a boolean.
        """
        return {c for c in self.all_coords() if predicate(c)}


class Grid:
    """N-D grid with dict-based storage: data[coord] = int.
    
    Attributes:
        data: Dictionary mapping grid coordinates to byte values.
    """
    def __init__(self, data: dict):
        self.data = data

    def get_value(self, coord: GridCoord) -> int:
        """Get the byte value at the specified coordinate; return -1 if unset."""
        return self.data.get(coord, -1)


class Stencil:
    """Represents a stencil — any arbitrary set of grid positions.
    
    Attributes:
        shape: Optional human-readable label (e.g., "L-shape", "square", "disconnected").
        len: Number of grid positions covered by stencil.
        coords: Explicit coordinate positions — the actual shape in Grid.
    """
    def __init__(self, shape: str = None, len: int = None, coords: StencilCoords = None):
        self.shape = shape
        self.len = len
        self.coords = coords if coords is not None else []


class StencilConfig:
    """Configuration for stencil key generation.
    
    Attributes:
        total_bytes: Ciphertext length.
        num_partitions: Number of partitions to create.
        grid_shape: GridShape object specifying grid dimensions.
        enable_cipher_permutation: Choose whether keygen API should generate a cipher_permutation.
            If True, ciphertext bytes are shuffled before being placed into stencil positions.
        enable_grid_permutation: Choose whether keygen API should generate a grid_permutation.
            If True, stencil slot assignments are shuffled after ciphertext is split across
            stencils naturally (Possibility 2 — post-split permutation).
    """
    def __init__(self, total_bytes: int, num_partitions: int, grid_shape: GridShape,
                 enable_cipher_permutation: bool = False, enable_grid_permutation: bool = False):
        self.total_bytes = total_bytes
        self.num_partitions = num_partitions
        self.grid_shape = grid_shape
        self.enable_cipher_permutation = enable_cipher_permutation
        self.enable_grid_permutation = enable_grid_permutation


class SecretKey:
    """Secret key bundling stencil and cipher configuration.

    Attributes:
        stencils: List of Stencil objects, one per partition (SR_l).
        partition_list: Partition sizes (e.g., [1, 1, 3]) — the partition R_l.
        cipher_cfg: CipherConfig subclass bundling algorithm + parameters + encrypt/decrypt methods.
        cipher_permutation: permutation as a list of
            ciphertext byte indices. cipher_permutation[i] = j means: the i-th stencil
            position in reading order receives the j-th ciphertext byte. Applied before
            placing bytes into stencil positions.
        grid_permutation: permutation as a list of stencil
            slot indices. grid_permutation[i] = j means: the i-th stencil in spatial order
            receives the j-th ciphertext chunk after natural splitting. Applied after
            distributing ciphertext across stencils.
    """
    def __init__(self, stencils: list[Stencil], partition_list: list[int], cipher_cfg: CipherConfig,
                 cipher_permutation: list[int] | None = None, grid_permutation: list[int] | None = None):
        self.stencils = stencils
        self.partition_list = partition_list
        self.cipher_cfg = cipher_cfg
        self.cipher_permutation = cipher_permutation
        self.grid_permutation = grid_permutation