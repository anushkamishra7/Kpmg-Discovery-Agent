"""
CLIP embedder for text and image inputs.
Produces 512-dim L2-normalized vectors compatible with Pinecone cosine search.
"""
from functools import lru_cache
from io import BytesIO
from pathlib import Path
from typing import Union

import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

MODEL_ID = "openai/clip-vit-base-patch32"
EMBED_DIM = 512


@lru_cache(maxsize=1)
def _load_model():
    """Load CLIP once and cache. First call downloads ~600MB from HuggingFace."""
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    model = CLIPModel.from_pretrained(MODEL_ID).to(device)
    model.eval()
    processor = CLIPProcessor.from_pretrained(MODEL_ID)
    return model, processor, device


def _to_tensor(features) -> torch.Tensor:
    """Unwrap newer transformers return types into a raw tensor."""
    if isinstance(features, torch.Tensor):
        return features
    if getattr(features, "pooler_output", None) is not None:
        return features.pooler_output
    if getattr(features, "last_hidden_state", None) is not None:
        return features.last_hidden_state[:, 0]
    raise TypeError(f"Cannot extract tensor from features of type {type(features)}")


def _normalize(features) -> list[float]:
    """L2-normalize and convert to a plain list of floats for Pinecone."""
    vec = _to_tensor(features)
    vec = vec / vec.norm(dim=-1, keepdim=True)
    return vec.squeeze(0).cpu().tolist()


def embed_text(text: str) -> list[float]:
    """Embed a text string into a 512-dim normalized vector."""
    model, processor, device = _load_model()
    inputs = processor(
        text=[text], return_tensors="pt", padding=True, truncation=True
    ).to(device)
    with torch.no_grad():
        features = model.get_text_features(**inputs)
    return _normalize(features)


def embed_image(image_input: Union[str, bytes, Path, Image.Image]) -> list[float]:
    """
    Embed an image into a 512-dim normalized vector.
    Accepts a file path, raw bytes, Path, or PIL Image object.
    """
    if isinstance(image_input, (str, Path)):
        image = Image.open(image_input).convert("RGB")
    elif isinstance(image_input, bytes):
        image = Image.open(BytesIO(image_input)).convert("RGB")
    elif isinstance(image_input, Image.Image):
        image = image_input.convert("RGB")
    else:
        raise TypeError(f"Unsupported image input type: {type(image_input)}")

    model, processor, device = _load_model()
    inputs = processor(images=image, return_tensors="pt").to(device)
    with torch.no_grad():
        features = model.get_image_features(**inputs)
    return _normalize(features)