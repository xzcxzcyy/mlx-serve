from mlx_audio.stt.models.base import STTOutput
from mlx_audio.stt.utils import load_model

from .base import ASRModel


class Qwen3ASR(ASRModel):
    def __init__(self, model_name: str):
        self._model_name = model_name
        self._model = None

    def load(self) -> None:
        self._model = load_model(self._model_name)

    def transcribe(self, audio_path: str) -> STTOutput:
        return self._model.generate(audio_path)

    @property
    def name(self) -> str:
        return self._model_name
