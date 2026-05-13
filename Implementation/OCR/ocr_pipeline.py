"""
ocr_pipeline.py — Mode B: Full end-to-end OCR decryption pipeline.

This is the integration layer that wires together every OCR module and
the stencil_lib. It is the receiver-side counterpart to the sender's
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
            ▼  SecureVisionOCR.ocr_single_cell()  — local TrOCR, no API
    [OCR'd byte value at each stencil coordinate]
            │
            ▼  Reconstruct Grid object with OCR'd values
    [Grid object — same type as steganography_encrypt output]
            │
            ▼  stencil_lib.decrypt(grid, secret_key, stencil_cfg)
    [Plaintext bytes]

Import pattern follows the stencil_system.ipynb notebook convention:
    locate the built wheel in build/dist/, install it, then import stencil_lib.
    Run 'inv build' inside Implementation/ before using this module.
"""

import os
import sys
import subprocess
import pathlib

# ── stencil_lib import (wheel-based, matches notebook convention) ─────────────
_here = pathlib.Path(__file__).parent          # Implementation/OCR/
_search_paths = [
    _here / ".." / "build" / "dist",           # built wheel location
]
_wheel = next(
    (str(w) for p in _search_paths for w in p.glob("stencil_lib-*.whl")),
    None,
)
if _wheel is None:
    raise FileNotFoundError(
        "stencil_lib wheel not found. "
        "Run 'inv build' inside Implementation/ before using ocr_pipeline."
    )
subprocess.check_call(
    [sys.executable, "-m", "pip", "install", "--quiet", _wheel, "--force-reinstall"]
)

import stencil_lib  # noqa: E402  — installed above

from grid_renderer     import render_grid, char_to_byte          # noqa: E402
from grid_detector     import load_image, detect_and_align_grid, estimate_cell_size  # noqa: E402
from stencil_extractor import (  # noqa: E402
    extract_stencil_cells,
    cell_to_bytes,
    preprocess_cell,
)
from ocr_handler import SecureVisionOCR  # noqa: E402


# ── sender side ───────────────────────────────────────────────────────────────

def render_stencil_image(
    grid: stencil_lib.Grid,
    grid_shape: stencil_lib.GridShape,
    output_path: str,
) -> str:
    """
    Sender utility: convert an obfuscated Grid (output of stencil_lib.encrypt)
    to a printable PNG for fax / screen / camera transmission.

    Args:
        grid        : stencil_lib.Grid — output of stencil_lib.encrypt().
        grid_shape  : stencil_lib.GridShape matching the grid dimensions.
        output_path : File path to save the PNG.

    Returns:
        Absolute path of the saved PNG.
    """
    render_grid(grid, grid_shape, output_path=output_path)
    return os.path.abspath(output_path)


# ── receiver side — core ──────────────────────────────────────────────────────

def ocr_image_to_grid(
    image_path: str,
    secret_key: stencil_lib.SecretKey,
    stencil_cfg: stencil_lib.StencilConfig,
    preprocess: bool = True,
    mode: str = "printed",
) -> stencil_lib.Grid:
    """
    Read a stencil image via local TrOCR and reconstruct a stencil_lib.Grid.

    Each stencil coordinate is read by TrOCR (offline, CPU-only). The
    resulting character is converted back to its byte value and placed at
    the correct coordinate in a new Grid. Non-stencil cells stay empty
    (not needed by steganography_decrypt — it only reads stencil positions).

    Args:
        image_path  : Path to the camera/scan image of the printed stencil.
        secret_key  : stencil_lib.SecretKey from the key exchange.
        stencil_cfg : stencil_lib.StencilConfig used during encryption.
        preprocess  : Apply per-cell adaptive threshold before OCR.
                      Recommended for real camera images; disable for clean
                      synthetic/rendered images.
        mode        : "printed" for typed/rendered grids (default),
                      "handwritten" for physically handwritten grids.

    Returns:
        stencil_lib.Grid with OCR'd byte values at all stencil coordinates.
    """
    if stencil_cfg.grid_shape.n != 2:
        raise ValueError("OCR pipeline only supports 2-D grids (n=2).")

    ocr = SecureVisionOCR(mode=mode)

    # Step 1 — load and perspective-correct the grid image
    raw_image  = load_image(image_path)
    grid_image = detect_and_align_grid(raw_image)

    rows, cols = stencil_cfg.grid_shape.shape
    cell_h, cell_w = estimate_cell_size(grid_image, rows, cols)

    # Step 2 — crop one cell image per stencil coordinate
    cells = extract_stencil_cells(
        grid_image, secret_key, stencil_cfg.grid_shape, cell_h, cell_w
    )

    # Step 3 — local TrOCR per cell → reconstruct grid dict
    grid_data: dict = {}
    for coord, cell_bgr in cells:
        if preprocess:
            cell_bgr = preprocess_cell(cell_bgr)
        cell_png  = cell_to_bytes(cell_bgr, upscale=True)
        char_str  = ocr.ocr_single_cell(cell_png)
        grid_data[coord] = char_to_byte(char_str[0]) if char_str else 0

    return stencil_lib.Grid(data=grid_data)


def full_ocr_decrypt(
    image_path: str,
    secret_key: stencil_lib.SecretKey,
    stencil_cfg: stencil_lib.StencilConfig,
    preprocess: bool = True,
    mode: str = "printed",
) -> bytes:
    """
    Convenience: camera image → plaintext in one call.

    Reconstructs a Grid from local TrOCR, then passes it to
    stencil_lib.decrypt() — all crypto logic stays inside stencil_lib.

    Args:
        image_path  : Path to the stencil image.
        secret_key  : stencil_lib.SecretKey.
        stencil_cfg : stencil_lib.StencilConfig used during encryption.
        preprocess  : Apply cell preprocessing before OCR.
        mode        : "printed" or "handwritten".

    Returns:
        Recovered plaintext as bytes.
    """
    reconstructed_grid = ocr_image_to_grid(
        image_path, secret_key, stencil_cfg,
        preprocess=preprocess, mode=mode,
    )
    # All crypto (steganography_decrypt + cipher_decrypt + permutations)
    # is handled internally by stencil_lib.decrypt — not duplicated here.
    return stencil_lib.decrypt(reconstructed_grid, secret_key, stencil_cfg)


# ── diagnostic helpers ────────────────────────────────────────────────────────

def diagnose_pipeline(
    image_path: str,
    secret_key: stencil_lib.SecretKey,
    stencil_cfg: stencil_lib.StencilConfig,
    output_dir: str = ".",
    mode: str = "printed",
) -> dict:
    """
    Run the pipeline and save intermediate images for debugging.
    Saves aligned grid, annotated grid, and per-cell crops to output_dir.
    """
    import cv2 as _cv2
    from stencil_extractor import annotate_grid_with_coords

    os.makedirs(output_dir, exist_ok=True)
    ocr = SecureVisionOCR(mode=mode)

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
        "aligned_grid"  : os.path.join(output_dir, "debug_aligned.png"),
        "annotated_grid": os.path.join(output_dir, "debug_annotated.png"),
        "cells"         : results,
    }
