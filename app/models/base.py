from abc import ABC, abstractmethod
from mlx_audio.stt.models.base import STTOutput


class ASRModel(ABC):
    @abstractmethod
    def load(self) -> None:
        """Load model weights into memory. Called once at startup."""
        ...

    @abstractmethod
    def transcribe(self, audio_path: str) -> STTOutput:
        """Run inference on an audio file."""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        ...
