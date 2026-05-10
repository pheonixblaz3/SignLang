from config.settings import MAX_HANDS, DETECTION_CONFIDENCE, TRACKING_CONFIDENCE
from .utils.helpers import normalize_landmarks


class HandDetector:
    """Hand detector using MediaPipe.

    Mediapipe is imported lazily in __init__ so importing this module doesn't
    immediately import TensorFlow/JAX-heavy dependencies.
    """
    def __init__(self, max_num_hands=None, detection_confidence=None, tracking_confidence=None):
        # Import mediapipe lazily to avoid heavy imports during top-level package import
        import mediapipe as mp  # type: ignore

        self._mp = mp
        self.mp_hands = self._mp.solutions.hands # type: ignore
        self.hands = self.mp_hands.Hands(
            max_num_hands=max_num_hands or MAX_HANDS,
            min_detection_confidence=detection_confidence or DETECTION_CONFIDENCE,
            min_tracking_confidence=tracking_confidence or TRACKING_CONFIDENCE,
        )
        self.mp_draw = self._mp.solutions.drawing_utils # type: ignore

    def detect(self, frame):
        results = self.hands.process(frame)
        if results.multi_hand_landmarks:
            landmarks = results.multi_hand_landmarks[0].landmark
            return normalize_landmarks(landmarks)  # Use utility for normalization
        return None

    def draw_landmarks(self, frame, landmarks):
        if landmarks:
            # Convert back to MediaPipe format if needed for drawing
            self.mp_draw.draw_landmarks(frame, landmarks, self.mp_hands.HAND_CONNECTIONS)
        return frame