"""Train a simple landmark-based MLP baseline.

This script expects processed numpy arrays created by `scripts/process_data.py`.
If scikit-learn is not installed, it will print instructions.

Usage:
    python scripts/train_baseline.py --data data/processed --out models/landmark_mlp.joblib
"""
import os
import argparse
import sys
import numpy as np

# Allow running directly from repo root; ensure local packages are importable.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

def load_data(data_dir):
    X_train = np.load(os.path.join(data_dir, 'X_train.npy'))
    y_train = np.load(os.path.join(data_dir, 'y_train.npy'))
    X_val = np.load(os.path.join(data_dir, 'X_val.npy'))
    y_val = np.load(os.path.join(data_dir, 'y_val.npy'))
    return X_train, y_train, X_val, y_val


def train_mlp(X_train, y_train, X_val, y_val, out_path):
    try:
        from sklearn.neural_network import MLPClassifier
        from sklearn.preprocessing import LabelEncoder
        import joblib
    except Exception as e:
        print("scikit-learn or joblib not found.")
        print("Install with: pip install scikit-learn joblib")
        raise

    le = LabelEncoder()
    y_train_enc = le.fit_transform(y_train)
    y_val_enc = le.transform(y_val)

    clf = MLPClassifier(hidden_layer_sizes=(128, 64), max_iter=200, random_state=42)
    clf.fit(X_train, y_train_enc)

    train_acc = clf.score(X_train, y_train_enc)
    val_acc = clf.score(X_val, y_val_enc)
    print(f"Train acc: {train_acc:.4f}, Val acc: {val_acc:.4f}")

    os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)
    joblib.dump({'model': clf, 'label_encoder': le}, out_path)
    print(f"Saved model to {out_path}")


def main(data_dir='data/processed', out='models/landmark_mlp.joblib'):
    if not os.path.exists(data_dir):
        print(f"Processed data not found in {data_dir}. Run scripts/process_data.py first.")
        return
    X_train, y_train, X_val, y_val = load_data(data_dir)
    train_mlp(X_train, y_train, X_val, y_val, out)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', default='data/processed')
    parser.add_argument('--out', default='models/landmark_mlp.joblib')
    args = parser.parse_args()
    main(data_dir=args.data, out=args.out)
