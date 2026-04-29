"""
grid_detector.py — Receiver-side image preprocessing.

Takes a raw camera/scan image of the printed stencil grid and returns:
  1. A cropped, perspective-corrected numpy array of just the grid region.
  2. The estimated cell dimensions (cell_h, cell_w) in pixels.

Strategy:
  - Primary  : find the largest rectangular contour (the printed grid border).
  - Fallback : if no clear border is detected, treat the full image as the grid.

Perspective correction handles photos taken at an angle (not dead-on).
"""

import cv2
import numpy as np


# ── helpers ─────────────────────────────────────────────────────────────────

def _order_corner_points(pts: np.ndarray) -> np.ndarray:
    """
    Sort 4 corner points as [top-left, top-right, bottom-right, bottom-left].
    Works for any quadrilateral returned by findContours.
    """
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]   # top-left     (min x+y)
    rect[2] = pts[np.argmax(s)]   # bottom-right (max x+y)
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # top-right    (min y-x)
    rect[3] = pts[np.argmax(diff)]  # bottom-left  (max y-x)
    return rect


def _four_point_transform(image: np.ndarray, pts: np.ndarray) -> np.ndarray:
    """Apply perspective warp to straighten a quadrilateral region."""
    rect = _order_corner_points(pts)
    tl, tr, br, bl = rect

    # compute output width: max of top-edge and bottom-edge lengths
    w_top    = np.linalg.norm(tr - tl)
    w_bottom = np.linalg.norm(br - bl)
    out_w    = int(max(w_top, w_bottom))

    # compute output height
    h_left  = np.linalg.norm(bl - tl)
    h_right = np.linalg.norm(br - tr)
    out_h   = int(max(h_left, h_right))

    dst = np.array(
        [[0, 0], [out_w - 1, 0], [out_w - 1, out_h - 1], [0, out_h - 1]],
        dtype="float32",
    )
    M = cv2.getPerspectiveTransform(rect, dst)
    return cv2.warpPerspective(image, M, (out_w, out_h))


# ── public API ───────────────────────────────────────────────────────────────

def load_image(image_path: str) -> np.ndarray:
    """Load image from file path into a BGR numpy array."""
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Could not load image: {image_path}")
    return img


def detect_and_align_grid(image: np.ndarray) -> np.ndarray:
    """
    Detect the stencil grid in a camera/scan image and return a
    perspective-corrected crop containing only the grid.

    Args:
        image: BGR numpy array (from cv2.imread or camera frame).

    Returns:
        Aligned BGR numpy array of the grid region.
    """
    gray    = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges   = cv2.Canny(blurred, threshold1=50, threshold2=150)

    # dilate edges slightly to close small gaps in grid lines
    kernel  = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    dilated = cv2.dilate(edges, kernel, iterations=1)

    contours, _ = cv2.findContours(
        dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        return image  # fallback: full image

    # Pick the largest contour by area
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    for contour in contours[:5]:  # inspect top-5 candidates
        peri   = cv2.arcLength(contour, closed=True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, closed=True)

        if len(approx) == 4:
            # Found a quadrilateral — apply perspective correction
            pts = approx.reshape(4, 2).astype("float32")
            return _four_point_transform(image, pts)

    # Fallback: largest bounding rect (no perspective correction)
    x, y, w, h = cv2.boundingRect(contours[0])
    return image[y : y + h, x : x + w]


def estimate_cell_size(
    grid_image: np.ndarray, rows: int, cols: int
) -> tuple[int, int]:
    """
    Estimate per-cell pixel dimensions given known grid dimensions.

    Args:
        grid_image : aligned grid image (output of detect_and_align_grid).
        rows, cols : number of rows and columns in the logical grid.

    Returns:
        (cell_h, cell_w) in pixels.
    """
    h, w = grid_image.shape[:2]
    return h // rows, w // cols


def refine_cell_size_from_lines(
    grid_image: np.ndarray, rows: int, cols: int
) -> tuple[int, int]:
    """
    Attempt to detect actual grid lines via Hough transform to get more
    accurate cell dimensions. Falls back to estimate_cell_size on failure.
    """
    gray = cv2.cvtColor(grid_image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)

    h_lines = cv2.HoughLinesP(
        binary, 1, np.pi / 180,
        threshold=80, minLineLength=grid_image.shape[1] // 3, maxLineGap=10
    )
    v_lines = cv2.HoughLinesP(
        binary, 1, np.pi / 180,
        threshold=80, minLineLength=grid_image.shape[0] // 3, maxLineGap=10
    )

    def _spacing(lines, axis):
        if lines is None or len(lines) < 2:
            return None
        coords = sorted(set(
            int(l[0][axis]) for l in lines
            if abs(l[0][axis] - l[0][axis + 2]) < 10  # near-horizontal/vertical
        ))
        if len(coords) < 2:
            return None
        gaps = [coords[i + 1] - coords[i] for i in range(len(coords) - 1)]
        return int(np.median(gaps))

    cell_h = _spacing(h_lines, 1) or (grid_image.shape[0] // rows)
    cell_w = _spacing(v_lines, 0) or (grid_image.shape[1] // cols)
    return cell_h, cell_w
