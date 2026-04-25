import os
from dataclasses import dataclass, field

import yaml


@dataclass
class Settings:
    model_name: str = "mlx-community/Qwen3-ASR-1.7B-8bit"
    hf_token: str = ""
    host: str = "0.0.0.0"
    port: int = 8000
    allowed_cidrs: list[str] = field(
        default_factory=lambda: ["127.0.0.1/32", "192.168.64.0/24"]
    )
    max_upload_bytes: int = 50 * 1024 * 1024  # 50 MB, -1 = unlimited
    allowed_extensions: set[str] = field(
        default_factory=lambda: {"wav", "mp3", "flac", "m4a", "aac", "ogg", "opus"}
    )


def load_settings(path: str) -> Settings:
    with open(path) as f:
        cfg = yaml.safe_load(f) or {}

    server = cfg.get("server", {})
    model = cfg.get("model", {})
    security = cfg.get("security", {})
    upload = cfg.get("upload", {})

    # 环境变量 HF_TOKEN 优先于 yaml
    hf_token = os.environ.get("HF_TOKEN") or model.get("hf_token", "")

    settings = Settings(
        model_name=model.get("name", Settings.model_name),
        hf_token=hf_token,
        host=server.get("host", Settings.host),
        port=server.get("port", Settings.port),
        allowed_cidrs=security.get("allowed_cidrs", ["127.0.0.1/32", "192.168.64.0/24"]),
        max_upload_bytes=upload.get("max_bytes", 50 * 1024 * 1024),
        allowed_extensions=set(upload.get("allowed_extensions", ["wav", "mp3", "flac", "m4a", "aac", "ogg", "opus"])),
    )
    return settings
