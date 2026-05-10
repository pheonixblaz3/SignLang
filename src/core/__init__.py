"""Core module - configuration, logging, and exceptions."""

from .config import Config
from .logger import get_logger, setup_logging
from .exceptions import (
    ModelLoadError,
    CameraError,
    WebSocketError,
    InferenceError,
)

__all__ = [
    "Config",
    "get_logger",
    "setup_logging",
    "ModelLoadError",
    "CameraError",
    "WebSocketError",
    "InferenceError",
]
