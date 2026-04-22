from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

# Type aliases for stencil coordinates
StencilCoord = Tuple[int, int]           # a single co-ordinate (x, y)
StencilCoords = List[StencilCoord]       # list of co-ordinate pairs
GridCoord = Tuple[int, int]              # (row, col) in grid
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
class GridSize():
    rows: int
    cols: int


@dataclass
class Grid(GridSize):
    data: List[bytearray]


@dataclass
class Stencil():
    """Represents a stencil — any arbitrary set of grid positions.
    shape  : optional human-readable label e.g. "L-shape", "square", "disconnected"
    len    : number of grid positions covered by stencil
    coords : explicit (row, col) positions — the actual shape in Grid.
    """
    shape:  str # label
    len:    int = None
    coords: StencilCoords = field(default_factory=list)  # co-ordinates of stencil positions in grid


@dataclass
class SecretKey:
    stencils: List[Stencil]       # list of Stencil objects for each partition
    partition_list:      List[int]     # e.g. [1, 1, 3]
    #permutation:    List[int]    # sigma — shuffle of [0..n-1]
    #reading_order:  str          # e.g. "top-bottom-left-right"
    cipher_cfg:     CipherConfig  # bundles algo + params + encrypt()/decrypt() handles