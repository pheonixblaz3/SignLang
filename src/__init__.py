"""Top-level package for sign-decoder.

IMPORTANT: avoid importing heavy submodules (like `detector` which depends on
MediaPipe/TensorFlow) at package import time. Import submodules directly where
needed (for example `from src.detector import HandDetector`).
"""

# Intentionally do not import submodules here to keep `import src` cheap.
__all__ = [
	# Consumers should import the classes directly from their modules, e.g.
	# `from src.capture import WebcamCapture`
]
