"""Sign language classifier using trained ML model."""

from typing import Optional, List, Tuple
import numpy as np
from src.core.logger import get_logger
from src.core.exceptions import InferenceError
from src.services.model_loader import ModelLoader

logger = get_logger(__name__)


class SignClassifier:
    """Classify hand landmarks into sign language letters using ML model."""

    def __init__(self, model_loader: Optional[ModelLoader] = None):
        """
        Initialize sign classifier.

        Args:
            model_loader: Optional ModelLoader instance. If None, will be created.
        """
        self.model_loader = model_loader
        self.classes = []

        if self.model_loader:
            self.classes = self.model_loader.get_classes()
            logger.info(f"Classifier initialized with {len(self.classes)} classes")

    def set_model_loader(self, model_loader: ModelLoader) -> None:
        """Set the model loader."""
        self.model_loader = model_loader
        self.classes = self.model_loader.get_classes()
        logger.info(f"Model loader set. Classes: {len(self.classes)}")

    def classify(self, landmarks: np.ndarray) -> Optional[str]:
        """
        Classify landmarks into a sign letter.

        Args:
            landmarks: Normalized landmarks (21 x 3 array or flattened 63-dim vector)

        Returns:
            Predicted letter or None if classification fails
        """
        if self.model_loader is None or self.model_loader.model is None:
            logger.error("Model not loaded")
            return None

        try:
            # Validate input
            if landmarks is None:
                return None

            # Flatten if needed (21 x 3 -> 63)
            if isinstance(landmarks, np.ndarray):
                if landmarks.ndim == 2:
                    landmarks = landmarks.flatten()
            else:
                landmarks = np.array(landmarks).flatten()

            # Make prediction
            result = self.model_loader.predict(landmarks)
            return result["prediction"]

        except Exception as e:
            logger.error(f"Classification error: {e}")
            return None

    def classify_with_confidence(self, landmarks: np.ndarray) -> Tuple[Optional[str], float]:
        """
        Classify landmarks with confidence score.

        Args:
            landmarks: Normalized landmarks

        Returns:
            Tuple of (predicted_letter, confidence)
        """
        if self.model_loader is None or self.model_loader.model is None:
            return None, 0.0

        try:
            if landmarks is None:
                return None, 0.0

            if isinstance(landmarks, np.ndarray):
                if landmarks.ndim == 2:
                    landmarks = landmarks.flatten()
            else:
                landmarks = np.array(landmarks).flatten()

            result = self.model_loader.predict(landmarks)
            return result["prediction"], result["confidence"]

        except Exception as e:
            logger.error(f"Classification with confidence error: {e}")
            return None, 0.0

    def get_top_predictions(
        self, landmarks: np.ndarray, k: int = 3
    ) -> List[Tuple[str, float]]:
        """
        Get top K predictions.

        Args:
            landmarks: Normalized landmarks
            k: Number of top predictions

        Returns:
            List of (letter, confidence) tuples
        """
        if self.model_loader is None or self.model_loader.model is None:
            return []

        try:
            if landmarks is None:
                return []

            if isinstance(landmarks, np.ndarray):
                if landmarks.ndim == 2:
                    landmarks = landmarks.flatten()
            else:
                landmarks = np.array(landmarks).flatten()

            result = self.model_loader.predict(landmarks)
            return result.get("top_3", [])[:k]

        except Exception as e:
            logger.error(f"Get top predictions error: {e}")
            return []

    def get_classes(self) -> List[str]:
        """Get list of supported classes."""
        if self.model_loader:
            return self.model_loader.get_classes()
        return []