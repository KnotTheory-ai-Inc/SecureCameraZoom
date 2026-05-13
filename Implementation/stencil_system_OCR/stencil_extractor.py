import io
import cv2
import numpy as np
from PIL import Image

CROP_INSET = 3
UPSCALE_FACTOR = 4


def extract_all_cells(
    grid_image: np.ndarray,
    rows: int,
    cols: int,
    cell_h: int = None,
    cell_w: int = None,
) -> list[tuple[tuple, np.ndarray]]:
    img_h, img_w = grid_image.shape[:2]
    if cell_h is None:
        cell_h = img_h // rows
    if cell_w is None:
        cell_w = img_w // cols

    results = []
    for r in range(rows):
        for c in range(cols):
            y1 = r * cell_h + CROP_INSET
            y2 = min((r + 1) * cell_h - CROP_INSET, img_h)
            x1 = c * cell_w + CROP_INSET
            x2 = min((c + 1) * cell_w - CROP_INSET, img_w)
            crop = grid_image[y1:y2, x1:x2]
            if crop.size == 0:
                crop = np.full((cell_h, cell_w, 3), 255, dtype=np.uint8)
            results.append(((r, c), crop))
    return results


def extract_stencil_cells(
    grid_image: np.ndarray,
    secret_key,
    grid_shape,
    cell_h: int = None,
    cell_w: int = None,
) -> list[tuple[tuple, np.ndarray]]:
    rows, cols = grid_shape.shape
    img_h, img_w = grid_image.shape[:2]
    if cell_h is None:
        cell_h = img_h // rows
    if cell_w is None:
        cell_w = img_w // cols

    results = []
    for stencil in secret_key.stencils:
        for coord in stencil.coords:
            row, col = coord
            y1 = row * cell_h + CROP_INSET
            y2 = min((row + 1) * cell_h - CROP_INSET, img_h)
            x1 = col * cell_w + CROP_INSET
            x2 = min((col + 1) * cell_w - CROP_INSET, img_w)
            crop = grid_image[y1:y2, x1:x2]
            if crop.size == 0:
                crop = np.full((cell_h, cell_w, 3), 255, dtype=np.uint8)
            results.append((coord, crop))
    return results


def cell_to_pil(cell_bgr: np.ndarray, upscale: bool = True) -> Image.Image:
    rgb = cv2.cvtColor(cell_bgr, cv2.COLOR_BGR2RGB)
    pil = Image.fromarray(rgb)
    if upscale and UPSCALE_FACTOR > 1:
        pil = pil.resize((pil.width * UPSCALE_FACTOR, pil.height * UPSCALE_FACTOR), Image.NEAREST)
    return pil


def cell_to_bytes(cell_bgr: np.ndarray, upscale: bool = True) -> bytes:
    buf = io.BytesIO()
    cell_to_pil(cell_bgr, upscale=upscale).save(buf, format="PNG")
    return buf.getvalue()


def preprocess_cell(cell_bgr: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(cell_bgr, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, h=10)
    thresh = cv2.adaptiveThreshold(
        denoised, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        blockSize=11,
        C=2,
    )
    return cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)


def annotate_grid_with_coords(
    grid_image: np.ndarray,
    secret_key,
    grid_shape,
    cell_h: int = None,
    cell_w: int = None,
) -> np.ndarray:
    annotated = grid_image.copy()
    rows, cols = grid_shape.shape
    img_h, img_w = annotated.shape[:2]
    if cell_h is None:
        cell_h = img_h // rows
    if cell_w is None:
        cell_w = img_w // cols

    colours = [(0, 0, 220), (0, 180, 0), (200, 0, 200), (0, 180, 180)]
    for s_idx, stencil in enumerate(secret_key.stencils):
        colour = colours[s_idx % len(colours)]
        for coord in stencil.coords:
            row, col = coord
            y1, y2 = row * cell_h, min((row + 1) * cell_h, img_h)
            x1, x2 = col * cell_w, min((col + 1) * cell_w, img_w)
            cv2.rectangle(annotated, (x1, y1), (x2, y2), colour, thickness=2)
    return annotated
