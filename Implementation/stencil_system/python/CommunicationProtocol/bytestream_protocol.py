def grid_to_bytestream(grid: Grid) -> bytes:
    """
    Flatten the N-D grid into a byte stream for transmission.
    - Input: grid (Grid, ciphertext-embedded)
    - Output: bytes object.
    - Implementation: b''.join(grid.data)  — each row is already a bytearray.
    - Note: Equivalent byte index: grid.data[row][col] == bytestream[row * cols + col]
    """


def bytestream_to_grid(bytestream: bytes, rows: int, cols: int) -> Grid:
    """
    Convert a byte stream back into a N-D grid.
    - Input: bytestream (bytes), rows (int), cols (int)
    - Output: Grid dataclass instance.
    """
