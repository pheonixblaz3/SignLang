import os
import unittest
from src.capture import WebcamCapture

# Skip these hardware-dependent tests when running in CI or when NO_WEBCAM is set
skip_tests = bool(os.getenv("CI")) or bool(os.getenv("NO_WEBCAM"))


@unittest.skipIf(skip_tests, "Skipping webcam tests in CI or when NO_WEBCAM is set")
class TestWebcamCapture(unittest.TestCase):
    def test_initialization(self):
        capture = WebcamCapture()
        self.assertIsNotNone(capture.cap)
        capture.release()

    def test_get_frame(self):
        capture = WebcamCapture()
        frame = capture.get_frame()
        self.assertIsNotNone(frame)
        capture.release()


if __name__ == '__main__':
    unittest.main()