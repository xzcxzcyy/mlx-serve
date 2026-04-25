from pydantic import BaseModel


class Segment(BaseModel):
    text: str
    start: float
    end: float
    language: str | None = None


class TranscriptionResponse(BaseModel):
    text: str
    segments: list[Segment] | None = None
    language: str | None = None
    processing_time: float
