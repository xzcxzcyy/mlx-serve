from .base import ASRModel
from .qwen3 import Qwen3ASR


def create_model(model_name: str) -> ASRModel:
    if "qwen3" in model_name.lower():
        return Qwen3ASR(model_name)
    # Future models: add elif branches here
    raise ValueError(f"Unsupported model: {model_name}")
