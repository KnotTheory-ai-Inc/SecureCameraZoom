import random
import pytest
from Encryption.steganography_encrypt import do_partitioning


def test_partition_count():
    """Number of groups equals len(partition)."""
    ct = random.randbytes(10)
    result = do_partitioning(ct, [1, 1, 3, 5])
    assert len(result) == 4


def test_partition_sizes():
    """Each group has exactly partition[i] bytes."""
    ct = random.randbytes(10)
    partition = [1, 1, 3, 5]
    result = do_partitioning(ct, partition)
    for group, p in zip(result, partition):
        assert len(group) == p


def test_partition_reassembly():
    """Concatenating all groups recovers the original ciphertext."""
    ct = random.randbytes(16)
    partition = [4, 4, 4, 4]
    result = do_partitioning(ct, partition)
    assert b"".join(result) == ct


def test_single_partition():
    """Single group covering entire ciphertext."""
    ct = random.randbytes(8)
    result = do_partitioning(ct, [8])
    assert len(result) == 1
    assert result[0] == ct


def test_all_ones_partition():
    """Partition [1]*n splits ciphertext into individual bytes."""
    ct = random.randbytes(5)
    result = do_partitioning(ct, [1, 1, 1, 1, 1])
    assert len(result) == 5
    for i, group in enumerate(result):
        assert group == bytes([ct[i]])


def test_uneven_partition():
    """Uneven partition sizes still sum correctly."""
    ct = random.randbytes(10)
    partition = [2, 5, 3]
    result = do_partitioning(ct, partition)
    assert b"".join(result) == ct
    assert [len(g) for g in result] == partition


def test_each_group_is_bytes():
    """Every group is a bytes object."""
    ct = random.randbytes(9)
    result = do_partitioning(ct, [3, 3, 3])
    for group in result:
        assert isinstance(group, bytes)
