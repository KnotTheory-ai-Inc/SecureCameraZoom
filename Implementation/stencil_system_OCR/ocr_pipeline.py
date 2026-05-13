import os
import sys
import subprocess
import pathlib

_here = pathlib.Path(__file__).parent
_wheel = next(
    (str(w) for p in [_here / ".." / "build" / "dist"] for w in p.glob("stencil_lib-*.whl")),
    None,
)
if _wheel is None:
    raise FileNotFoundError(
        "stencil_lib wheel not found. Run 'inv build' inside Implementation/ first."
    )
subprocess.check_call(
    [sys.executable, "-m", "pip", "install", "--quiet", _wheel, "--force-reinstall"]
)

import stencil_lib  # noqa: E402

from grid_renderer import render_grid, char_to_byte
from grid_detector import load_image, detect_and_align_grid, estimate_cell_size
from stencil_extractor import extract_all_cells, cell_to_bytes, preprocess_cell
from ocr_handler import SecureVisionOCR


def render_stencil_image(grid, grid_shape, output_path: str) -> str:
    render_grid(grid, grid_shape, output_path=output_path)
    return os.path.abspath(output_path)


def ocr_image_to_grid(
    image_path: str,
    stencil_cfg,
    preprocess: bool = True,
    mode: str = "printed",
) -> stencil_lib.Grid:
    if stencil_cfg.grid_shape.n != 2:
        raise ValueError("OCR pipeline only supports 2-D grids (n=2).")

    rows, cols = stencil_cfg.grid_shape.shape
    ocr = SecureVisionOCR(mode=mode)
    grid_image = detect_and_align_grid(load_image(image_path))
    cell_h, cell_w = estimate_cell_size(grid_image, rows, cols)
    cells = extract_all_cells(grid_image, rows, cols, cell_h, cell_w)

    grid_data: dict = {}
    for coord, cell_bgr in cells:
        if preprocess:
            cell_bgr = preprocess_cell(cell_bgr)
        char_str = ocr.ocr_single_cell(cell_to_bytes(cell_bgr, upscale=True))
        grid_data[coord] = char_to_byte(char_str[0]) if char_str else 0

    return stencil_lib.Grid(data=grid_data)


def full_ocr_decrypt(
    image_path: str,
    secret_key,
    stencil_cfg,
    preprocess: bool = True,
    mode: str = "printed",
) -> bytes:
    grid = ocr_image_to_grid(image_path, stencil_cfg, preprocess=preprocess, mode=mode)
    return stencil_lib.decrypt(grid, secret_key, stencil_cfg)


def diagnose_pipeline(
    image_path: str,
    secret_key,
    stencil_cfg,
    output_dir: str = ".",
    mode: str = "printed",
) -> dict:
    import cv2 as _cv2
    from stencil_extractor import annotate_grid_with_coords

    os.makedirs(output_dir, exist_ok=True)
    ocr = SecureVisionOCR(mode=mode)
    rows, cols = stencil_cfg.grid_shape.shape

    raw_image = load_image(image_path)
    grid_image = detect_and_align_grid(raw_image)
    _cv2.imwrite(os.path.join(output_dir, "debug_aligned.png"), grid_image)

    cell_h, cell_w = estimate_cell_size(grid_image, rows, cols)
    annotated = annotate_grid_with_coords(grid_image, secret_key, stencil_cfg.grid_shape, cell_h, cell_w)
    _cv2.imwrite(os.path.join(output_dir, "debug_annotated.png"), annotated)

    cells = extract_all_cells(grid_image, rows, cols, cell_h, cell_w)
    results = []
    for i, (coord, cell_bgr) in enumerate(cells):
        cell_path = os.path.join(output_dir, f"debug_cell_{i:03d}.png")
        processed = preprocess_cell(cell_bgr)
        _cv2.imwrite(cell_path, processed)
        char_str = ocr.ocr_single_cell(cell_to_bytes(processed, upscale=True))
        results.append({"index": i, "coord": coord, "ocr_char": char_str, "cell_path": cell_path})

    return {
        "aligned_grid": os.path.join(output_dir, "debug_aligned.png"),
        "annotated_grid": os.path.join(output_dir, "debug_annotated.png"),
        "cells": results,
    }
