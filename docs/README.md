# SignSpeak - American Sign Language Recognition System

A comprehensive real-time hand gesture recognition system that translates American Sign Language (ASL) gestures into text using computer vision and machine learning.

## 🚀 Quick Start

```bash
# 1. Set up environment
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 2. Record training data
python scripts/record_landmarks_only.py --video-source 0 --base data/landmarks_only --subject user

# 3. Train the model
python scripts/train_baseline.py

# 4. Start the API server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Visit `http://localhost:8000` to access the web interface.

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Development](#-development)
- [Testing](#-testing)
- [Contributing](#-contributing)

## ✨ Features

### Core Functionality
- **Real-time ASL Recognition**: Live webcam gesture detection and classification
- **Dual Model Support**: MLP classifier for alphabet letters + PyTorch model for common words
- **Web Interface**: Modern React-based frontend with live video streaming
- **REST API**: FastAPI backend with WebSocket support for real-time predictions
- **Data Collection**: Interactive tools for recording training data

### Technical Features
- **MediaPipe Integration**: High-performance hand landmark detection
- **Machine Learning Pipeline**: Complete data processing, training, and inference
- **MJPEG Streaming**: Low-latency video streaming for web interface
- **Cross-platform**: Windows/Linux/Mac support
- **Modular Architecture**: Clean separation of concerns

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Frontend  │    │   FastAPI Backend│    │   ML Models     │
│   (React/Vue)   │◄──►│   + WebSocket    │◄──►│   (MLP/PyTorch) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Video Stream  │    │   Hand Detection│    │   Training Data │
│   (MJPEG)       │    │   (MediaPipe)   │    │   (Landmarks)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Components

1. **Frontend**: React-based web interface for real-time interaction
2. **Backend API**: FastAPI server handling predictions and streaming
3. **Hand Detection**: MediaPipe-powered landmark extraction
4. **ML Models**: Scikit-learn MLP + PyTorch neural networks
5. **Data Pipeline**: Collection, processing, and augmentation tools

## 📁 Project Structure

```
signspeak/
├── 📁 config/              # Configuration files
│   ├── settings.py        # Global settings (camera, detection params)
│   └── readme.md
├── 📁 data/               # Training data and datasets
│   ├── 📁 raw/           # Raw captured images and landmarks
│   ├── 📁 processed/     # Preprocessed training data
│   └── 📁 manifests/     # Data manifests and metadata
├── 📁 docs/              # Documentation
│   ├── README.md         # This file
│   ├── STARTUP.md        # Complete setup guide
│   └── *.md              # Feature-specific docs
├── 📁 frontend/          # Web frontend (React/Vue)
├── 📁 models/            # Trained ML models
├── 📁 scripts/           # Utility scripts
│   ├── record_*.py       # Data collection tools
│   ├── train_*.py        # Training scripts
│   ├── process_*.py      # Data processing
│   └── realtime_*.py     # Live prediction tools
├── 📁 src/               # Core source code
│   ├── __init__.py
│   ├── capture.py        # Camera/video capture
│   ├── detector.py       # Hand detection (MediaPipe)
│   ├── classifier.py     # ML classification logic
│   ├── translator.py     # Text translation
│   ├── 📁 api/          # API endpoints
│   └── 📁 utils/        # Helper utilities
├── 📁 tests/             # Test suite
├── 📁 green/             # Security/validation module
├── 📁 helper_ai/         # AI assistance utilities
├── main.py               # FastAPI application entry point
├── pyproject.toml        # Project configuration
├── requirements.txt      # Python dependencies
└── QUICK_START.txt       # Quick start guide
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Webcam or video device
- 4GB+ RAM recommended

### Setup Steps

1. **Clone/Download the project**
2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation**
   ```bash
   python -c "import cv2, mediapipe, fastapi; print('✅ All dependencies installed')"
   ```

## 🎯 Usage

### Data Collection
```bash
# Record landmark data for training
python scripts/record_landmarks_only.py --video-source 0 --base data/landmarks_only --subject user

# Record image data (alternative)
python scripts/record_data.py --output data/raw --camera 0
```

### Model Training
```bash
# Train baseline MLP model
python scripts/train_baseline.py

# Process data first if needed
python scripts/process_data.py --input data/raw --output data/processed
```

### Running the Application
```bash
# Start the API server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Access the web interface at http://localhost:8000
```

### Real-time Testing
```bash
# Test predictions locally
python scripts/realtime_predict.py --model models/landmark_mlp_recorded.joblib --camera 0
```

## 🔌 API Documentation

### Endpoints

#### GET `/`
Serves the web frontend interface.

#### GET `/stream`
Returns MJPEG video stream with landmark overlays.
- **Response**: `multipart/x-mixed-replace` stream

#### POST `/predict`
Single gesture prediction from landmark data.
- **Request Body**: JSON with landmark coordinates
- **Response**: Predicted gesture label and confidence

#### WebSocket `/ws/decode`
Real-time gesture streaming.
- **Messages**: Landmark data → Prediction results

### Example API Usage

```python
import requests
import json

# Single prediction
landmarks = [...]  # 21 hand landmarks
response = requests.post('http://localhost:8000/predict',
                        json={'landmarks': landmarks})
print(response.json())
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_pipeline.py

# Test camera availability
python scripts/test_camera_indices.py
```

## 🔧 Development

### Adding New Gestures
1. Record training data using `record_landmarks_only.py`
2. Add gesture to model training pipeline
3. Update classifier logic if needed

### Model Improvements
- Experiment with different architectures in `src/classifier.py`
- Add data augmentation in `scripts/process_data.py`
- Tune hyperparameters in training scripts

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is open source. See individual files for license information.

## 🙏 Acknowledgments

- MediaPipe for hand detection
- FastAPI for the web framework
- OpenCV for computer vision utilities
- Scikit-learn for machine learning tools

## 📞 Support

For issues and questions:
1. Check the [documentation](./docs/)
2. Review existing [issues](../../issues)
3. Create a new issue with detailed information

---

**Last Updated**: April 2026
**Version**: 0.1.0</content>
<parameter name="filePath">c:\Users\medhu\Desktop\Work\SignLanguage\SignSpeak_MAin\README.md