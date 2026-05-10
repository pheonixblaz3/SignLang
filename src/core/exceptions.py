"""Custom exception types for SignSpeak."""


class SignSpeakError(Exception):
    """Base exception for SignSpeak application."""

    pass


class ModelLoadError(SignSpeakError):
    """Raised when model cannot be loaded."""

    pass


class CameraError(SignSpeakError):
    """Raised when camera operations fail."""

    pass


class WebSocketError(SignSpeakError):
    """Raised when WebSocket operations fail."""

    pass


class InferenceError(SignSpeakError):
    """Raised when inference pipeline fails."""

    pass
