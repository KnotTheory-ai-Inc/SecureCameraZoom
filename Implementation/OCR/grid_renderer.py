"""
grid_renderer.py — Sender-side utility.

Converts a Grid object (the obfuscated stencil produced by steganography_encrypt)
into a printable PNG image. Each grid cell becomes a fixed-size character tile.
The receiver captures this image (camera/fax/screen) and feeds it into the OCR pipeline.

Byte → character mapping:
    byte_value % 95 + 32  →  printable ASCII (0x20 ' ' … 0x7E '~')
This is the visual encoding contract shared between sender and receiver.
"""

import io
from PIL import Image, ImageDraw, ImageFont

CELL_PX   = 40    # pixels per cell (width and height)
FONT_SIZE = 22
PADDING   = 6     # inner margin so glyphs don't touch grid lines

# Fallback: PIL built-in font if no monospace TTF is found on the system
_MONO_FONT_CANDIDATES = [
    "cour.ttf",          # Windows Courier New
    "DejaVuSansMono.ttf",
    "LiberationMono-Regular.ttf",
    "FreeMono.ttf",
]


def _load_font(size: int = FONT_SIZE) -> ImageFont.FreeTypeFont:
    for name in _MONO_FONT_CANDIDATES:
        try:
            return ImageFont.truetype(name, size)
        except (IOError, OSError):
            continue
    return ImageFont.load_default()


def byte_to_char(value: int) -> str:
    """Map a raw byte (0-255) to a single printable ASCII character."""
    return chr(value % 95 + 32)


def char_to_byte(char: str) -> int:
    """Inverse of byte_to_char — OCR char back to byte value (within 0-94 range)."""
    return ord(char) - 32


def render_grid(grid, grid_shape, output_path: str = None) -> Image.Image:
    """
    Render a 2-D Grid as a monospace character grid image.

    Args:
        grid       : Grid object with dict-based data (coord -> int).
        grid_shape : GridShape with .shape = (rows, cols).
        output_path: If given, save PNG to this path.

    Returns:
        PIL Image object of the rendered grid.
    """
    if grid_shape.n != 2:
        raise ValueError("render_grid only supports 2-D grids (n=2).")

    rows, cols = grid_shape.shape
    font = _load_font()

    img_w = cols * CELL_PX
    img_h = rows * CELL_PX
    img = Image.new("RGB", (img_w, img_h), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    for row in range(rows):
        for col in range(cols):
            coord = (row, col)
            byte_val = grid.get_value(coord)
            char = byte_to_char(byte_val) if byte_val != -1 else "?"

            x = col * CELL_PX
            y = row * CELL_PX

            # light grid lines
            draw.rectangle(
                [x, y, x + CELL_PX - 1, y + CELL_PX - 1],
                outline=(210, 210, 210),
            )
            # character centred in cell
            draw.text((x + PADDING, y + PADDING), char, fill=(20, 20, 20), font=font)

    if output_path:
        img.save(output_path, format="PNG")

    return img


def render_grid_bytes(grid, grid_shape, mime_type: str = "image/png") -> bytes:
    """Render the grid and return raw image bytes (no disk I/O)."""
    img = render_grid(grid, grid_shape)
    buf = io.BytesIO()
    fmt = "PNG" if "png" in mime_type.lower() else "JPEG"
    img.save(buf, format=fmt)
    return buf.getvalue()


def highlight_stencil_cells(
    grid, grid_shape, secret_key, output_path: str = None
) -> Image.Image:
    """
    Debug utility: render grid with stencil cells highlighted in red.
    Helps visually verify key-to-grid alignment before OCR.
    """
    img = render_grid(grid, grid_shape)
    draw = ImageDraw.Draw(img)

    stencil_coords = set()
    for stencil in secret_key.stencils:
        for coord in stencil.coords:
            stencil_coords.add(coord)

    for (row, col) in stencil_coords:
        x = col * CELL_PX
        y = row * CELL_PX
        draw.rectangle(
            [x + 1, y + 1, x + CELL_PX - 2, y + CELL_PX - 2],
            outline=(220, 30, 30),
            width=2,
        )

    if output_path:
        img.save(output_path, format="PNG")
    return img
