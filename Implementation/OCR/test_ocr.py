"""
test_ocr.py — Standalone OCR pipeline tests (fully local, zero API key).

All tests run offline using local TrOCR models. No Gemini API, no cloud,
no internet required after the one-time model download.

Run with:
    pytest Implementation/OCR/test_ocr.py -v -s --noconftest

The --noconftest flag isolates us from Implementation/conftest.py which
requires the crypto wheel to be built first.

Test groups:
    1. Unit tests   — no model loading (renderer, detector, extractor logic)
    2. Model tests  — load TrOCR once, test OCR on synthetic data
    3. Pipeline     — full end-to-end synthetic test (keygen → encrypt → render → OCR → decrypt)

Download models before running (one-time):
    python -c "from transformers import TrOCRProcessor, VisionEncoderDecoderModel; \
               TrOCRProcessor.from_pretrained('microsoft/trocr-small-printed'); \
               VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-small-printed')"
"""

import io
import sys
import pytest
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ── path setup ────────────────────────────────────────────────────────────────
_OCR_DIR = Path(__file__).parent
_SRC_DIR = _OCR_DIR.parent / "src" / "python"
sys.path.insert(0, str(_OCR_DIR))
sys.path.insert(0, str(_SRC_DIR))

SAMPLE_DIR = _OCR_DIR / "sample_images"


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def ocr():
    """Load TrOCR once for the whole test session."""
    from ocr_handler import SecureVisionOCR
    return SecureVisionOCR(mode="printed")


@pytest.fixture(scope="session")
def synthetic_grid_and_key():
    """
    Build a minimal synthetic stencil using the crypto library.
    Caesar cipher, 2-D 10×10 grid, 5-byte message. No API calls.
    """
    from common.classes import GridShape, StencilConfig  # noqa: E402
    from Keygen.keygen import keygen                      # noqa: E402
    from Encryption.encrypt import encrypt                # noqa: E402
    from test.utils.classes import CaesarConfig          # noqa: E402

    plaintext   = b"HELLO"
    cipher_cfg  = CaesarConfig(shift=3)
    grid_shape  = GridShape(n=2, shape=(10, 10))
    stencil_cfg = StencilConfig(
        total_bytes=len(plaintext),
        num_partitions=len(plaintext),
        grid_shape=grid_shape,
        enable_cipher_permutation=False,
        enable_grid_permutation=False,
    )
    secret_key = keygen(stencil_cfg, cipher_cfg)
    grid       = encrypt(plaintext, secret_key, stencil_cfg)
    return grid, secret_key, stencil_cfg, grid_shape, plaintext


def _make_char_image(char: str, size: int = 160) -> bytes:
    """Create a clean white PNG of a single character for OCR testing."""
    img  = Image.new("RGB", (size, size), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("cour.ttf", size - 40)
    except (IOError, OSError):
        font = ImageFont.load_default()
    draw.text((size // 4, size // 8), char, fill=(0, 0, 0), font=font)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ── Group 1: unit tests (no model loading) ────────────────────────────────────

class TestGridRenderer:
    def test_render_returns_pil_image(self, synthetic_grid_and_key):
        from grid_renderer import render_grid
        grid, _, _, grid_shape, _ = synthetic_grid_and_key
        img = render_grid(grid, grid_shape)
        assert isinstance(img, Image.Image)
        assert img.size == (grid_shape.shape[1] * 40, grid_shape.shape[0] * 40)

    def test_render_to_bytes(self, synthetic_grid_and_key):
        from grid_renderer import render_grid_bytes
        grid, _, _, grid_shape, _ = synthetic_grid_and_key
        data = render_grid_bytes(grid, grid_shape)
        assert Image.open(io.BytesIO(data)).format == "PNG"

    def test_byte_char_roundtrip(self):
        from grid_renderer import byte_to_char, char_to_byte
        for b in range(95):
            assert char_to_byte(byte_to_char(b)) == b

    def test_highlight_stencil_cells(self, synthetic_grid_and_key):
        from grid_renderer import highlight_stencil_cells
        grid, secret_key, _, grid_shape, _ = synthetic_grid_and_key
        assert isinstance(highlight_stencil_cells(grid, grid_shape, secret_key), Image.Image)


class TestGridDetector:
    def test_load_image_raises_on_missing(self):
        from grid_detector import load_image
        with pytest.raises(FileNotFoundError):
            load_image("nonexistent_file.png")

    def test_detect_and_align_returns_ndarray(self, synthetic_grid_and_key):
        import cv2
        from grid_renderer import render_grid_bytes
        from grid_detector import detect_and_align_grid
        grid, _, _, grid_shape, _ = synthetic_grid_and_key
        png = render_grid_bytes(grid, grid_shape)
        bgr = cv2.imdecode(np.frombuffer(png, np.uint8), cv2.IMREAD_COLOR)
        aligned = detect_and_align_grid(bgr)
        assert aligned is not None and aligned.shape[2] == 3

    def test_estimate_cell_size(self, synthetic_grid_and_key):
        import cv2
        from grid_renderer import render_grid_bytes
        from grid_detector import detect_and_align_grid, estimate_cell_size
        grid, _, _, grid_shape, _ = synthetic_grid_and_key
        png = render_grid_bytes(grid, grid_shape)
        bgr = cv2.imdecode(np.frombuffer(png, np.uint8), cv2.IMREAD_COLOR)
        aligned = detect_and_align_grid(bgr)
        rows, cols = grid_shape.shape
        cell_h, cell_w = estimate_cell_size(aligned, rows, cols)
        assert cell_h > 0 and cell_w > 0


class TestStencilExtractor:
    def test_extract_returns_correct_count(self, synthetic_grid_and_key):
        import cv2
        from grid_renderer import render_grid_bytes
        from grid_detector import detect_and_align_grid
        from stencil_extractor import extract_stencil_cells
        grid, secret_key, _, grid_shape, plaintext = synthetic_grid_and_key
        png = render_grid_bytes(grid, grid_shape)
        bgr = cv2.imdecode(np.frombuffer(png, np.uint8), cv2.IMREAD_COLOR)
        aligned = detect_and_align_grid(bgr)
        cells = extract_stencil_cells(aligned, secret_key, grid_shape)
        assert len(cells) == len(plaintext)

    def test_cell_to_bytes_is_valid_png(self, synthetic_grid_and_key):
        import cv2
        from grid_renderer import render_grid_bytes
        from grid_detector import detect_and_align_grid
        from stencil_extractor import extract_stencil_cells, cell_to_bytes
        grid, secret_key, _, grid_shape, _ = synthetic_grid_and_key
        png = render_grid_bytes(grid, grid_shape)
        bgr = cv2.imdecode(np.frombuffer(png, np.uint8), cv2.IMREAD_COLOR)
        aligned = detect_and_align_grid(bgr)
        cells = extract_stencil_cells(aligned, secret_key, grid_shape)
        for _, cell in cells[:3]:
            assert Image.open(io.BytesIO(cell_to_bytes(cell))).format == "PNG"


# ── Group 2: TrOCR model tests ────────────────────────────────────────────────

class TestOCRHandler:
    def test_model_loads(self, ocr):
        from ocr_handler import SecureVisionOCR
        assert ocr.processor is not None
        assert ocr.model is not None

    def test_ocr_single_char_image(self, ocr):
        """Feed a clean rendered character — TrOCR should return that char."""
        char_png = _make_char_image("A")
        result = ocr.extract_text_from_bytes(char_png)
        assert isinstance(result, str)
        print(f"\n[TrOCR single char] rendered 'A' → got '{result}'")

    def test_ocr_single_cell_returns_one_char(self, ocr):
        char_png = _make_char_image("K")
        result = ocr.ocr_single_cell(char_png)
        assert isinstance(result, str) and len(result) <= 1
        print(f"\n[ocr_single_cell] rendered 'K' → got '{result}'")

    def test_ocr_from_image_file(self, ocr, tmp_path):
        char_png = _make_char_image("Z")
        p = tmp_path / "test_char.png"
        p.write_bytes(char_png)
        result = ocr.extract_text_from_image(str(p))
        assert isinstance(result, str)
        print(f"\n[extract_text_from_image] rendered 'Z' → got '{result}'")

    def test_handwritten_model_loads(self):
        from ocr_handler import SecureVisionOCR  # noqa: F401
        ocr_hw = SecureVisionOCR(mode="handwritten")
        assert ocr_hw.model is not None

    def test_sample_images_if_present(self, ocr):
        images = [f for f in SAMPLE_DIR.glob("*")
                  if f.suffix.lower() in {".png", ".jpg", ".jpeg"}]
        if not images:
            pytest.skip("No images in sample_images/ — add some to test real camera input")
        for img_path in images:
            result = ocr.extract_text_from_image(str(img_path))
            print(f"\n[sample] {img_path.name} → '{result}'")
            assert isinstance(result, str)


# ── Group 3: full pipeline (requires crypto wheel: inv build) ─────────────────

class TestOCRPipeline:
    def test_render_then_ocr_single_cell(self, ocr, synthetic_grid_and_key):
        """Render a grid cell, run TrOCR on it, verify it returns a string."""
        import cv2
        from grid_renderer import render_grid_bytes
        from grid_detector import detect_and_align_grid
        from stencil_extractor import extract_stencil_cells, cell_to_bytes, preprocess_cell

        grid, secret_key, _, grid_shape, _ = synthetic_grid_and_key
        png = render_grid_bytes(grid, grid_shape)
        bgr = cv2.imdecode(np.frombuffer(png, np.uint8), cv2.IMREAD_COLOR)
        aligned = detect_and_align_grid(bgr)
        cells   = extract_stencil_cells(aligned, secret_key, grid_shape)

        coord, first_cell = cells[0]
        processed = preprocess_cell(first_cell)
        char = ocr.ocr_single_cell(cell_to_bytes(processed, upscale=True))
        print(f"\n[pipeline cell OCR] coord={coord} → '{char}'")
        assert isinstance(char, str)

    def test_full_pipeline_grid_reconstruction(self, synthetic_grid_and_key, tmp_path):
        """Render grid → PNG → ocr_image_to_grid → verify Grid has correct coord count."""
        from grid_renderer import render_grid
        from ocr_pipeline import ocr_image_to_grid

        grid, secret_key, stencil_cfg, grid_shape, plaintext = synthetic_grid_and_key
        img_path = str(tmp_path / "stencil.png")
        render_grid(grid, grid_shape, output_path=img_path)

        reconstructed = ocr_image_to_grid(img_path, secret_key, stencil_cfg, preprocess=False)
        # Grid should have one entry per stencil position
        assert len(reconstructed.data) == len(plaintext)
        print(f"\n[ocr_image_to_grid] {len(reconstructed.data)} coords recovered")

    def test_full_ocr_decrypt_roundtrip(self, synthetic_grid_and_key, tmp_path):
        """Full round-trip: plaintext → encrypt → render → OCR → decrypt → plaintext."""
        from grid_renderer import render_grid
        from ocr_pipeline import full_ocr_decrypt

        grid, secret_key, stencil_cfg, grid_shape, plaintext = synthetic_grid_and_key
        img_path = str(tmp_path / "stencil_roundtrip.png")
        render_grid(grid, grid_shape, output_path=img_path)

        recovered = full_ocr_decrypt(img_path, secret_key, stencil_cfg, preprocess=False)
        print(f"\n[round-trip] original={plaintext!r}  recovered={recovered!r}")
        assert recovered == plaintext, (
            f"Round-trip failed: original={plaintext!r}, recovered={recovered!r}"
        )
