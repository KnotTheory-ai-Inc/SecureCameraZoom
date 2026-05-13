import io
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import torch

_PRINTED_MODEL_ID = "microsoft/trocr-small-printed"
_HANDWRITTEN_MODEL_ID = "microsoft/trocr-small-handwritten"

_VALID_CHARS = {chr(v % 95 + 32) for v in range(95)}


class SecureVisionOCR:
    def __init__(self, mode: str = "printed"):
        model_id = _PRINTED_MODEL_ID if mode == "printed" else _HANDWRITTEN_MODEL_ID
        self.processor = TrOCRProcessor.from_pretrained(model_id, local_files_only=True)
        self.model = VisionEncoderDecoderModel.from_pretrained(model_id, local_files_only=True)
        self.model.eval()
        self.model.to("cpu")

    def _run(self, pil_image: Image.Image) -> str:
        if pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")
        pixel_values = self.processor(images=pil_image, return_tensors="pt").pixel_values
        with torch.no_grad():
            generated_ids = self.model.generate(pixel_values)
        return self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()

    def extract_text_from_image(self, image_path: str) -> str:
        return self._run(Image.open(image_path))

    def extract_text_from_bytes(self, image_bytes: bytes) -> str:
        return self._run(Image.open(io.BytesIO(image_bytes)))

    def ocr_single_cell(self, cell_bytes: bytes) -> str:
        text = self.extract_text_from_bytes(cell_bytes)
        for ch in text:
            if ch in _VALID_CHARS:
                return ch
        return ""

    def ocr_grid_region(self, image_bytes: bytes, rows: int, cols: int) -> list[list[str]]:
        flat = self.extract_text_from_bytes(image_bytes)
        flat = flat.replace("\n", "").replace(" ", "")
        flat = flat.ljust(rows * cols, "?")[: rows * cols]
        return [list(flat[r * cols: (r + 1) * cols]) for r in range(rows)]
