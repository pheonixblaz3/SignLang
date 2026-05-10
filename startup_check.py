#!/usr/bin/env python3
"""Startup check script for SignSpeak V2."""

import sys
import os
import time
from pathlib import Path

def check_python_version():
    """Check Python version."""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("❌ Python 3.10+ required")
        return False
    print("✅ Python version OK")
    return True

def check_dependencies():
    """Check if dependencies are installed."""
    deps = [
        'fastapi', 'uvicorn', 'numpy', 'scipy',
        'sklearn', 'joblib', 'mediapipe', 'cv2', 'pydantic'
    ]
    missing = []
    for dep in deps:
        try:
            __import__(dep)
            print(f"✅ {dep} OK")
        except ImportError:
            missing.append(dep)
            print(f"❌ {dep} missing")
    return len(missing) == 0

def check_files():
    """Check if required files exist."""
    files = [
        'main.py',
        'models/landmark_mlp_recorded.joblib',
        'frontend/dist/landing.html',
        'frontend/dist/app.html',
        'src/core/config.py',
        'src/services/model_loader.py'
    ]
    missing = []
    for file in files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            missing.append(file)
            print(f"❌ {file} missing")
    return len(missing) == 0

def check_imports():
    """Check if imports work."""
    try:
        from src.core.config import Config
        print("✅ Config import OK")
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False

    try:
        from src.services.model_loader import ModelLoader
        print("✅ ModelLoader import OK")
    except Exception as e:
        print(f"❌ ModelLoader import failed: {e}")
        return False

    try:
        from src.detector import HandDetector
        print("✅ HandDetector import OK")
    except Exception as e:
        print(f"❌ HandDetector import failed: {e}")
        return False

    return True

def check_model_loading():
    """Check if model can be loaded."""
    try:
        from src.services.model_loader import ModelLoader
        ml = ModelLoader('models/landmark_mlp_recorded.joblib', False)
        ml.load()
        print("✅ Model loading OK")
        return True
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return False

def main():
    """Run all checks."""
    print("🔍 SignSpeak V2 Startup Check")
    print("=" * 40)

    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Files", check_files),
        ("Imports", check_imports),
        ("Model Loading", check_model_loading),
    ]

    all_passed = True
    for name, check_func in checks:
        print(f"\n📋 Checking {name}...")
        if not check_func():
            all_passed = False

    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 All checks passed! Ready to start.")
        print("\n🚀 Startup command:")
        print("   .\\.venv\\Scripts\\python.exe main.py")
        print("\n🌐 Then visit:")
        print("   http://localhost:8000 (landing page)")
        print("   http://localhost:8000/app (application)")
    else:
        print("❌ Some checks failed. Fix issues before starting.")
        sys.exit(1)

if __name__ == "__main__":
    main()