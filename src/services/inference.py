"""Advanced inference pipeline with smoothing and debouncing."""

from collections import deque
from typing import Dict, List, Optional, Tuple
import time
import numpy as np
from src.core.logger import get_logger

logger = get_logger(__name__)


class InferencePipeline:
    """
    Advanced prediction pipeline with:
    - Frame buffering and aggregation
    - Confidence threshold filtering
    - Letter hold timer for stability
    - Duplicate suppression with cooldown
    - Top-3 prediction tracking
    """

    def __init__(
        self,
        frame_buffer_size: int = 5,
        confidence_threshold: float = 0.4,
        letter_hold_frames: int = 3,
        letter_cooldown_ms: int = 200,
    ):
        """
        Initialize inference pipeline.

        Args:
            frame_buffer_size: Number of frames to aggregate
            confidence_threshold: Minimum confidence to accept prediction
            letter_hold_frames: Frames prediction must remain stable
            letter_cooldown_ms: Milliseconds between duplicate letters
        """
        self.frame_buffer_size = frame_buffer_size
        self.confidence_threshold = confidence_threshold
        self.letter_hold_frames = letter_hold_frames
        self.letter_cooldown_ms = letter_cooldown_ms

        # Frame history buffer
        self.prediction_buffer: deque = deque(maxlen=frame_buffer_size)
        self.confidence_buffer: deque = deque(maxlen=frame_buffer_size)

        # Letter hold tracking
        self.current_letter: Optional[str] = None
        self.letter_hold_count: int = 0

        # Duplicate suppression
        self.last_letter: Optional[str] = None
        self.last_letter_time: float = 0.0

        # Performance metrics
        self.frame_count: int = 0
        self.inference_times: deque = deque(maxlen=100)

    def process(
        self,
        prediction: str,
        confidence: float,
        inference_time_ms: float,
        top_3_predictions: Optional[List[Tuple[str, float]]] = None,
    ) -> Dict:
        """
        Process prediction through pipeline.

        Args:
            prediction: Predicted letter
            confidence: Confidence score (0-1)
            inference_time_ms: Time taken for inference
            top_3_predictions: Top 3 predictions with confidences

        Returns:
            Dict with:
                - letter: Final predicted letter (or None if not ready)
                - confidence: Confidence of letter
                - top_3: Top 3 predictions
                - state: Current pipeline state
                - fps: Frames per second
        """
        self.frame_count += 1
        self.inference_times.append(inference_time_ms)

        # Store in buffers
        self.prediction_buffer.append(prediction)
        self.confidence_buffer.append(confidence)

        # Calculate aggregated prediction
        aggregated = self._aggregate_predictions()
        aggregated_letter = aggregated["letter"]
        aggregated_confidence = aggregated["confidence"]

        # Apply confidence threshold
        if aggregated_confidence < self.confidence_threshold:
            self.current_letter = None
            self.letter_hold_count = 0
            return {
                "letter": None,
                "confidence": 0.0,
                "top_3": top_3_predictions or [],
                "state": "low_confidence",
                "fps": self._calculate_fps(),
            }

        # Check if letter is changing
        if aggregated_letter != self.current_letter:
            self.current_letter = aggregated_letter
            self.letter_hold_count = 1
            return {
                "letter": None,
                "confidence": 0.0,
                "top_3": top_3_predictions or [],
                "state": "letter_changing",
                "fps": self._calculate_fps(),
            }

        # Increment hold count
        self.letter_hold_count += 1

        # Check if hold time is satisfied
        if self.letter_hold_count < self.letter_hold_frames:
            return {
                "letter": None,
                "confidence": 0.0,
                "top_3": top_3_predictions or [],
                "state": f"holding ({self.letter_hold_count}/{self.letter_hold_frames})",
                "fps": self._calculate_fps(),
            }

        # Letter is ready - check cooldown
        current_time = time.time() * 1000  # milliseconds
        time_since_last = current_time - self.last_letter_time

        if self.last_letter == aggregated_letter and time_since_last < self.letter_cooldown_ms:
            return {
                "letter": None,
                "confidence": 0.0,
                "top_3": top_3_predictions or [],
                "state": f"cooldown ({int(self.letter_cooldown_ms - time_since_last)}ms)",
                "fps": self._calculate_fps(),
            }

        # Accept letter
        self.last_letter = aggregated_letter
        self.last_letter_time = current_time

        logger.debug(
            f"Accepted letter '{aggregated_letter}' with confidence {aggregated_confidence:.2f}"
        )

        return {
            "letter": aggregated_letter,
            "confidence": aggregated_confidence,
            "top_3": top_3_predictions or [],
            "state": "accepted",
            "fps": self._calculate_fps(),
        }

    def _aggregate_predictions(self) -> Dict:
        """Aggregate predictions from buffer."""
        if not self.prediction_buffer:
            return {"letter": None, "confidence": 0.0}

        # Most common prediction
        predictions = list(self.prediction_buffer)
        confidence_scores = list(self.confidence_buffer)

        # Vote on most common letter
        from collections import Counter

        letter_counts = Counter(predictions)
        most_common_letter = letter_counts.most_common(1)[0][0]

        # Average confidence for that letter
        indices = [i for i, p in enumerate(predictions) if p == most_common_letter]
        avg_confidence = np.mean([confidence_scores[i] for i in indices])

        return {"letter": most_common_letter, "confidence": float(avg_confidence)}

    def _calculate_fps(self) -> float:
        """Calculate frames per second."""
        if not self.inference_times or len(self.inference_times) < 2:
            return 0.0
        avg_time_ms = np.mean(list(self.inference_times))
        if avg_time_ms == 0:
            return 0.0
        return 1000.0 / avg_time_ms

    def reset(self) -> None:
        """Reset pipeline state."""
        self.prediction_buffer.clear()
        self.confidence_buffer.clear()
        self.current_letter = None
        self.letter_hold_count = 0
        self.last_letter = None
        self.last_letter_time = 0.0
        logger.debug("Inference pipeline reset")

    def get_stats(self) -> Dict:
        """Get current pipeline statistics."""
        return {
            "frame_count": self.frame_count,
            "buffer_size": len(self.prediction_buffer),
            "current_letter": self.current_letter,
            "hold_count": self.letter_hold_count,
            "avg_inference_ms": float(np.mean(list(self.inference_times)))
            if self.inference_times
            else 0.0,
            "fps": self._calculate_fps(),
        }
