import cv2
import numpy as np


def _order_corner_points(pts: np.ndarray) -> np.ndarray:
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect


def _four_point_transform(image: np.ndarray, pts: np.ndarray) -> np.ndarray:
    rect = _order_corner_points(pts)
    tl, tr, br, bl = rect
    out_w = int(max(np.linalg.norm(tr - tl), np.linalg.norm(br - bl)))
    out_h = int(max(np.linalg.norm(bl - tl), np.linalg.norm(br - tr)))
    dst = np.array([[0, 0], [out_w - 1, 0], [out_w - 1, out_h - 1], [0, out_h - 1]], dtype="float32")
    M = cv2.getPerspectiveTransform(rect, dst)
    return cv2.warpPerspective(image, M, (out_w, out_h))


def load_image(image_path: str) -> np.ndarray:
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Could not load image: {image_path}")
    return img


def detect_and_align_grid(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, threshold1=50, threshold2=150)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    dilated = cv2.dilate(edges, kernel, iterations=1)

    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return image

    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    for contour in contours[:5]:
        peri = cv2.arcLength(contour, closed=True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, closed=True)
        if len(approx) == 4:
            pts = approx.reshape(4, 2).astype("float32")
            return _four_point_transform(image, pts)

    x, y, w, h = cv2.boundingRect(contours[0])
    return image[y: y + h, x: x + w]


def estimate_cell_size(grid_image: np.ndarray, rows: int, cols: int) -> tuple[int, int]:
    h, w = grid_image.shape[:2]
    return h // rows, w // cols


def refine_cell_size_from_lines(grid_image: np.ndarray, rows: int, cols: int) -> tuple[int, int]:
    gray = cv2.cvtColor(grid_image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)

    h_lines = cv2.HoughLinesP(binary, 1, np.pi / 180, threshold=80,
                               minLineLength=grid_image.shape[1] // 3, maxLineGap=10)
    v_lines = cv2.HoughLinesP(binary, 1, np.pi / 180, threshold=80,
                               minLineLength=grid_image.shape[0] // 3, maxLineGap=10)

    def _spacing(lines, axis):
        if lines is None or len(lines) < 2:
            return None
        coords = sorted({int(l[0][axis]) for l in lines if abs(l[0][axis] - l[0][axis + 2]) < 10})
        if len(coords) < 2:
            return None
        return int(np.median([coords[i + 1] - coords[i] for i in range(len(coords) - 1)]))

    return (
        _spacing(h_lines, 1) or (grid_image.shape[0] // rows),
        _spacing(v_lines, 0) or (grid_image.shape[1] // cols),
    )
