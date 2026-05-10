import numpy as np
def normalize_landmarks(landmarks):
    """Normalize hand landmarks for consistent processing (e.g., scale to 0-1)."""
    if not landmarks:
        return None
    # Example: Center and scale based on wrist (landmark 0)
    wrist = np.array([landmarks[0].x, landmarks[0].y, landmarks[0].z])
    normalized = []
    for lm in landmarks:
        point = np.array([lm.x, lm.y, lm.z]) - wrist
        normalized.append(point)
    return np.array(normalized)
def calculate_distance(lm1, lm2):
    """Calculate Euclidean distance between two landmarks."""
    return np.linalg.norm(np.array([lm1.x - lm2.x, lm1.y - lm2.y, lm1.z - lm2.z]))