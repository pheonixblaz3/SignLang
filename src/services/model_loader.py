"""Model loading and health check utilities."""

import os
import time
from typing import Dict, Optional, Any
import joblib
import torch
from src.core.logger import get_logger
from src.core.exceptions import ModelLoadError

logger = get_logger(__name__)


class ModelLoader:
    """Load and manage ML models with health checks."""

    def __init__(self, model_path: str, gpu_enabled: bool = True):
        """
        Initialize model loader.

        Args:
            model_path: Path to model file
            gpu_enabled: Whether to use GPU if available
        """
        self.model_path = model_path
        self.gpu_enabled = gpu_enabled
        self.model: Optional[Any] = None
        self.label_encoder: Optional[Any] = None
        self.load_time: float = 0.0
        self.device: str = self._detect_device()

    def _detect_device(self) -> str:
        """Detect available device (GPU or CPU)."""
        if not self.gpu_enabled:
            logger.info("GPU disabled via config")
            return "cpu"

        if torch.cuda.is_available():
            device = f"cuda:{torch.cuda.current_device()}"
            gpu_name = torch.cuda.get_device_name(0)
            logger.info(f"GPU detected: {gpu_name}")
            return device
        else:
            logger.info("GPU not available, using CPU")
            return "cpu"

    def load(self) -> bool:
        """
        Load model from disk.

        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(self.model_path):
            raise ModelLoadError(f"Model file not found: {self.model_path}")

        try:
            start_time = time.time()
            logger.info(f"Loading model from {self.model_path}...")

            # Load joblib model
            loaded_data = joblib.load(self.model_path)

            # Handle different formats
            if isinstance(loaded_data, dict) and "model" in loaded_data:
                self.model = loaded_data["model"]
                self.label_encoder = loaded_data.get("label_encoder", None)
            else:
                self.model = loaded_data

            self.load_time = time.time() - start_time
            logger.info(f"Model loaded successfully in {self.load_time:.2f}s")
            return True

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise ModelLoadError(f"Model loading failed: {e}")

    def predict(self, landmarks: Any) -> Dict:
        """
        Make prediction with model.

        Args:
            landmarks: Input landmarks (should be flattened)

        Returns:
            Dict with prediction and probabilities
        """
        if self.model is None:
            raise ModelLoadError("Model not loaded")

        try:
            # Ensure input is 2D (batch_size, features)
            if len(landmarks.shape) == 1:
                landmarks = landmarks.reshape(1, -1)

            # Get prediction and probabilities
            prediction = self.model.predict(landmarks)[0]
            probabilities = self.model.predict_proba(landmarks)[0]

            # Get top 3 predictions
            top_3_indices = sorted(range(len(probabilities)), key=lambda i: probabilities[i], reverse=True)[:3]
            top_3 = []

            if self.label_encoder:
                for idx in top_3_indices:
                    label = self.label_encoder.inverse_transform([idx])[0]
                    top_3.append((label, float(probabilities[idx])))
            else:
                for idx in top_3_indices:
                    top_3.append((chr(ord("A") + idx), float(probabilities[idx])))

            return {
                "prediction": prediction,
                "confidence": float(max(probabilities)),
                "top_3": top_3,
            }

        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise

    def get_classes(self) -> list:
        """Get list of model classes."""
        if self.label_encoder:
            return list(self.label_encoder.classes_)
        elif hasattr(self.model, "classes_"):
            return list(self.model.classes_)
        else:
            # Default A-Z
            return [chr(ord("A") + i) for i in range(26)]

    def get_health_status(self) -> Dict:
        """Get model health status."""
        return {
            "loaded": self.model is not None,
            "model_path": self.model_path,
            "device": self.device,
            "load_time_seconds": self.load_time,
            "num_classes": len(self.get_classes()) if self.model else 0,
            "model_type": self.model.__class__.__name__ if self.model else None,
        }

    def get_model_info(self) -> Dict:
        """Get detailed model information."""
        classes = self.get_classes()
        return {
            "type": "joblib" if isinstance(self.model, object) else "unknown",
            "classes": len(classes),
            "class_labels": classes[:10],  # First 10 for brevity
            "device": self.device,
            "load_time_ms": int(self.load_time * 1000),
        }
