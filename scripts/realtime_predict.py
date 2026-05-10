"""Realtime webcam predictor — shows a preview window with model predictions.

Usage:
    python scripts/realtime_predict.py --model models/landmark_mlp_recorded.joblib --camera 0

This script reads frames from the webcam, runs the project's HandDetector,
predicts with the trained model if available, and displays the annotated
preview. Press 'q' to quit.
"""
import os
import sys
import argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import joblib
import numpy as np
import cv2

from src.capture import WebcamCapture
from src.detector import HandDetector


def load_model(path):
    if not os.path.exists(path):
        print(f"Model path not found: {path}")
        return None, None
    obj = joblib.load(path)
    if isinstance(obj, dict):
        model = obj.get('model') or obj.get('clf')
        le = obj.get('label_encoder') or obj.get('le')
    else:
        model = obj
        le = None
    return model, le


def main(model_path, camera_index):
    cap = WebcamCapture(video_source=camera_index)
    det = HandDetector()
    model, le = load_model(model_path)

    try:
        while True:
            frame = cap.get_frame()
            if frame is None:
                continue
            disp = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            landmarks = det.detect(frame)
            if landmarks is not None:
                # draw landmarks as small circles
                h, w = disp.shape[:2]
                for (x, y, z) in landmarks:
                    # Map normalized MediaPipe coords to pixel coordinates
                    try:
                        cx = int(max(0, min(w - 1, x * w)))
                        cy = int(max(0, min(h - 1, y * h)))
                        cv2.circle(disp, (cx, cy), 3, (0, 255, 0), -1)
                    except Exception:
                        continue

                if model is not None:
                    arr = np.asarray(landmarks)
                    if arr.ndim == 2:
                        x = arr.flatten().reshape(1, -1)
                    else:
                        x = arr.reshape(1, -1)
                    try:
                        pred_idx = model.predict(x)
                        pred = le.inverse_transform(pred_idx)[0] if le is not None else pred_idx[0]
                        cv2.putText(disp, f"Pred: {pred}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
                    except Exception:
                        pass

            cv2.imshow('realtime_predict', disp)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default=os.path.join('models', 'landmark_mlp_recorded.joblib'))
    parser.add_argument('--camera', type=int, default=0)
    args = parser.parse_args()
    main(args.model, args.camera)
