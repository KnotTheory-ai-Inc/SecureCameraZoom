"""
test_ocr.py — Standalone OCR pipeline tests.

Run with:
    pytest Implementation/OCR/test_ocr.py -v -s --noconftest

The --noconftest flag isolates us from Implementation/conftest.py which
requires the crypto wheel to be built first.

Test groups:
    1. Unit tests  — no API calls (renderer, detector, extractor logic)
    2. Integration — require GEMINI_API_KEY and make real Gemini API calls
    3. Pipeline    — full end-to-end synthetic test (keygen → encrypt → render → OCR → decrypt)
"""

import io
import os
import sys
import pytest
import numpy as np
from pathlib import Path
from PIL import Image

# ── path setup ────────────────────────────────────────────────────────────────
# Allow imports from OCR/ itself (ocr_handler, grid_renderer, etc.)
_OCR_DIR = Path(__file__).parent
_SRC_DIR = _OCR_DIR.parent / "src" / "python"
sys.path.insert(0, str(_OCR_DIR))
sys.path.insert(0, str(_SRC_DIR))

SAMPLE_DIR = _OCR_DIR / "sample_images"

# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def ocr():
    from ocr_handler import SecureVisionOCR
    return SecureVisionOCR()


@pytest.fixture(scope="session")
def synthetic_grid_and_key():
    """
    Build a minimal synthetic stencil end-to-end using the crypto library.
    Caesar cipher with shift=3, 2-D 10×10 grid, 5-byte message.
    No API calls — pure in-memory.
    """
    from common.classes import GridShape, StencilConfig
    from Keygen.keygen import keygen
    from Encryption.encrypt import encrypt
    from test.utils.classes import CaesarConfig  # noqa: E402 — test utility

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


# ── Group 1: unit tests (no API) ─────────────────────────────────────────────

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
        assert isinstance(data, bytes)
        img = Image.open(io.BytesIO(data))
        assert img.format == "PNG"

    def test_byte_char_roundtrip(self):
        from grid_renderer import byte_to_char, char_to_byte
        for b in range(95):  # printable ASCII range
            assert char_to_byte(byte_to_char(b)) == b

    def test_highlight_stencil_cells(self, synthetic_grid_and_key):
        from grid_renderer import highlight_stencil_cells
        grid, secret_key, _, grid_shape, _ = synthetic_grid_and_key
        img = highlight_stencil_cells(grid, grid_shape, secret_key)
        assert isinstance(img, Image.Image)


class TestGridDetector:
    def test_load_image_raises_on_missing(self):
        from grid_detector import load_image
        with pytest.raises(FileNotFoundError):
            load_image("nonexistent_file.png")

    def test_detect_and_align_returns_ndarray(self, synthetic_grid_and_key):
        import cv2, numpy as np
        from grid_renderer import render_grid_bytes
        from grid_detector import detect_and_align_grid
        grid, _, _, grid_shape, _ = synthetic_grid_and_key
        png_bytes = render_grid_bytes(grid, grid_shape)
        nparr = np.frombuffer(png_bytes, np.uint8)
        bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        aligned = detect_and_align_grid(bgr)
        assert aligned is not None
        assert aligned.shape[2] == 3  # BGR channels

    def test_estimate_cell_size(self, synthetic_grid_and_key):
        import cv2, numpy as np
        from grid_renderer import render_grid_bytes
        from grid_detector import detect_and_align_grid, estimate_cell_size
        grid, _, _, grid_shape, _ = synthetic_grid_and_key
        png_bytes = render_grid_bytes(grid, grid_shape)
        nparr = np.frombuffer(png_bytes, np.uint8)
        bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        aligned = detect_and_align_grid(bgr)
        rows, cols = grid_shape.shape
        cell_h, cell_w = estimate_cell_size(aligned, rows, cols)
        assert cell_h > 0 and cell_w > 0


class TestStencilExtractor:
    def test_extract_returns_correct_count(self, synthetic_grid_and_key):
        import cv2, numpy as np
        from grid_renderer import render_grid_bytes
        from grid_detector import detect_and_align_grid
        from stencil_extractor import extract_stencil_cells
        grid, secret_key, stencil_cfg, grid_shape, plaintext = synthetic_grid_and_key
        png_bytes = render_grid_bytes(grid, grid_shape)
        nparr = np.frombuffer(png_bytes, np.uint8)
        bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        aligned = detect_and_align_grid(bgr)
        cells = extract_stencil_cells(aligned, secret_key, grid_shape)
        # Each byte of plaintext has one stencil position
        assert len(cells) == len(plaintext)

    def test_each_cell_is_non_empty(self, synthetic_grid_and_key):
        import cv2, numpy as np
        from grid_renderer import render_grid_bytes
        from grid_detector import detect_and_align_grid
        from stencil_extractor import extract_stencil_cells
        grid, secret_key, stencil_cfg, grid_shape, _ = synthetic_grid_and_key
        png_bytes = render_grid_bytes(grid, grid_shape)
        nparr = np.frombuffer(png_bytes, np.uint8)
        bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        aligned = detect_and_align_grid(bgr)
        cells = extract_stencil_cells(aligned, secret_key, grid_shape)
        for coord, cell in cells:
            assert cell.size > 0, f"Empty crop at coord {coord}"

    def test_cell_to_bytes_is_valid_png(self, synthetic_grid_and_key):
        import cv2, numpy as np
        from grid_renderer import render_grid_bytes
        from grid_detector import detect_and_align_grid
        from stencil_extractor import extract_stencil_cells, cell_to_bytes
        grid, secret_key, stencil_cfg, grid_shape, _ = synthetic_grid_and_key
        png_bytes = render_grid_bytes(grid, grid_shape)
        nparr = np.frombuffer(png_bytes, np.uint8)
        bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        aligned = detect_and_align_grid(bgr)
        cells = extract_stencil_cells(aligned, secret_key, grid_shape)
        for _, cell in cells[:3]:   # check first 3 cells
            b = cell_to_bytes(cell)
            img = Image.open(io.BytesIO(b))
            assert img.format == "PNG"


# ── Group 2: integration tests (require GEMINI_API_KEY) ──────────────────────

@pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY") and not (Path(__file__).parent / ".env").exists(),
    reason="GEMINI_API_KEY not set",
)
class TestOCRHandler:
    def test_api_key_loaded(self):
        from dotenv import load_dotenv
        load_dotenv()
        assert os.getenv("GEMINI_API_KEY"), "GEMINI_API_KEY not found in .env"

    def test_client_initializes(self):
        from ocr_handler import SecureVisionOCR
        vision = SecureVisionOCR()
        assert vision.client is not None
        assert vision.model_name == "gemini-2.0-flash"

    def test_extract_text_from_image(self, ocr):
        images = [
            f for f in SAMPLE_DIR.glob("*")
            if f.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
        ]
        if not images:
            pytest.skip("No sample images in sample_images/")
        result = ocr.extract_text_from_image(str(images[0]))
        assert isinstance(result, str) and len(result) > 0
        print(f"\n[full-image OCR] {images[0].name}:\n{result}\n")

    def test_extract_text_from_bytes(self, ocr):
        images = list(SAMPLE_DIR.glob("*.png"))
        if not images:
            pytest.skip("No PNG in sample_images/")
        result = ocr.extract_text_from_bytes(images[0].read_bytes())
        assert isinstance(result, str) and len(result) > 0


# ── Group 3: full pipeline (require GEMINI_API_KEY + crypto library) ─────────

@pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY") and not (Path(__file__).parent / ".env").exists(),
    reason="GEMINI_API_KEY not set",
)
class TestOCRPipeline:
    def test_render_then_ocr_single_cell(self, ocr, synthetic_grid_and_key, tmp_path):
        """Render a grid, crop first stencil cell, OCR it, verify it's a character."""
        import cv2, numpy as np
        from grid_renderer import render_grid_bytes
        from grid_detector import detect_and_align_grid
        from stencil_extractor import extract_stencil_cells, cell_to_bytes, preprocess_cell

        grid, secret_key, stencil_cfg, grid_shape, _ = synthetic_grid_and_key
        png_bytes = render_grid_bytes(grid, grid_shape)
        nparr = np.frombuffer(png_bytes, np.uint8)
        bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        aligned = detect_and_align_grid(bgr)
        cells = extract_stencil_cells(aligned, secret_key, grid_shape)

        coord, first_cell = cells[0]
        processed = preprocess_cell(first_cell)
        cell_png = cell_to_bytes(processed, upscale=True)
        char = ocr.ocr_single_cell(cell_png)
        print(f"\n[single-cell OCR] coord={coord} → '{char}'")
        assert isinstance(char, str)

    def test_full_pipeline_extract_ciphertext(self, synthetic_grid_and_key, tmp_path):
        """Render grid → save PNG → run extract_ciphertext_from_image → verify length."""
        from grid_renderer import render_grid
        from ocr_pipeline import extract_ciphertext_from_image

        grid, secret_key, stencil_cfg, grid_shape, plaintext = synthetic_grid_and_key
        img_path = str(tmp_path / "test_stencil.png")
        render_grid(grid, grid_shape, output_path=img_path)

        ciphertext = extract_ciphertext_from_image(img_path, secret_key, stencil_cfg)
        print(f"\n[pipeline] extracted ciphertext bytes: {ciphertext}")
        assert isinstance(ciphertext, bytes)
        assert len(ciphertext) == len(plaintext)

    def test_full_ocr_decrypt_roundtrip(self, synthetic_grid_and_key, tmp_path):
        """Full round-trip: plaintext → encrypt → render → OCR → decrypt → plaintext."""
        from grid_renderer import render_grid
        from ocr_pipeline import full_ocr_decrypt

        grid, secret_key, stencil_cfg, grid_shape, plaintext = synthetic_grid_and_key
        img_path = str(tmp_path / "test_stencil_roundtrip.png")
        render_grid(grid, grid_shape, output_path=img_path)

        recovered = full_ocr_decrypt(img_path, secret_key, stencil_cfg)
        print(f"\n[round-trip] original={plaintext!r}  recovered={recovered!r}")
        assert recovered == plaintext, (
            f"Round-trip failed: original={plaintext!r}, recovered={recovered!r}"
        )
