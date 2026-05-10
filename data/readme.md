# Data Organization Guide

## Overview

SignSpeak uses a structured data pipeline for collecting, processing, and training gesture recognition models. This document explains the data organization and workflow.

## Directory Structure

```
data/
├── 📁 raw/               # Raw captured data
│   ├── 📁 images/       # Original images (A-Z folders)
│   ├── 📁 landmarks/    # Raw landmark .npy files (A-Z folders)
│   └── 📁 manifests/    # CSV manifests with metadata
├── 📁 processed/        # Preprocessed training data
│   ├── X_train.npy     # Training features
│   ├── X_val.npy       # Validation features
│   ├── y_train.npy     # Training labels
│   └── y_val.npy       # Validation labels
├── 📁 landmarks_only/   # Landmark-focused dataset
│   ├── 📁 landmarks/   # Processed landmark files
│   └── 📁 manifests/   # Manifest files
└── 📁 e2e_test/         # End-to-end test data
    ├── 📁 landmarks/   # Test landmarks
    └── 📁 manifests/   # Test manifests
```

## Data Formats

### Landmark Files (.npy)
- **Format**: NumPy arrays with shape `(n_samples, 63)` or `(n_samples, 21, 3)`
- **Content**: Flattened hand landmark coordinates (x, y, z for 21 points)
- **Normalization**: Coordinates normalized relative to wrist landmark

### Image Files
- **Format**: JPEG/PNG images
- **Naming**: `{label}_{timestamp}.jpg`
- **Content**: Raw webcam captures with hand gestures

### Manifest Files (CSV)
```csv
filename,label,timestamp,subject,confidence
A_1640995200000.npy,A,1640995200000,user1,0.95
B_1640995201000.npy,B,1640995201000,user1,0.92
```

## Data Collection Workflow

### 1. Landmark Recording
```bash
python scripts/record_landmarks_only.py --video-source 0 --base data/landmarks_only --subject user
```
- **Output**: Saves landmark arrays to `data/landmarks_only/landmarks/{label}/`
- **Format**: Individual .npy files per gesture sample

### 2. Image Recording (Alternative)
```bash
python scripts/record_data.py --output data/raw --camera 0
```
- **Output**: Saves images to `data/raw/images/{label}/`
- **Format**: JPEG images with automatic labeling

### 3. Landmark Extraction
```bash
python scripts/extract_landmarks.py --input data/raw/images --output data/raw/landmarks
```
- **Input**: Image directories
- **Output**: Landmark .npy files
- **Process**: Runs MediaPipe on each image

### 4. Data Processing
```bash
python scripts/process_data.py --input data/raw --output data/processed
```
- **Features**:
  - Normalization and scaling
  - Data augmentation (flips, jitter)
  - Train/validation/test splits
  - Outlier removal

## Data Quality Guidelines

### Recording Best Practices
- **Lighting**: Well-lit environment, avoid backlighting
- **Background**: Plain background to reduce noise
- **Positioning**: Hand centered in frame, consistent distance
- **Speed**: Slow, deliberate gestures for clear capture
- **Variations**: Multiple angles, lighting conditions, hand sizes

### Quality Metrics
- **Landmark Confidence**: > 0.8 for reliable samples
- **Hand Detection Rate**: > 95% successful detections
- **Gesture Clarity**: Clear, unambiguous gestures
- **Sample Diversity**: Multiple subjects, conditions

## Training Data Requirements

### Minimum Dataset Sizes
- **Alphabet Letters**: 100-200 samples per letter (A-Z)
- **Common Words**: 50-100 samples per word
- **Total Samples**: 2,600+ for basic alphabet recognition

### Data Augmentation
- **Geometric**: Rotation (±15°), scaling (0.8-1.2x)
- **Color**: Brightness/contrast adjustments
- **Spatial**: Horizontal flips, small translations
- **Temporal**: Frame interpolation for sequences

## Model Training Data

### Feature Format
```python
# Single sample shape
X_sample.shape  # (63,) - flattened landmarks
# Batch shape
X_train.shape   # (n_samples, 63)
y_train.shape   # (n_samples,) - encoded labels
```

### Label Encoding
- **Alphabet**: 0-25 (A=0, B=1, ..., Z=25)
- **Words**: 0-9 (hello=0, bye=1, etc.)
- **Format**: Integer labels for classification

## Testing and Validation

### Cross-Validation
- **K-Fold**: 5-fold stratified cross-validation
- **Subject-wise**: Separate subjects for train/val/test
- **Temporal**: Time-based splits for sequence data

### Evaluation Metrics
- **Accuracy**: Overall classification accuracy
- **Precision/Recall**: Per-class performance
- **Confusion Matrix**: Error analysis
- **Real-time Performance**: FPS, latency measurements

## Data Management Commands

### Cleanup
```bash
# Remove processed data
rm -rf data/processed/

# Remove raw captures
rm -rf data/raw/images/
```

### Backup
```bash
# Archive training data
tar -czf data_backup.tar.gz data/

# Sync to cloud storage
aws s3 sync data/ s3://signspeak-data/
```

### Statistics
```bash
# Count samples per class
find data/landmarks_only/landmarks -name "*.npy" | wc -l

# Check data distribution
python -c "
import os
import numpy as np
base = 'data/landmarks_only/landmarks'
for label in os.listdir(base):
    count = len(os.listdir(os.path.join(base, label)))
    print(f'{label}: {count} samples')
"
```

## Troubleshooting

### Common Issues
- **Low Detection Rate**: Check lighting, camera quality, hand positioning
- **Inconsistent Landmarks**: Ensure stable hand position during recording
- **Model Overfitting**: Increase data augmentation, collect more samples
- **Real-time Lag**: Optimize model size, reduce input resolution

### Data Validation
```python
# Check landmark file integrity
import numpy as np
data = np.load('sample.npy')
assert data.shape[-1] == 63, f"Invalid shape: {data.shape}"
assert np.isfinite(data).all(), "Contains NaN/inf values"
```