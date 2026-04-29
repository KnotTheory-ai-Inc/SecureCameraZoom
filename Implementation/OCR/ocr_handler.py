"""
ocr_handler.py — Gemini Vision OCR wrapper (SecureVisionOCR).

Two categories of methods:

  General OCR (original):
    extract_text_from_image(image_path)  — full image OCR
    extract_text_from_bytes(image_bytes) — in-memory image OCR

  Stencil-aware OCR (new):
    ocr_single_cell(cell_bytes)          — single character cell, tight prompt
    ocr_grid_region(image_bytes, coords) — batch: full grid image + coordinate hints
"""

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types


# ── system prompts ────────────────────────────────────────────────────────────

_SYSTEM_FULL_IMAGE = (
    "You are an expert OCR vision system. Scan the image for any hidden structural markers, "
    "grids, or bounding boxes. Zoom your attention to that specific region. Transcribe any "
    "handwritten or printed text (including cursive) exactly as written. Return ONLY the raw "
    "extracted text, with absolutely no conversational filler or formatting."
)

_SYSTEM_SINGLE_CELL = (
    "You are a precision OCR system reading a single character from a magnified grid cell. "
    "The image contains exactly ONE printed or handwritten character. "
    "Return ONLY that single character — no spaces, no punctuation, no explanation. "
    "If the character is ambiguous, return your best single-character guess."
)

_SYSTEM_GRID_REGION = (
    "You are a cryptographic OCR system. The image is a section of an obfuscated character grid. "
    "Read every character exactly as printed. Return the characters as a flat string with no spaces "
    "or separators — one character per grid cell, left-to-right, top-to-bottom. "
    "Do not guess or hallucinate. If a cell is unreadable, output a '?' for that position."
)


class SecureVisionOCR:
    """
    Gemini-powered OCR for the SecureCameraZoom stencil pipeline.

    Initialisation loads GEMINI_API_KEY from the .env file in the same
    directory and configures the google-genai client.
    """

    def __init__(self):
        load_dotenv()
        self.client     = genai.Client()
        self.model_name = "gemini-2.0-flash"
        self._config_full  = types.GenerateContentConfig(system_instruction=_SYSTEM_FULL_IMAGE)
        self._config_cell  = types.GenerateContentConfig(system_instruction=_SYSTEM_SINGLE_CELL)
        self._config_grid  = types.GenerateContentConfig(system_instruction=_SYSTEM_GRID_REGION)

    # ── general OCR ───────────────────────────────────────────────────────────

    def extract_text_from_image(self, image_path: str) -> str:
        """
        Upload an image file and run full-image OCR.
        Returns extracted text as a stripped string.
        """
        uploaded_file = self.client.files.upload(file=image_path)
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=uploaded_file,
            config=self._config_full,
        )
        return response.text.strip()

    def extract_text_from_bytes(self, image_bytes: bytes, mime_type: str = "image/png") -> str:
        """
        Run OCR on an in-memory image (raw bytes).
        Useful for live camera frames without disk I/O.
        """
        part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=part,
            config=self._config_full,
        )
        return response.text.strip()

    # ── stencil-aware OCR ─────────────────────────────────────────────────────

    def ocr_single_cell(self, cell_bytes: bytes, mime_type: str = "image/png") -> str:
        """
        OCR a single magnified grid cell — expects exactly ONE character.

        Used by ocr_pipeline.extract_ciphertext_from_image() for each
        stencil coordinate. The tight system prompt tells Gemini to return
        only the single character, eliminating OCR noise.

        Args:
            cell_bytes : PNG bytes of the upscaled cell crop.
            mime_type  : MIME type of cell_bytes (default image/png).

        Returns:
            Single character string, or empty string if unreadable.
        """
        part = types.Part.from_bytes(data=cell_bytes, mime_type=mime_type)
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=part,
            config=self._config_cell,
        )
        text = response.text.strip()
        # Return exactly the first character only — guard against verbose responses
        return text[0] if text else ""

    def ocr_grid_region(
        self,
        image_bytes: bytes,
        rows: int,
        cols: int,
        mime_type: str = "image/png",
    ) -> list[list[str]]:
        """
        Batch OCR a full grid image in one API call.

        Sends the whole aligned grid image to Gemini with a prompt that
        asks for all characters in reading order. Parses the flat string
        response back into a 2-D list[row][col].

        Fewer API calls than ocr_single_cell() but less accurate for
        stencil extraction — recommended only when quota is tight.

        Args:
            image_bytes : PNG bytes of the full aligned grid image.
            rows, cols  : Logical grid dimensions (from GridShape).
            mime_type   : MIME type.

        Returns:
            2-D list of characters: result[row][col] = char (or '?' if unreadable).
        """
        user_prompt = (
            f"The grid has {rows} rows and {cols} columns. "
            f"Return exactly {rows * cols} characters as a flat string."
        )
        part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[part, user_prompt],
            config=self._config_grid,
        )
        flat = response.text.strip().replace("\n", "").replace(" ", "")
        # Pad or trim to exact expected length
        flat = flat.ljust(rows * cols, "?")[: rows * cols]

        grid_chars = []
        for r in range(rows):
            row_chars = list(flat[r * cols : (r + 1) * cols])
            grid_chars.append(row_chars)
        return grid_chars
