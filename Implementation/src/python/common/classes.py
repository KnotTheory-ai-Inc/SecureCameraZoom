from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple
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
class SecretKey:
    stencil_coords: List[Tuple[int, int]]  # e.g. [(2,3), (3,3), ...]
    partition:      List[int]              # e.g. [1, 1, 3]
    permutation:    List[int]              # σ — shuffle of [0..n-1]
    reading_order:  str                    # e.g. "top-bottom-left-right"
    cipher_cfg:     CipherConfig           # bundles algo + params + encrypt()/decrypt() handles

@dataclass
class Grid:
    data: List[bytearray]   # data[row][col]
    rows: int
    cols: int