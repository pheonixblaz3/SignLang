"""Process raw collected data into numpy arrays for training.

Reads `data/raw/manifests/manifest.csv`, loads landmark .npy files, applies
simple augmentations (flip, jitter), and writes train/val/test splits to
`data/processed` as .npy files.

Usage:
    python scripts/process_data.py --base data/raw --out data/processed
"""
import os
import csv
import argparse
import sys
import numpy as np
from collections import defaultdict
import random

# Allow running this script directly from the repo root (so imports of local
# packages in tests and scripts work). Insert project root into sys.path.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def load_manifest(manifest_path):
    if not os.path.exists(manifest_path):
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")
    rows = []
    with open(manifest_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


def load_landmark(path):
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    return np.load(path)


def augment_landmarks(lm):
    """Return a list of augmented variants of the given landmark array.

    lm is expected to be an (N,3) numpy array (already normalized by detector).
    Augmentations: identity, horizontal flip, small gaussian jitter.
    """
    variants = []
    variants.append(lm)
    # horizontal flip (invert x axis)
    flip = lm.copy()
    flip[:, 0] = -flip[:, 0]
    variants.append(flip)
    # jitter
    jitter = lm + np.random.normal(scale=0.01, size=lm.shape)
    variants.append(jitter)
    return variants


def gather_data(manifest_rows, augment=True):
    X = []
    y = []
    label_set = set()
    for r in manifest_rows:
        lm_path = r.get('landmark_file') or r.get('landmark')
        label = r.get('label')
        if not lm_path or not label:
            continue
        try:
            lm = load_landmark(lm_path)
        except Exception as e:
            print(f"Warning: could not load {lm_path}: {e}")
            continue
        # ensure shape (N,3)
        lm = np.asarray(lm)
        if lm.ndim == 1:
            # flatten back to (N,3) if saved flattened
            lm = lm.reshape(-1, 3)

        variants = [lm]
        if augment:
            variants = augment_landmarks(lm)

        for v in variants:
            X.append(v.flatten())
            y.append(label)
            label_set.add(label)

    return np.asarray(X), np.asarray(y), sorted(list(label_set))


def stratified_split(X, y, labels, ratios=(0.7, 0.15, 0.15), seed=42):
    random.seed(seed)
    by_label = defaultdict(list)
    for xi, yi in zip(X, y):
        by_label[yi].append(xi)

    X_train, X_val, X_test = [], [], []
    y_train, y_val, y_test = [], [], []

    for label, items in by_label.items():
        random.shuffle(items)
        n = len(items)
        n_train = int(n * ratios[0])
        n_val = int(n * ratios[1])
        train_items = items[:n_train]
        val_items = items[n_train:n_train + n_val]
        test_items = items[n_train + n_val:]

        X_train.extend(train_items)
        y_train.extend([label] * len(train_items))
        X_val.extend(val_items)
        y_val.extend([label] * len(val_items))
        X_test.extend(test_items)
        y_test.extend([label] * len(test_items))

    return (np.asarray(X_train), np.asarray(y_train),
            np.asarray(X_val), np.asarray(y_val),
            np.asarray(X_test), np.asarray(y_test))


def save_processed(out_dir, splits):
    os.makedirs(out_dir, exist_ok=True)
    X_train, y_train, X_val, y_val, X_test, y_test = splits
    np.save(os.path.join(out_dir, 'X_train.npy'), X_train)
    np.save(os.path.join(out_dir, 'y_train.npy'), y_train)
    np.save(os.path.join(out_dir, 'X_val.npy'), X_val)
    np.save(os.path.join(out_dir, 'y_val.npy'), y_val)
    np.save(os.path.join(out_dir, 'X_test.npy'), X_test)
    np.save(os.path.join(out_dir, 'y_test.npy'), y_test)


def main(base='data/raw', out='data/processed', augment=True):
    manifest = os.path.join(base, 'manifests', 'manifest.csv')
    try:
        rows = load_manifest(manifest)
    except FileNotFoundError:
        print(f"No manifest found at {manifest}. Run the recorder first to collect samples.")
        return

    X, y, labels = gather_data(rows, augment=augment)
    if len(X) == 0:
        print("No data found in manifest. Exiting.")
        return

    splits = stratified_split(X, y, labels)
    save_processed(out, splits)
    print(f"Processed data saved to {out}. Labels: {labels}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', default='data/raw')
    parser.add_argument('--out', default='data/processed')
    parser.add_argument('--no-augment', action='store_true')
    args = parser.parse_args()
    main(base=args.base, out=args.out, augment=not args.no_augment)
