"""
ocr_handler.py — Local OCR engine (zero cloud, zero API key).

Uses Microsoft TrOCR via HuggingFace Transformers — runs 100% offline
on CPU after a one-time model download.

Model strategy:
  Primary   : microsoft/trocr-small-printed   (62 MB, ~80 ms/cell on CPU)
              → for rendered/printed grid cells (the normal case)
  Fallback  : microsoft/trocr-small-handwritten (62 MB)
              → for physically handwritten grids photographed by camera

Why TrOCR:
  - Designed for single text-line / single-character image input — exactly
    what stencil_extractor.py produces.
  - 62 M parameters → runs on any edge CPU including embedded CCTV hardware.
  - No network socket after download. Works in air-gapped environments.
  - Pure HuggingFace transformers: pip install transformers torch

Download models once:
    from transformers import TrOCRProcessor, VisionEncoderDecoderModel
    TrOCRProcessor.from_pretrained("microsoft/trocr-small-printed")
    VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-small-printed")
"""

import io
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import torch

# Model IDs — both downloaded once and cached locally by HuggingFace
_PRINTED_MODEL_ID     = "microsoft/trocr-small-printed"
_HANDWRITTEN_MODEL_ID = "microsoft/trocr-small-handwritten"


class SecureVisionOCR:
    """
    Local OCR engine for the SecureCameraZoom stencil pipeline.

    Wraps TrOCR (printed + handwritten variants) for fully offline,
    CPU-based character recognition. No API key, no network required
    after the initial model download.

    Args:
        mode : "printed"     — for rendered / typed grid images (default)
               "handwritten" — for physically handwritten grids
    """

    def __init__(self, mode: str = "printed"):
        model_id = _PRINTED_MODEL_ID if mode == "printed" else _HANDWRITTEN_MODEL_ID
        self.processor = TrOCRProcessor.from_pretrained(model_id)
        self.model     = VisionEncoderDecoderModel.from_pretrained(model_id)
        self.model.eval()                     # inference mode — no gradient tracking
        self._device   = "cpu"                # edge devices have no GPU
        self.model.to(self._device)

    # ── internal helper ───────────────────────────────────────────────────────

    def _run(self, pil_image: Image.Image) -> str:
        """Core inference: PIL image → text string."""
        if pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")
        pixel_values = self.processor(images=pil_image, return_tensors="pt").pixel_values
        pixel_values = pixel_values.to(self._device)
        with torch.no_grad():
            generated_ids = self.model.generate(pixel_values)
        return self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()

    # ── general OCR ───────────────────────────────────────────────────────────

    def extract_text_from_image(self, image_path: str) -> str:
        """
        Run OCR on an image file. Returns extracted text as a stripped string.
        Compatible with the original Gemini-based API signature.
        """
        pil = Image.open(image_path)
        return self._run(pil)

    def extract_text_from_bytes(self, image_bytes: bytes, mime_type: str = "image/png") -> str:
        """
        Run OCR on raw image bytes (no disk I/O).
        Useful for live camera frames piped directly from cv2.
        Compatible with the original Gemini-based API signature.
        """
        pil = Image.open(io.BytesIO(image_bytes))
        return self._run(pil)

    # ── stencil-aware OCR ─────────────────────────────────────────────────────

    def ocr_single_cell(self, cell_bytes: bytes, mime_type: str = "image/png") -> str:
        """
        OCR a single magnified grid cell — expects exactly ONE character.

        Used by ocr_pipeline.extract_ciphertext_from_image() for each
        stencil coordinate.

        TrOCR was specifically trained on single text-line images, making
        it ideal for individual character cell crops.

        Args:
            cell_bytes : PNG bytes of the upscaled cell crop.
            mime_type  : MIME type (default image/png, ignored — PIL auto-detects).

        Returns:
            First character of the OCR result, or empty string if unreadable.
        """
        text = self.extract_text_from_bytes(cell_bytes)
        return text[0] if text else ""

    def ocr_grid_region(
        self,
        image_bytes: bytes,
        rows: int,
        cols: int,
        mime_type: str = "image/png",
    ) -> list[list[str]]:
        """
        Batch OCR a full grid image in one pass.

        Passes the whole aligned grid to TrOCR. Parses the flat string
        response back into a 2-D list[row][col] of characters.

        Note: TrOCR reads left-to-right top-to-bottom, matching our grid
        rendering order. Results may be less accurate than per-cell OCR
        for grids with tightly packed random characters.

        Args:
            image_bytes : PNG bytes of the full aligned grid image.
            rows, cols  : Logical grid dimensions (from GridShape).
            mime_type   : Ignored — PIL auto-detects format.

        Returns:
            2-D list: result[row][col] = char, or '?' for unreadable cells.
        """
        flat = self.extract_text_from_bytes(image_bytes)
        flat = flat.replace("\n", "").replace(" ", "")
        flat = flat.ljust(rows * cols, "?")[: rows * cols]

        return [list(flat[r * cols : (r + 1) * cols]) for r in range(rows)]
