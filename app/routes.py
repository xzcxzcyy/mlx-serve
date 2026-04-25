import asyncio
import logging
import os
import tempfile

from fastapi import APIRouter, File, HTTPException, Query, Request, UploadFile

from .schemas import Segment, TranscriptionResponse

logger = logging.getLogger("mlx-serve")

router = APIRouter()


@router.get("/health")
async def health(request: Request):
    return {"status": "ok", "model": request.app.state.asr_model.name}


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe(
    request: Request,
    file: UploadFile = File(...),
    include_segments: bool = Query(False),
):
    settings = request.app.state.settings

    # Validate extension
    ext = (file.filename or "").rsplit(".", 1)[-1].lower()
    if ext not in settings.allowed_extensions:
        raise HTTPException(400, f"Unsupported format: .{ext}")

    # Read file and check size
    data = await file.read()
    if not data:
        raise HTTPException(400, "Empty file")
    if settings.max_upload_bytes >= 0 and len(data) > settings.max_upload_bytes:
        raise HTTPException(413, "File too large")

    logger.info("Received %d bytes from %s", len(data), request.client and request.client.host)

    # Write to temp file
    tmp = tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False)
    try:
        tmp.write(data)
        tmp.close()

        # Serialize inference (MLX is not thread-safe)
        async with request.app.state.inference_lock:
            result = await asyncio.to_thread(
                request.app.state.asr_model.transcribe, tmp.name
            )

        logger.info("Transcribed in %.2fs, include_segments=%s", result.total_time, include_segments)

        segments = [
            Segment(
                text=s["text"],
                start=s["start"],
                end=s["end"],
                language=s.get("language"),
            )
            for s in (result.segments or [])
        ] if include_segments else None

        language = result.language
        if isinstance(language, list):
            language = language[0] if language else None

        return TranscriptionResponse(
            text=result.text,
            segments=segments,
            language=language,
            processing_time=result.total_time,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Inference failed: %s", e, exc_info=True)
        raise HTTPException(500, f"Inference failed: {e}")
    finally:
        os.unlink(tmp.name)
