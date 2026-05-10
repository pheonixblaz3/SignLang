import cv2
from config.settings import CAMERA_INDEX


class WebcamCapture:
    """Wrapper around cv2.VideoCapture.

    Accepts either an integer camera index or a string path to a video file.
    If `video_source` is None, uses the default CAMERA_INDEX from settings.
    """
    def __init__(self, video_source=None):
        if video_source is None:
            video_source = CAMERA_INDEX
        self.cap = cv2.VideoCapture(video_source)
        if not self.cap.isOpened():
            raise ValueError(f"Could not open video source: {video_source}")

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def release(self):
        try:
            self.cap.release()
        except Exception:
            pass