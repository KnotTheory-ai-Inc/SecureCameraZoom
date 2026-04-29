"""
ocr_pipeline.py — Mode B: Full end-to-end OCR decryption pipeline.

This is the integration layer that wires together every OCR module and
the crypto library. It is the receiver-side counterpart to the sender's
encrypt() call.

Full pipeline (Mode B — camera/image path):

    [Camera Image of Printed Stencil Grid]
            │
            ▼  grid_detector.detect_and_align_grid()
    [Perspective-corrected Grid Image]
            │
            ▼  stencil_extractor.extract_stencil_cells()
    [Per-cell crops, ordered by SecretKey stencil reading order]
            │
            ▼  SecureVisionOCR.ocr_single_cell()  (per cell)
    [Extracted character per stencil position]
            │
            ▼  inverse cipher permutation  (if StencilConfig.enable_cipher_permutation)
    [Ciphertext bytes]
            │
            ▼  stencil_lib.decrypt()   ← crypto team calls this
    [Plaintext]

Public functions:
    extract_ciphertext_from_image()   — receiver extracts ciphertext from image
    render_stencil_image()            — sender renders Grid → PNG for printing
    full_ocr_decrypt()                — convenience: image → plaintext in one call

sys.path injection:
    This module adds ../src/python to sys.path so it can import
    SecretKey, GridShape, StencilConfig from the crypto library
    without requiring the wheel to be installed.
"""

import os
import sys

# Make the stencil_lib importable from OCR/ without wheel installation
_SRC = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "src", "python")
)
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from common.classes import Grid, GridShape, SecretKey, StencilConfig  # noqa: E402
from Decryption.cipher_decrypt import cipher_decrypt                   # noqa: E402

from grid_renderer    import render_grid, render_grid_bytes, byte_to_char, char_to_byte  # noqa: E402
from grid_detector    import load_image, detect_and_align_grid, estimate_cell_size       # noqa: E402
from stencil_extractor import (                                                           # noqa: E402
    extract_stencil_cells,
    cell_to_bytes,
    preprocess_cell,
)
from ocr_handler import SecureVisionOCR                                # noqa: E402


# ── sender side ──────────────────────────────────────────────────────────────

def render_stencil_image(grid: Grid, grid_shape: GridShape, output_path: str) -> str:
    """
    Sender utility: convert an obfuscated Grid to a printable PNG.

    Args:
        grid        : Output of encrypt() — the obfuscated grid.
        grid_shape  : GridShape matching the grid dimensions.
        output_path : Where to save the PNG file.

    Returns:
        Absolute path of the saved PNG.
    """
    render_grid(grid, grid_shape, output_path=output_path)
    return os.path.abspath(output_path)


# ── receiver side ─────────────────────────────────────────────────────────────

def extract_ciphertext_from_image(
    image_path: str,
    secret_key: SecretKey,
    stencil_cfg: StencilConfig,
    preprocess: bool = True,
) -> bytes:
    """
    Mode B pipeline: camera image of the stencil → ciphertext bytes.

    This is the drop-in replacement for steganography_decrypt() when the
    grid is received as a physical image rather than a byte stream.

    Args:
        image_path  : Path to the camera/scan image of the printed stencil.
        secret_key  : SecretKey from the key exchange (stencils + permutations).
        stencil_cfg : StencilConfig used during encryption (same instance).
        preprocess  : Apply per-cell adaptive threshold before OCR (recommended
                      for real camera images; disable for clean synthetic images).

    Returns:
        Ciphertext bytes in the same format as steganography_decrypt().

    Raises:
        FileNotFoundError : if image_path does not exist.
        ValueError        : if the grid shape is not 2-D.
    """
    if stencil_cfg.grid_shape.n != 2:
        raise ValueError("OCR pipeline only supports 2-D grids.")

    ocr = SecureVisionOCR()

    # Step 1 — load + perspective-correct the grid image
    raw_image  = load_image(image_path)
    grid_image = detect_and_align_grid(raw_image)

    rows, cols = stencil_cfg.grid_shape.shape
    cell_h, cell_w = estimate_cell_size(grid_image, rows, cols)

    # Step 2 — crop one image per stencil coordinate (in reading order)
    cells = extract_stencil_cells(
        grid_image, secret_key, stencil_cfg.grid_shape, cell_h, cell_w
    )

    # Step 3 — OCR each cell → one character per stencil position
    raw_bytes = bytearray()
    for coord, cell_bgr in cells:
        if preprocess:
            cell_bgr = preprocess_cell(cell_bgr)

        cell_png = cell_to_bytes(cell_bgr, upscale=True)
        char_str = ocr.ocr_single_cell(cell_png)

        if char_str:
            raw_bytes.append(char_to_byte(char_str[0]))
        else:
            raw_bytes.append(0)   # unreadable cell — safe zero fill

    ciphertext = bytes(raw_bytes)

    # Step 4 — apply inverse cipher permutation if it was used during encryption
    if stencil_cfg.enable_cipher_permutation and secret_key.cipher_permutation:
        inv = [0] * len(secret_key.cipher_permutation)
        for i, p in enumerate(secret_key.cipher_permutation):
            inv[p] = i
        ciphertext = bytes(ciphertext[i] for i in inv)

    return ciphertext


def full_ocr_decrypt(
    image_path: str,
    secret_key: SecretKey,
    stencil_cfg: StencilConfig,
    preprocess: bool = True,
) -> bytes:
    """
    Convenience function: camera image → plaintext in one call.

    Combines extract_ciphertext_from_image() + cipher_decrypt() so the
    caller does not need to touch the crypto layer directly.

    Args:
        image_path  : Path to the stencil image.
        secret_key  : SecretKey (must include cipher_cfg).
        stencil_cfg : StencilConfig used during encryption.
        preprocess  : Apply cell preprocessing before OCR.

    Returns:
        Recovered plaintext as bytes.
    """
    ciphertext = extract_ciphertext_from_image(
        image_path, secret_key, stencil_cfg, preprocess=preprocess
    )
    return cipher_decrypt(ciphertext, secret_key.cipher_cfg)


# ── diagnostic helpers ────────────────────────────────────────────────────────

def diagnose_pipeline(
    image_path: str,
    secret_key: SecretKey,
    stencil_cfg: StencilConfig,
    output_dir: str = ".",
) -> dict:
    """
    Run the pipeline and save intermediate images for debugging.
    Returns a dict with paths and per-cell OCR results.

    Saves:
        <output_dir>/debug_aligned.png        — perspective-corrected grid
        <output_dir>/debug_annotated.png      — stencil cells highlighted
        <output_dir>/debug_cell_<i>.png       — each extracted cell crop
    """
    from stencil_extractor import annotate_grid_with_coords
    import cv2 as _cv2

    os.makedirs(output_dir, exist_ok=True)
    ocr = SecureVisionOCR()

    raw_image  = load_image(image_path)
    grid_image = detect_and_align_grid(raw_image)
    _cv2.imwrite(os.path.join(output_dir, "debug_aligned.png"), grid_image)

    rows, cols = stencil_cfg.grid_shape.shape
    cell_h, cell_w = estimate_cell_size(grid_image, rows, cols)

    annotated = annotate_grid_with_coords(
        grid_image, secret_key, stencil_cfg.grid_shape, cell_h, cell_w
    )
    _cv2.imwrite(os.path.join(output_dir, "debug_annotated.png"), annotated)

    cells = extract_stencil_cells(
        grid_image, secret_key, stencil_cfg.grid_shape, cell_h, cell_w
    )

    results = []
    for i, (coord, cell_bgr) in enumerate(cells):
        cell_path = os.path.join(output_dir, f"debug_cell_{i:03d}.png")
        processed = preprocess_cell(cell_bgr)
        _cv2.imwrite(cell_path, processed)

        char_str = ocr.ocr_single_cell(cell_to_bytes(processed, upscale=True))
        results.append({"index": i, "coord": coord, "ocr_char": char_str, "cell_path": cell_path})

    return {
        "aligned_grid" : os.path.join(output_dir, "debug_aligned.png"),
        "annotated_grid": os.path.join(output_dir, "debug_annotated.png"),
        "cells"        : results,
    }
