def grid_to_bytestream(grid: Grid) -> bytes:
    """
    Flatten the 2D grid into a byte stream for transmission.
    - Input: grid (Grid, ciphertext-embedded)
    - Output: bytes object.
    - Implementation: b''.join(grid.data)  — each row is already a bytearray.
    - Note: Equivalent byte index: grid.data[row][col] == bytestream[row * cols + col]
    """

def get_grid_dimensions() -> Tuple[int, int]:
    """
    Return the (rows, cols) dimensions of the transmitted grid.
    - Output: (rows, cols) tuple
    - Note: both sender and receiver must agree on grid dimensions out-of-band
      (or dimensions can be prepended to the bytestream as a header).
    """

def bytestream_to_grid(bytestream: bytes, rows: int, cols: int) -> Grid:
    """
    Convert a byte stream back into a 2D grid.
    - Input: bytestream (bytes), rows (int), cols (int)
    - Output: Grid dataclass instance.
    """
