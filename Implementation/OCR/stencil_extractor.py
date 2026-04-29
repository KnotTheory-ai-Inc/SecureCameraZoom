"""
stencil_extractor.py — Maps SecretKey stencil coordinates to pixel crops.

Given the aligned grid image (output of grid_detector) and the SecretKey,
this module extracts one cropped image per stencil coordinate — ordered
exactly as the reading order the receiver uses to reassemble ciphertext.

The OCR module then runs on each individual crop, reading one character per cell.
Single-character crops give Gemini a much simpler task than full-grid OCR and
dramatically improve accuracy.

Coordinate ordering (critical for correct ciphertext reconstruction):
    We iterate stencils in SecretKey.stencils order, and within each stencil
    iterate coords in stencil.coords order. This mirrors how steganography_decrypt
    walks the stencils — the i-th byte OCR'd must correspond to the i-th grid position
    that steganography_encrypt placed a ciphertext byte.
"""

import io
import cv2
import numpy as np
from PIL import Image


# How much to pad inward (pixels) when cropping each cell.
# Removes grid-line pixels that confuse the OCR model.
CROP_INSET = 3

# Upscale factor before sending to OCR — Gemini handles large images better.
UPSCALE_FACTOR = 4


# ── core extraction ──────────────────────────────────────────────────────────

def extract_stencil_cells(
    grid_image: np.ndarray,
    secret_key,
    grid_shape,
    cell_h: int = None,
    cell_w: int = None,
) -> list[tuple[tuple, np.ndarray]]:
    """
    Extract per-cell image crops for every stencil coordinate.

    Args:
        grid_image : Aligned BGR grid image (output of detect_and_align_grid).
        secret_key : SecretKey with .stencils (list of Stencil objects).
        grid_shape : GridShape with .shape = (rows, cols).
        cell_h     : Cell height in pixels. Auto-computed if None.
        cell_w     : Cell width  in pixels. Auto-computed if None.

    Returns:
        List of (coord, cell_bgr) pairs in stencil reading order.
        coord     : (row, col) tuple matching SecretKey coordinates.
        cell_bgr  : BGR numpy array of the cropped cell.
    """
    rows, cols = grid_shape.shape
    img_h, img_w = grid_image.shape[:2]

    if cell_h is None:
        cell_h = img_h // rows
    if cell_w is None:
        cell_w = img_w // cols

    results: list[tuple[tuple, np.ndarray]] = []

    for stencil in secret_key.stencils:
        for coord in stencil.coords:
            row, col = coord

            # pixel bounding box of this cell
            y1 = row * cell_h + CROP_INSET
            y2 = min((row + 1) * cell_h - CROP_INSET, img_h)
            x1 = col * cell_w + CROP_INSET
            x2 = min((col + 1) * cell_w - CROP_INSET, img_w)

            crop = grid_image[y1:y2, x1:x2]

            if crop.size == 0:
                # Coordinate out of bounds — return white placeholder
                crop = np.full((cell_h, cell_w, 3), 255, dtype=np.uint8)

            results.append((coord, crop))

    return results


# ── format conversion helpers ────────────────────────────────────────────────

def cell_to_pil(cell_bgr: np.ndarray, upscale: bool = True) -> Image.Image:
    """Convert a BGR cell crop to a PIL Image, optionally upscaling for OCR."""
    rgb = cv2.cvtColor(cell_bgr, cv2.COLOR_BGR2RGB)
    pil = Image.fromarray(rgb)
    if upscale and UPSCALE_FACTOR > 1:
        new_w = pil.width  * UPSCALE_FACTOR
        new_h = pil.height * UPSCALE_FACTOR
        pil = pil.resize((new_w, new_h), Image.NEAREST)
    return pil


def cell_to_bytes(cell_bgr: np.ndarray, upscale: bool = True) -> bytes:
    """Convert a BGR cell crop to PNG bytes ready for Gemini's file API."""
    pil = cell_to_pil(cell_bgr, upscale=upscale)
    buf = io.BytesIO()
    pil.save(buf, format="PNG")
    return buf.getvalue()


def preprocess_cell(cell_bgr: np.ndarray) -> np.ndarray:
    """
    Optional per-cell preprocessing to improve OCR accuracy:
      - Convert to grayscale
      - Adaptive threshold (handles uneven lighting from camera)
      - Light denoise
    Returns BGR image (re-converted so Gemini gets a colour-safe image).
    """
    gray    = cv2.cvtColor(cell_bgr, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, h=10)
    thresh  = cv2.adaptiveThreshold(
        denoised, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        blockSize=11,
        C=2,
    )
    return cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)


# ── debug / visualisation ────────────────────────────────────────────────────

def annotate_grid_with_coords(
    grid_image: np.ndarray,
    secret_key,
    grid_shape,
    cell_h: int = None,
    cell_w: int = None,
) -> np.ndarray:
    """
    Draw coloured rectangles over every stencil cell in the grid image.
    Useful for debugging coordinate alignment before running OCR.

    Returns annotated BGR image.
    """
    annotated = grid_image.copy()
    rows, cols = grid_shape.shape
    img_h, img_w = annotated.shape[:2]
    if cell_h is None:
        cell_h = img_h // rows
    if cell_w is None:
        cell_w = img_w // cols

    colours = [
        (0, 0, 220),    # red
        (0, 180, 0),    # green
        (200, 0, 200),  # magenta
        (0, 180, 180),  # yellow
    ]

    for s_idx, stencil in enumerate(secret_key.stencils):
        colour = colours[s_idx % len(colours)]
        for coord in stencil.coords:
            row, col = coord
            y1 = row * cell_h
            y2 = min((row + 1) * cell_h, img_h)
            x1 = col * cell_w
            x2 = min((col + 1) * cell_w, img_w)
            cv2.rectangle(annotated, (x1, y1), (x2, y2), colour, thickness=2)

    return annotated
