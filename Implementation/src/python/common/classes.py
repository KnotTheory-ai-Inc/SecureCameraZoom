from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass, field
from itertools import product as _iter_product
import random
from typing import List, Optional, Tuple

# Type aliases for stencil coordinates
StencilCoord = Tuple[int, ...]  # e.g. (row, col) for 2-D, (x, y, z) for 3-D
StencilCoords = List[StencilCoord]       # list of co-ordinate pairs

# N-D array of ints, e.g. [row, col] for 2-D, [x, y, z] for 3-D.
GridCoord = Tuple[int, ...]
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


@dataclass
class GridShape:
    # Number of dimensions, e.g. 2 for 2-D, 3 for 3-D, N for N-D.
    n: int 
    # Size along each dimension, e.g. (rows, cols) for 2-D, (x, y, z) for 3-D
    shape: Tuple[int, ...]

    def __post_init__(self):
        if self.n != len(self.shape):
            raise ValueError(f"GridShape: n ({self.n}) must match len(shape) ({len(self.shape)})")
        if not all(isinstance(dim, int) and dim > 0 for dim in self.shape):
            raise ValueError(f"GridShape: all dimensions in shape must be positive integers, got {self.shape}")

    def get_neighbors(self, coord: GridCoord) -> List[GridCoord]:
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


@dataclass
class Grid(GridShape):
    # N-D grid with dict-based storage: data[coord] = int
    def __init__(self, data: dict):
        self.data = data

    def get_value(self, coord: GridCoord) -> int:
        # Get the byte value at the specified coordinate; return -1 if unset
        return self.data.get(coord, -1)
    

@dataclass
class Stencil():
    """Represents a stencil — any arbitrary set of grid positions.
    shape  : optional human-readable label e.g. "L-shape", "square", "disconnected"
    len    : number of grid positions covered by stencil
    coords : explicit (row, col) positions — the actual shape in Grid.
    """
    shape:  str = None # label
    len:    int = None
    coords: StencilCoords = field(default_factory=list)  # co-ordinates of stencil positions in grid

# --- StencilConfig dataclass ---
@dataclass
class StencilConfig:
    total_bytes: int
    num_partitions: int
    grid_shape: GridShape


@dataclass
class SecretKey:
    stencils: List[Stencil]       # list of Stencil objects for each partition
    partition_list:      List[int]     # e.g. [1, 1, 3]
    #permutation:    List[int]    # sigma — shuffle of [0..n-1]
    #reading_order:  str          # e.g. "top-bottom-left-right"
    cipher_cfg:     CipherConfig  # bundles algo + params + encrypt()/decrypt() handles