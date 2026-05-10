# 📊 Complete Project Directory Tree

```
SignSpeak/
│
├─ 🚀 START.bat ............................ MAIN LAUNCHER (Click here!)
├─ main.py ............................... FastAPI Application Entry
├─ requirements.txt ....................... Python Dependencies
├─ pyproject.toml ......................... Project Configuration
├─ .gitignore ............................ Git Ignore Rules
│
├─ 📋 README.md .......................... Main Documentation
├─ 📋 ORGANIZATION.md .................... This Folder Organization
├─ 📋 QUICK_START.md ..................... Quick Launch Guide
├─ 📋 PROJECT_MAP.md ..................... Project Structure Map
│
│
├─ 📁 src/ ............................... CORE APPLICATION CODE
│  ├─ __init__.py
│  ├─ capture.py ......................... Video Capture
│  ├─ classifier.py ...................... Sign Classification
│  ├─ detector.py ........................ Hand Detection (MediaPipe)
│  ├─ translator.py ...................... ASL Translation
│  │
│  ├─ 📁 api/ ............................ FastAPI Endpoints
│  │  ├─ __init__.py
│  │  └─ endpoints.py .................... Route Definitions
│  │
│  └─ 📁 utils/ .......................... Utility Functions
│     ├─ __init__.py
│     └─ helpers.py ...................... Helper Functions
│
│
├─ 📁 models/ ............................ MACHINE LEARNING MODELS
│  ├─ sign_model.pth ..................... PyTorch Model (Gestures)
│  ├─ landmark_mlp_recorded.joblib ....... Scikit-Learn Classifier
│  │
│  └─ 📁 ignore/ ......................... Deprecated Models
│     ├─ e2e_test_model.joblib
│     └─ landmark_mlp_recorded_one.joblib
│
│
├─ 📁 data/ .............................. TRAINING & TEST DATA
│  │
│  ├─ 📁 processed/ ...................... Processed Datasets
│  │  ├─ X_train.npy
│  │  ├─ X_test.npy
│  │  ├─ X_val.npy
│  │  ├─ y_train.npy
│  │  ├─ y_test.npy
│  │  └─ y_val.npy
│  │
│  ├─ 📁 landmarks_only/ ................ Landmark-Only Data
│  │  ├─ 📁 landmarks/
│  │  │  └─ [A-Z folders with .npy files]
│  │  ├─ 📁 manifests/
│  │  │  └─ manifest.csv
│  │  └─ readme.md
│  │
│  ├─ 📁 raw/ ........................... Raw Image Data
│  │  ├─ 📁 images/ ..................... Original Images
│  │  │  └─ [A-Z + unknown folders]
│  │  ├─ 📁 landmarks/ .................. Extracted Landmarks
│  │  │  └─ [A-Z folders]
│  │  ├─ 📁 manifests/
│  │  │  └─ manifest.csv
│  │  └─ readme.md
│  │
│  ├─ 📁 e2e-ignore/ .................... End-To-End Test Data
│  │  ├─ 📁 e2e_processed/
│  │  │  ├─ X_test.npy
│  │  │  ├─ X_train.npy
│  │  │  ├─ X_val.npy
│  │  │  ├─ y_test.npy
│  │  │  ├─ y_train.npy
│  │  │  └─ y_val.npy
│  │  ├─ 📁 e2e_test/
│  │  │  ├─ 📁 landmarks/
│  │  │  │  └─ [A-Z folders]
│  │  │  └─ 📁 manifests/
│  │  │     └─ manifest.csv
│  │  └─ readme.md
│  │
│  └─ readme.md .......................... Data Documentation
│
│
├─ 📁 scripts/ ........................... UTILITY SCRIPTS
│  ├─ record_data.py ..................... Record Training Data
│  ├─ record_landmarks_only.py ........... Record Landmarks Only
│  ├─ extract_landmarks.py .............. Extract Hand Landmarks
│  ├─ process_data.py ................... Process Raw Data
│  ├─ train_baseline.py ................. Train ML Model
│  └─ realtime_predict.py ............... Real-Time Prediction
│
│
├─ 📁 frontend/ .......................... WEB USER INTERFACE
│  │
│  ├─ 📁 dist/ .......................... Built Frontend (Production)
│  │
│  ├─ 📁 demo/ .......................... DEMO UI
│  │  └─ test_ui.html ................... ⭐ Standalone Demo (No Backend!)
│  │
│  └─ stuff.md .......................... Frontend Notes
│
│
├─ 📁 config/ ........................... CONFIGURATION FILES
│  ├─ settings.py ....................... Application Settings
│  └─ readme.md ......................... Config Documentation
│
│
├─ 📁 docs/ ............................. 📚 DOCUMENTATION
│  │
│  ├─ README.md ......................... Documentation Index
│  ├─ QUICK_START.md .................... Quick Start Guide (Root Copy)
│  ├─ COMPETITION_READY.md .............. Competition Checklist
│  ├─ FOLDER_STRUCTURE.md ............... Folder Structure Detail
│  ├─ API.md ............................ API Documentation
│  ├─ STARTUP.md ........................ Startup Guide
│  ├─ LANDMARKS_QUICK_START.md .......... Landmark Collection Guide
│  ├─ data_collection.md ................ Data Collection Process
│  ├─ FRONTEND_SETUP.md ................. Frontend Setup Instructions
│  ├─ FRONTEND_COMPLETE.md .............. Frontend Completion Status
│  ├─ start.md .......................... Startup Notes
│  │
│  └─ 📁 guides/ ........................ Additional Guides
│     └─ [Future guides]
│
│
├─ 📁 tests/ ............................ UNIT TESTS
│  ├─ readme.md
│  ├─ test_capture.py ................... Capture Tests
│  ├─ test_pipeline.py .................. Pipeline Tests
│  ├─ test_camera_indices.py ............ Camera Tests
│  ├─ test_websocket.py ................. WebSocket Tests
│  ├─ test_raw_ws.py .................... Raw WebSocket Tests
│  └─ minimal_ws_test.py ................ Minimal Test
│
│
├─ 📁 tools/ ............................ 🛠️ DEVELOPMENT TOOLS
│  └─ run.bat ........................... Main Launcher Script
│
│
├─ 📁 notebooks/ ........................ JUPYTER NOTEBOOKS (Optional)
│  └─ [Future analysis notebooks]
│
│
├─ 📁 green/ ............................ SECURITY & VALIDATION
│  ├─ __init__.py
│  ├─ green.py .......................... Tag File Verification
│  ├─ README.MD
│  │
│  └─ 📁 encrypt/
│     └─ project.tag .................... Project Validation Tag
│
│
├─ 📁 helper_ai/ ........................ AI HELPERS
│  ├─ __init__.py
│  └─ get_response.py ................... Response Generation
│
│
└─ 📁 .venv/ ............................ 🐍 PYTHON VIRTUAL ENVIRONMENT
   └─ [Python 3.12.7 packages]
      ├─ fastapi
      ├─ uvicorn
      ├─ tensorflow
      ├─ opencv-python
      ├─ mediapipe
      ├─ scikit-learn
      ├─ joblib
      ├─ numpy
      └─ [more...]
```

---

## 🎯 Where To Find Things

### 🚀 To Launch
- Click **START.bat** (root)
- Or run **tools/run.bat**

### 🎨 To Try Demo
- Open **frontend/demo/test_ui.html** in browser

### 📖 To Read Docs
- Start with **README.md**
- Or check **docs/** folder
- Quick reference: **QUICK_START.md**

### 💻 To Code
- Application: **src/**
- Models: **models/**
- Scripts: **scripts/**

### 🧪 To Test
- Tests: **tests/**

### 📊 To Access Data
- Training data: **data/processed/**
- Raw data: **data/raw/**
- Landmarks: **data/landmarks_only/**

### ⚙️ To Configure
- Settings: **config/settings.py**

---

**Project is organized, cleaned up, and ready for competition! 🏆**
