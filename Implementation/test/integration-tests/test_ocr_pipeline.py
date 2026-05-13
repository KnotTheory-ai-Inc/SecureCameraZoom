import io
import sys
import pytest
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

_OCR_DIR = Path(__file__).parent.parent.parent / "stencil_system_OCR"
sys.path.insert(0, str(_OCR_DIR))


@pytest.fixture(scope="session")
def ocr():
    from ocr_handler import SecureVisionOCR
    return SecureVisionOCR(mode="printed")


@pytest.fixture(scope="session")
def synthetic_grid_and_key():
    from common.classes import GridShape, StencilConfig  # noqa: E402
    from Keygen.keygen import keygen                      # noqa: E402
    from Encryption.encrypt import encrypt                # noqa: E402
    from test.utils.classes import CaesarConfig          # noqa: E402

    plaintext = b"HELLO"
    cipher_cfg = CaesarConfig(shift=3)
    grid_shape = GridShape(n=2, shape=(10, 10))
    stencil_cfg = StencilConfig(
        total_bytes=len(plaintext),
        num_partitions=len(plaintext),
        grid_shape=grid_shape,
        enable_cipher_permutation=False,
        enable_grid_permutation=False,
    )
    secret_key = keygen(stencil_cfg, cipher_cfg)
    grid = encrypt(plaintext, secret_key, stencil_cfg)
    return grid, secret_key, stencil_cfg, grid_shape, plaintext


def _make_char_image(char: str, size: int = 160) -> bytes:
    img = Image.new("RGB", (size, size), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("cour.ttf", size - 40)
    except (IOError, OSError):
        font = ImageFont.load_default()
    draw.text((size // 4, size // 8), char, fill=(0, 0, 0), font=font)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_render_returns_pil_image(synthetic_grid_and_key):
    from grid_renderer import render_grid
    grid, _, _, grid_shape, _ = synthetic_grid_and_key
    img = render_grid(grid, grid_shape)
    assert isinstance(img, Image.Image)
    assert img.size == (grid_shape.shape[1] * 40, grid_shape.shape[0] * 40)


def test_render_to_bytes(synthetic_grid_and_key):
    from grid_renderer import render_grid_bytes
    grid, _, _, grid_shape, _ = synthetic_grid_and_key
    data = render_grid_bytes(grid, grid_shape)
    assert Image.open(io.BytesIO(data)).format == "PNG"


def test_byte_char_roundtrip():
    from grid_renderer import byte_to_char, char_to_byte
    for b in range(95):
        assert char_to_byte(byte_to_char(b)) == b


def test_load_image_raises_on_missing():
    from grid_detector import load_image
    with pytest.raises(FileNotFoundError):
        load_image("nonexistent_file.png")


def test_detect_and_align_returns_ndarray(synthetic_grid_and_key):
    import cv2
    from grid_renderer import render_grid_bytes
    from grid_detector import detect_and_align_grid
    grid, _, _, grid_shape, _ = synthetic_grid_and_key
    png = render_grid_bytes(grid, grid_shape)
    bgr = cv2.imdecode(np.frombuffer(png, np.uint8), cv2.IMREAD_COLOR)
    aligned = detect_and_align_grid(bgr)
    assert aligned is not None and aligned.shape[2] == 3


def test_extract_all_cells_returns_correct_count(synthetic_grid_and_key):
    import cv2
    from grid_renderer import render_grid_bytes
    from grid_detector import detect_and_align_grid
    from stencil_extractor import extract_all_cells
    grid, _, _, grid_shape, _ = synthetic_grid_and_key
    png = render_grid_bytes(grid, grid_shape)
    bgr = cv2.imdecode(np.frombuffer(png, np.uint8), cv2.IMREAD_COLOR)
    aligned = detect_and_align_grid(bgr)
    rows, cols = grid_shape.shape
    cells = extract_all_cells(aligned, rows, cols)
    assert len(cells) == rows * cols


def test_model_loads(ocr):
    assert ocr.processor is not None
    assert ocr.model is not None


def test_ocr_single_char_image(ocr):
    char_png = _make_char_image("A")
    result = ocr.extract_text_from_bytes(char_png)
    assert isinstance(result, str)


def test_ocr_single_cell_returns_one_char(ocr):
    char_png = _make_char_image("K")
    result = ocr.ocr_single_cell(char_png)
    assert isinstance(result, str) and len(result) <= 1


def test_full_pipeline_grid_reconstruction(synthetic_grid_and_key, tmp_path):
    from grid_renderer import render_grid
    from ocr_pipeline import ocr_image_to_grid

    grid, _, stencil_cfg, grid_shape, plaintext = synthetic_grid_and_key
    img_path = str(tmp_path / "stencil.png")
    render_grid(grid, grid_shape, output_path=img_path)

    reconstructed = ocr_image_to_grid(img_path, stencil_cfg, preprocess=False)
    assert len(reconstructed.data) == grid_shape.shape[0] * grid_shape.shape[1]


def test_full_ocr_decrypt_roundtrip(synthetic_grid_and_key, tmp_path):
    from grid_renderer import render_grid
    from ocr_pipeline import full_ocr_decrypt

    grid, secret_key, stencil_cfg, grid_shape, plaintext = synthetic_grid_and_key
    img_path = str(tmp_path / "stencil_roundtrip.png")
    render_grid(grid, grid_shape, output_path=img_path)

    recovered = full_ocr_decrypt(img_path, secret_key, stencil_cfg, preprocess=False)
    assert recovered == plaintext, f"Round-trip failed: original={plaintext!r}, recovered={recovered!r}"
