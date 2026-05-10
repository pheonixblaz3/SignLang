"""Extract hand landmarks from raw images using MediaPipe.

This script loads images from `data/raw/images/<label>/`, runs hand detection,
saves the landmarks as .npy files in `data/raw/landmarks/<label>/`, and updates
the manifest CSV with the landmark file paths.

Usage:
    python scripts/extract_landmarks.py --base data/raw
"""
import os
import sys
import csv
import argparse
import numpy as np
from pathlib import Path

# Ensure project root is on sys.path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.detector import HandDetector
from src.capture import WebcamCapture
import cv2


def load_manifest(manifest_path):
    """Load manifest CSV; return list of dicts."""
    if not os.path.exists(manifest_path):
        print(f"Manifest not found: {manifest_path}")
        return []
    rows = []
    with open(manifest_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


def save_manifest(manifest_path, rows):
    """Write manifest CSV."""
    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
    with open(manifest_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["image_file", "landmark_file", "label", "timestamp", "subject_id", "notes"])
        for r in rows:
            writer.writerow([r.get(k, '') for k in ["image_file", "landmark_file", "label", "timestamp", "subject_id", "notes"]])


def extract_landmarks(base='data/raw'):
    """Load images, extract landmarks, save .npy files, update manifest."""
    detector = HandDetector()
    manifest_path = os.path.join(base, 'manifests', 'manifest.csv')
    rows = load_manifest(manifest_path)
    
    updated = 0
    skipped = 0
    
    for row in rows:
        img_path = row.get('image_file')
        lm_path_existing = row.get('landmark_file') or ''
        label = row.get('label')
        
        # Skip if image path is empty
        if not img_path:
            continue
        
        # Skip if landmarks already extracted
        if lm_path_existing and os.path.exists(lm_path_existing):
            print(f"Skipping (landmarks exist): {img_path}")
            skipped += 1
            continue
        
        # Load image and extract landmarks
        if not os.path.exists(img_path):
            print(f"Warning: image not found: {img_path}")
            skipped += 1
            continue
        
        try:
            img = cv2.imread(img_path)
            if img is None:
                print(f"Warning: could not read image: {img_path}")
                skipped += 1
                continue
            
            # Convert BGR to RGB
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            landmarks = detector.detect(img_rgb)
            
            if landmarks is None:
                print(f"No hand detected: {img_path}")
                skipped += 1
                continue
            
            # Save landmark .npy file
            timestamp = row.get('timestamp', 'unknown')
            lm_name = f"{label}_{timestamp}.npy"
            lm_dir = os.path.join(base, 'landmarks', label)
            os.makedirs(lm_dir, exist_ok=True)
            lm_path = os.path.join(lm_dir, lm_name)
            np.save(lm_path, landmarks)
            
            # Update row with landmark path
            row['landmark_file'] = lm_path
            updated += 1
            print(f"Extracted: {img_path} -> {lm_path}")
        
        except Exception as e:
            print(f"Error processing {img_path}: {e}")
            skipped += 1
    
    # Save updated manifest
    save_manifest(manifest_path, rows)
    print(f"\nDone. Updated {updated} rows, skipped {skipped}.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', default='data/raw', help='raw data base directory')
    args = parser.parse_args()
    extract_landmarks(base=args.base)
