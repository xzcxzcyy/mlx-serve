import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .config import Settings
from .middleware import AccessLogMiddleware, IPAllowListMiddleware
from .models import create_model
from .routes import router

logger = logging.getLogger("mlx-serve")


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info(f"Loading model: {settings.model_name}")
        model = create_model(settings.model_name)
        model.load()
        logger.info("Model loaded")

        app.state.asr_model = model
        app.state.settings = settings
        app.state.inference_lock = asyncio.Lock()
        yield

    app = FastAPI(title="mlx-serve", lifespan=lifespan)
    app.add_middleware(IPAllowListMiddleware, allowed_cidrs=settings.allowed_cidrs)
    app.add_middleware(AccessLogMiddleware)
    app.include_router(router)
    return app
