"""Centralized configuration management."""

import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class Config:
    """Configuration object for SignSpeak application."""

    # Camera settings
    CAMERA_INDEX: int = int(os.getenv("CAMERA_INDEX", "0"))
    MAX_HANDS: int = int(os.getenv("MAX_HANDS", "1"))
    DETECTION_CONFIDENCE: float = float(os.getenv("DETECTION_CONFIDENCE", "0.7"))
    TRACKING_CONFIDENCE: float = float(os.getenv("TRACKING_CONFIDENCE", "0.5"))

    # Inference pipeline settings
    FRAME_BUFFER_SIZE: int = int(os.getenv("FRAME_BUFFER_SIZE", "5"))
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.4"))
    LETTER_HOLD_FRAMES: int = int(os.getenv("LETTER_HOLD_FRAMES", "3"))
    LETTER_COOLDOWN_MS: int = int(os.getenv("LETTER_COOLDOWN_MS", "200"))

    # Model settings
    MODEL_PATH: str = os.getenv("MODEL_PATH", "models/landmark_mlp_recorded.joblib")
    GPU_ENABLED: bool = os.getenv("GPU_ENABLED", "true").lower() == "true"

    # Logging settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/signspeak.log")

    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    RELOAD: bool = os.getenv("RELOAD", "false").lower() == "true"

    # Frame processing
    FRAME_RATE: float = float(os.getenv("FRAME_RATE", "0.1"))  # Seconds between frames

    @classmethod
    def from_env(cls) -> "Config":
        """Create config instance from environment variables."""
        return cls()

    def __str__(self) -> str:
        """String representation of configuration."""
        lines = ["SignSpeak Configuration:", "-" * 40]
        for key, value in self.__dict__.items():
            if not key.startswith("_"):
                lines.append(f"  {key}: {value}")
        return "\n".join(lines)
