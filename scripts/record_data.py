import os
import csv
import time
import argparse
import sys
import numpy as np
import cv2

# Ensure project root is on sys.path so `from src...` imports work when running
# scripts directly (e.g., `python scripts/record_data.py`).
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
    """Draw hand joints and connections on image.
    
    Args:
        img: BGR image to draw on (modified in place).
        landmarks: normalized landmarks array of shape (21, 3).
        frame_shape: shape of the original frame (H, W, C).
    """
    h, w = frame_shape[:2]
    
    # Draw connections (bones)
    for start_idx, end_idx in HAND_CONNECTIONS:
        start = landmarks[start_idx]
        end = landmarks[end_idx]
        # Convert from normalized [-1, 1] to pixel coords
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
        # Label each joint
        cv2.putText(img, str(i), (x + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 0), 1)

def ensure_dirs(base):
    os.makedirs(os.path.join(base, "images"), exist_ok=True)
    os.makedirs(os.path.join(base, "landmarks"), exist_ok=True)
    for lbl in LABELS:
        os.makedirs(os.path.join(base, "images", lbl), exist_ok=True)
        os.makedirs(os.path.join(base, "landmarks", lbl), exist_ok=True)

def write_manifest(manifest_path, row):
    new_file = not os.path.exists(manifest_path)
    with open(manifest_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(["image_file", "landmark_file", "label", "timestamp", "subject_id", "notes"])
        writer.writerow(row)


def auto_record_mode(capture, base, subject_id, manifest_path, samples_per_label, detector):
    """Automatically record N samples for each label (A-Z) in sequence."""
    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
    ensure_dirs(base)
    
    print(f"Auto-record mode: recording {samples_per_label} samples per label (A-Z)")
    print("Press 'q' to quit early, 's' to skip current label")
    
    for label in LABELS:
        count = 0
        print(f"\n=== Recording label '{label}' ({count}/{samples_per_label}) ===")
        print("Move your hand in front of the camera. Press 'q' to quit, 's' to skip this label.")
        
        while count < samples_per_label:
            frame = capture.get_frame()
            if frame is None:
                time.sleep(0.1)
                continue
            
            # Show label overlay
            disp = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            cv2.putText(disp, f"Label: {label} ({count}/{samples_per_label})", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
            
            landmarks = None
            if detector is not None:
                landmarks = detector.detect(frame)
                if landmarks is not None:
                    cv2.putText(disp, "Hand detected", (10, 70),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
                    draw_hand_landmarks(disp, landmarks, frame.shape)
            
            cv2.imshow("Auto-Record", disp)
            key = cv2.waitKey(1) & 0xFF
            
            # Auto-record: save frame every ~100ms (adjust as needed)
            if True:  # Always record when in auto mode
                ts = int(time.time() * 1000)
                img_name = f"{label}_{ts}.jpg"
                img_path = os.path.join(base, "images", label, img_name)
                cv2.imwrite(img_path, disp)
                
                if detector is not None and landmarks is not None:
                    lm_name = f"{label}_{ts}.npy"
                    lm_path = os.path.join(base, "landmarks", label, lm_name)
                    np.save(lm_path, landmarks)
                else:
                    lm_path = ""
                
                write_manifest(manifest_path, [img_path, lm_path, label, ts, subject_id, "auto"])
                count += 1
                print(f"  Saved {count}/{samples_per_label}")
                time.sleep(0.1)  # Throttle to avoid excessive writes
            
            if key == ord('q'):
                print("Quitting auto-record mode.")
                capture.release()
                cv2.destroyAllWindows()
                return
            elif key == ord('s'):
                print(f"Skipping label '{label}'.")
                break
    
    print("\nAuto-record complete! All labels recorded.")
    capture.release()
    cv2.destroyAllWindows()



def main(base="data/raw", subject_id="subj_01", video_source=None, no_detect=False, preview_only=False, with_detect=False, auto_record=None, samples_per_label=300):
    # Allow overriding the video source (camera index or video file path)
    try:
        capture = WebcamCapture(video_source)
    except Exception as e:
        print(f"Failed to open video source {video_source}: {e}")
        print("Try passing --video-source 0 (or 1,2...) or a path to a video file.")
        return
    # Instantiate detector lazily only if needed (MediaPipe is heavy)
    detector = None
    if with_detect or (not no_detect and not preview_only and not auto_record):
        try:
            detector = HandDetector()
        except Exception as e:
            print(f"Warning: could not initialize hand detector: {e}")
            print("Falling back to --no-detect mode (images will be saved without landmarks).")
            detector = None
    manifest_path = os.path.join(base, "manifests", "manifest.csv")
    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
    ensure_dirs(base)

    # Auto-record mode: automatically cycle through labels and record N samples per label
    if auto_record:
        auto_record_mode(capture, base, subject_id, manifest_path, samples_per_label, detector)
        return

    current_label = LABELS[0]
    print("Labels:", LABELS)
    print("Press number keys (1..{}) to switch label.".format(len(LABELS)))
    print("Press SPACE or 'r' to record sample. 'q' to quit.")
    print("Use --no-detect to save images without running MediaPipe, or --preview-only to just preview camera frames.")

    try:
        while True:
            frame = capture.get_frame()
            if frame is None:
                print("No frame; retrying...")
                time.sleep(0.1)
                continue

            # Show label overlay
            disp = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            cv2.putText(disp, f"Label: {current_label}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

            landmarks = None
            if detector is not None:
                landmarks = detector.detect(frame)  # normalized numpy array or None
                if landmarks is not None:
                    cv2.putText(disp, "Hand detected", (10, 70),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
                    # Draw hand landmarks and connections on the display
                    draw_hand_landmarks(disp, landmarks, frame.shape)

            cv2.imshow("Recorder", disp)
            key = cv2.waitKey(1) & 0xFF

            # label switch: keys 1..n
            if key in [ord(str(i)) for i in range(1, len(LABELS)+1)]:
                idx = int(chr(key)) - 1
                current_label = LABELS[idx]
                print("Switched label to", current_label)

            # record
            if not preview_only and (key == ord('r') or key == 32):  # 'r' or space
                ts = int(time.time() * 1000)
                img_name = f"{current_label}_{ts}.jpg"
                img_path = os.path.join(base, "images", current_label, img_name)

                # save image as BGR
                cv2.imwrite(img_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

                # If detector active and landmarks found, save them; otherwise leave blank
                if detector is not None and landmarks is not None:
                    lm_name = f"{current_label}_{ts}.npy"
                    lm_path = os.path.join(base, "landmarks", current_label, lm_name)
                    np.save(lm_path, landmarks)
                else:
                    lm_path = ""

                write_manifest(manifest_path, [img_path, lm_path, current_label, ts, subject_id, ""])
                print("Saved image:", img_path, "landmarks:", lm_path or "(none)")

            if key == ord('q'):
                break

    finally:
        capture.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="data/raw", help="dataset base dir")
    parser.add_argument("--subject", default="subj_01", help="subject id")
    parser.add_argument("--video-source", dest="video_source", default=None,
                        help="Camera index (0,1,...) or path to video file")
    parser.add_argument("--no-detect", action='store_true', help="Do not run hand detection; just save images")
    parser.add_argument("--preview-only", action='store_true', help="Only preview camera frames; don't save samples")
    parser.add_argument("--with-detect", action='store_true', help="Enable hand detection and visualization during preview/recording")
    parser.add_argument("--auto-record", action='store_true', help="Automatically record samples for each label (A-Z) in sequence")
    parser.add_argument("--samples-per-label", type=int, default=300, help="Number of samples to record per label in auto-record mode")
    args = parser.parse_args()
    # try converting numeric sources to int
    vs = args.video_source
    if vs is not None:
        try:
            vs_int = int(vs)
            vs = vs_int
        except Exception:
            pass
    main(base=args.base, subject_id=args.subject, video_source=vs, no_detect=args.no_detect, preview_only=args.preview_only, with_detect=args.with_detect, auto_record=args.auto_record, samples_per_label=args.samples_per_label)
