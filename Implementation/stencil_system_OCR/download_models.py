"""
download_models.py — One-time model download for the OCR pipeline.

Run this ONCE after cloning/pulling the repo:
    python Implementation/OCR/download_models.py

Downloads ~470 MB total to the local HuggingFace cache.
After this, everything runs fully offline — no internet needed.

Models downloaded:
    microsoft/trocr-small-printed     (62M params, ~235 MB) — for rendered/printed grids
    microsoft/trocr-small-handwritten (62M params, ~235 MB) — for handwritten grids
"""

from transformers import TrOCRProcessor, VisionEncoderDecoderModel

MODELS = [
    ("microsoft/trocr-small-printed",     "printed grids (default)"),
    ("microsoft/trocr-small-handwritten", "handwritten grids"),
]

def download(model_id: str, description: str) -> None:
    print(f"\n--- Downloading: {model_id}")
    print(f"    Use case : {description}")
    TrOCRProcessor.from_pretrained(model_id)
    VisionEncoderDecoderModel.from_pretrained(model_id)
    print(f"    Done.")

if __name__ == "__main__":
    print("SecureCameraZoom — TrOCR model setup")
    print("=====================================")
    for model_id, desc in MODELS:
        download(model_id, desc)
    print("\nAll models cached locally.")
    print("Cache location: ~/.cache/huggingface/hub/")
    print("Pipeline is ready for offline use.")
