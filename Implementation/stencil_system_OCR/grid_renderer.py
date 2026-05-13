import io
from PIL import Image, ImageDraw, ImageFont

CELL_PX = 40
FONT_SIZE = 22
PADDING = 6

_MONO_FONT_CANDIDATES = [
    "cour.ttf",
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
    return chr(value % 95 + 32)


def char_to_byte(char: str) -> int:
    return ord(char) - 32


def render_grid(grid, grid_shape, output_path: str = None) -> Image.Image:
    if grid_shape.n != 2:
        raise ValueError("render_grid only supports 2-D grids (n=2).")

    rows, cols = grid_shape.shape
    font = _load_font()
    img = Image.new("RGB", (cols * CELL_PX, rows * CELL_PX), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    for row in range(rows):
        for col in range(cols):
            byte_val = grid.get_value((row, col))
            char = byte_to_char(byte_val) if byte_val != -1 else "?"
            x, y = col * CELL_PX, row * CELL_PX
            draw.rectangle([x, y, x + CELL_PX - 1, y + CELL_PX - 1], outline=(210, 210, 210))
            draw.text((x + PADDING, y + PADDING), char, fill=(20, 20, 20), font=font)

    if output_path:
        img.save(output_path, format="PNG")
    return img


def render_grid_bytes(grid, grid_shape) -> bytes:
    buf = io.BytesIO()
    render_grid(grid, grid_shape).save(buf, format="PNG")
    return buf.getvalue()


def highlight_stencil_cells(grid, grid_shape, secret_key, output_path: str = None) -> Image.Image:
    img = render_grid(grid, grid_shape)
    draw = ImageDraw.Draw(img)
    stencil_coords = {coord for stencil in secret_key.stencils for coord in stencil.coords}
    for row, col in stencil_coords:
        x, y = col * CELL_PX, row * CELL_PX
        draw.rectangle([x + 1, y + 1, x + CELL_PX - 2, y + CELL_PX - 2], outline=(220, 30, 30), width=2)
    if output_path:
        img.save(output_path, format="PNG")
    return img
