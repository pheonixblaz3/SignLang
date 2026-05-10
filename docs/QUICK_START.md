# 🎯 Quick Start Guide

## 🚀 Launch in 3 Steps

### 1️⃣ Click START.bat
Find and double-click **START.bat** in the project root folder

### 2️⃣ Wait for Server to Start
The server will start automatically and show:
```
Starting FastAPI Server...
Server available at:
   - Web UI: http://localhost:8000
   - API Docs: http://localhost:8000/docs
```

### 3️⃣ Open in Browser
Visit: **http://localhost:8000**

---

## 📚 Available Resources

### 🎨 Demo UI (No Backend Required!)
Open **frontend/demo/test_ui.html** in any browser for a beautiful demo

### 📖 Documentation
- Full API docs at: http://localhost:8000/docs
- More guides in the **docs/** folder

### 🧪 Test Real-Time Recognition
Once the server starts, use the web interface to test ASL recognition

---

## ⚙️ Troubleshooting

### START.bat doesn't work?
Try running `tools\run.bat` from PowerShell/Command Prompt

### Port 8000 already in use?
Modify the port in tools/run.bat (change 8000 to another number)

### Python not found?
Ensure Python 3.10+ is installed and in your system PATH

---

## 📂 Project Structure

```
SignSpeak/
├── START.bat           ← Main launcher
├── main.py             ← Application
├── frontend/demo/      ← Demo UI
├── docs/               ← Documentation
├── src/                ← Source code
├── models/             ← ML models
├── data/               ← Training data
└── scripts/            ← Utilities
```

---

**Need help?** Check the documentation in the **docs/** folder! 📖
