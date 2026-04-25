import argparse
import logging
import os

import uvicorn

from app.config import Settings, load_settings
from app.main import create_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def main():
    parser = argparse.ArgumentParser(description="mlx-serve ASR server")
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to YAML config file (default: %(default)s)",
    )
    parser.add_argument("--model", help="Override model name from config")
    parser.add_argument("--host", help="Override bind host from config")
    parser.add_argument("--port", type=int, help="Override bind port from config")
    args = parser.parse_args()

    settings = load_settings(args.config)

    if args.model:
        settings.model_name = args.model
    if args.host:
        settings.host = args.host
    if args.port:
        settings.port = args.port

    if settings.hf_token:
        os.environ["HF_TOKEN"] = settings.hf_token

    app = create_app(settings)
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
