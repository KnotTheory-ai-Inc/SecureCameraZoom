
import pytest
from Keygen.keygen import generate_stencils_skewconnected
from common.classes import GridShape, Stencil

def test_generate_stencils_skewconnected_basic():
	partition_list = [2, 3]
	grid_shape = GridShape(n=4, shape=(4, 5, 7, 3))
	stencils = generate_stencils_skewconnected(partition_list, grid_shape)
	# Should return two stencils
	assert len(stencils) == 2
	# Each stencil should have the correct length
	assert stencils[0].len == 2
	assert stencils[1].len == 3
	# All coordinates should be within grid bounds
	for stencil in stencils:
		for coord in stencil.coords:
			assert 0 <= coord[0] < 4
			assert 0 <= coord[1] < 5
			assert 0 <= coord[2] < 7
			assert 0 <= coord[3] < 3
	# All coordinates should be unique across all stencils
	all_coords = [c for s in stencils for c in s.coords]
	assert len(all_coords) == len(set(all_coords))

def test_generate_stencils_skewconnected_full_grid():
	partition_list = [1]*24
	grid_shape = GridShape(n=3, shape=(4, 6, 1))
	stencils = generate_stencils_skewconnected(partition_list, grid_shape)
	# Should cover all grid positions
	all_coords = set(c for s in stencils for c in s.coords)
	assert all_coords == grid_shape.all_coords()

def test_generate_stencils_skewconnected_partition_size_matches():
	partition_list = [4, 5]
	grid_shape = GridShape(n=3, shape=(4, 6, 1))
	stencils = generate_stencils_skewconnected(partition_list, grid_shape)
	for stencil, size in zip(stencils, partition_list):
		assert stencil.len == size


# --- Additional variety tests ---
def test_generate_stencils_skewconnected_2d_variety():
	partition_list = [1, 2, 3]
	grid_shape = GridShape(n=2, shape=(3, 3))
	stencils = generate_stencils_skewconnected(partition_list, grid_shape)
	assert len(stencils) == 3
	for stencil, size in zip(stencils, partition_list):
		assert stencil.len == size
		for coord in stencil.coords:
			assert 0 <= coord[0] < 3
			assert 0 <= coord[1] < 3

def test_generate_stencils_skewconnected_3d_variety():
	partition_list = [2, 4, 5]
	grid_shape = GridShape(n=3, shape=(3, 3, 2))
	stencils = generate_stencils_skewconnected(partition_list, grid_shape)
	assert len(stencils) == 3
	for stencil, size in zip(stencils, partition_list):
		assert stencil.len == size
		for coord in stencil.coords:
			assert 0 <= coord[0] < 3
			assert 0 <= coord[1] < 3
			assert 0 <= coord[2] < 2

def test_generate_stencils_skewconnected_single_large_partition():
	partition_list = [6]
	grid_shape = GridShape(n=2, shape=(2, 3))
	stencils = generate_stencils_skewconnected(partition_list, grid_shape)
	assert len(stencils) == 1
	assert stencils[0].len == 6
	for coord in stencils[0].coords:
		assert 0 <= coord[0] < 2
		assert 0 <= coord[1] < 3

def test_generate_stencils_skewconnected_all_ones():
	partition_list = [1, 1, 1, 1]
	grid_shape = GridShape(n=2, shape=(2, 2))
	stencils = generate_stencils_skewconnected(partition_list, grid_shape)
	assert len(stencils) == 4
	all_coords = set(c for s in stencils for c in s.coords)
	assert all_coords == grid_shape.all_coords()