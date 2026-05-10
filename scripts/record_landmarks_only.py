"""Record ONLY hand landmarks (coordinates) - no images.

Records hand landmarks (21 keypoints x 3 coords per keypoint) directly to .npy files.
Press spacebar to save the current hand landmarks. Landmarks are saved immediately
and can be used directly for training without extraction.

Usage:
    python scripts/record_landmarks_only.py --video-source 0 --base data/landmarks_only --subject subj_you

Controls:
    - Number keys 1..26: switch label (A-Z)
    - Space: save current hand landmarks
    - q: quit
"""
import os
import sys
import csv
import time
import argparse
import numpy as np
import cv2

# Ensure project root is on sys.path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.capture import WebcamCapture
from src.detector import HandDetector

# Default labels: A-Z (all 26 letters)
LABELS = [chr(ord('A') + i) for i in range(26)]  # ['A', 'B', ..., 'Z']

# Hand landmark connections (MediaPipe hand model)
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),  # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),  # Index
    (0, 9), (9, 10), (10, 11), (11, 12),  # Middle
    (0, 13), (13, 14), (14, 15), (15, 16),  # Ring
    (0, 17), (17, 18), (18, 19), (19, 20),  # Pinky
]

def draw_hand_landmarks(img, landmarks, frame_shape):
    """Draw hand joints and connections on image."""
    h, w = frame_shape[:2]
    
    # Draw connections (bones)
    for start_idx, end_idx in HAND_CONNECTIONS:
        start = landmarks[start_idx]
        end = landmarks[end_idx]
        x1 = int((start[0] + 1) * w / 2)
        y1 = int((start[1] + 1) * h / 2)
        x2 = int((end[0] + 1) * w / 2)
        y2 = int((end[1] + 1) * h / 2)
        cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    
    # Draw joints (keypoints)
    for i, landmark in enumerate(landmarks):
        x = int((landmark[0] + 1) * w / 2)
        y = int((landmark[1] + 1) * h / 2)
        cv2.circle(img, (x, y), 5, (0, 0, 255), -1)
        cv2.putText(img, str(i), (x + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 0), 1)

def ensure_dirs(base):
    os.makedirs(os.path.join(base, "landmarks"), exist_ok=True)
    for lbl in LABELS:
        os.makedirs(os.path.join(base, "landmarks", lbl), exist_ok=True)

def write_manifest(manifest_path, row):
    new_file = not os.path.exists(manifest_path)
    with open(manifest_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(["landmark_file", "label", "timestamp", "subject_id", "notes"])
        writer.writerow(row)

def main(base="data/landmarks_only", subject_id="subj_01", video_source=None):
    """Record landmarks only (no images) - save on spacebar press."""
    try:
        capture = WebcamCapture(video_source)
    except Exception as e:
        print(f"Failed to open video source {video_source}: {e}")
        print("Try passing --video-source 0 (or 1,2...) or a path to a video file.")
        return
    
    try:
        detector = HandDetector()
    except Exception as e:
        print(f"Failed to initialize hand detector: {e}")
        print("Make sure MediaPipe is installed.")
        capture.release()
        return
    
    manifest_path = os.path.join(base, "manifests", "manifest.csv")
    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
    ensure_dirs(base)
    
    current_label = LABELS[0]
    sample_count = {lbl: 0 for lbl in LABELS}
    
    print("=== LANDMARKS ONLY RECORDER ===")
    print("Records ONLY hand coordinates (no images)")
    print("Labels:", LABELS)
    print("Press number keys (1..26) to switch label.")
    print("Press SPACE to save current hand landmarks.")
    print("Press 'q' to quit.")
    print()
    
    try:
        while True:
            frame = capture.get_frame()
            if frame is None:
                print("No frame; retrying...")
                time.sleep(0.1)
                continue
            
            # Show label overlay
            disp = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            cv2.putText(disp, f"Label: {current_label} (count: {sample_count[current_label]})", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
            
            landmarks = detector.detect(frame)
            
            if landmarks is not None:
                cv2.putText(disp, "Hand detected - Press SPACE to save", (10, 70),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                draw_hand_landmarks(disp, landmarks, frame.shape)
            else:
                cv2.putText(disp, "No hand detected", (10, 70),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
            cv2.imshow("Landmarks Recorder", disp)
            key = cv2.waitKey(1) & 0xFF
            
            # Label switch: keys 1..26 (or A..Z directly)
            if key >= ord('1') and key <= ord('9'):
                idx = int(chr(key)) - 1
                if idx < len(LABELS):
                    current_label = LABELS[idx]
                    print(f"Switched to label: {current_label}")
            elif key >= ord('A') and key <= ord('Z'):
                current_label = chr(key)
                print(f"Switched to label: {current_label}")
            elif key >= ord('a') and key <= ord('z'):
                current_label = chr(key).upper()
                print(f"Switched to label: {current_label}")
            
            # Save on spacebar
            if key == 32:  # spacebar
                if landmarks is None:
                    print("No hand detected; sample skipped.")
                    continue
                
                ts = int(time.time() * 1000)
                lm_name = f"{current_label}_{ts}.npy"
                lm_path = os.path.join(base, "landmarks", current_label, lm_name)
                
                # Save landmarks as .npy file
                np.save(lm_path, landmarks)
                sample_count[current_label] += 1
                
                write_manifest(manifest_path, [lm_path, current_label, ts, subject_id, ""])
                print(f"[SAVED] {current_label}: {sample_count[current_label]} samples - {lm_path}")
            
            if key == ord('q'):
                break
    
    finally:
        capture.release()
        cv2.destroyAllWindows()
        
        # Print final summary
        print("\n=== RECORDING COMPLETE ===")
        total = sum(sample_count.values())
        print(f"Total samples recorded: {total}")
        for lbl in LABELS:
            if sample_count[lbl] > 0:
                print(f"  {lbl}: {sample_count[lbl]} samples")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Record ONLY hand landmarks (coordinates) - no images")
    parser.add_argument("--video-source", dest="video_source", default=None,
                        help="Camera index (0,1,...) or path to video file")
    parser.add_argument("--base", default="data/landmarks_only", help="output base directory")
    parser.add_argument("--subject", default="subj_01", help="subject id")
    args = parser.parse_args()
    
    # Try converting numeric sources to int
    vs = args.video_source
    if vs is not None:
        try:
            vs = int(vs)
        except Exception:
            pass
    
    main(base=args.base, subject_id=args.subject, video_source=vs)
