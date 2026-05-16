import pytest
from Keygen.keygen import generate_partition_list


def test_sum_equals_n():
    """Partition values must always sum to n."""
    result = generate_partition_list(20, 4)
    assert sum(result) == 20


def test_length_equals_num_partitions():
    """Number of groups must equal num_partitions."""
    result = generate_partition_list(15, 3)
    assert len(result) == 3


def test_all_groups_at_least_one():
    """Every partition group must have at least 1 byte."""
    result = generate_partition_list(10, 5)
    assert all(p >= 1 for p in result)


def test_single_partition():
    """num_partitions=1 gives a single group equal to n."""
    result = generate_partition_list(8, 1)
    assert result == [8]


def test_max_partitions():
    """num_partitions=n gives all ones."""
    result = generate_partition_list(5, 5)
    assert len(result) == 5
    assert sum(result) == 5
    assert all(p >= 1 for p in result)


def test_invalid_num_partitions_zero():
    """num_partitions=0 raises ValueError."""
    with pytest.raises(ValueError):
        generate_partition_list(10, 0)


def test_invalid_num_partitions_exceeds_n():
    """num_partitions > n raises ValueError."""
    with pytest.raises(ValueError):
        generate_partition_list(5, 6)


@pytest.mark.parametrize("n,k", [(10, 2), (16, 4), (100, 10), (7, 3)])
def test_parametrized_sum(n, k):
    """Parametrized: sum always equals n for various inputs."""
    result = generate_partition_list(n, k)
    assert sum(result) == n
    assert len(result) == k
