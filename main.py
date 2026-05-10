"""SignSpeak V2 - FastAPI Application Entry Point."""

import os
import asyncio
import time
from pathlib import Path
from threading import Thread, Lock

import cv2
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

# Core imports
from src.core.config import Config
from src.core.logger import setup_logging, get_logger
from src.detector import HandDetector
from src.classifier import SignClassifier
from src.translator import Translator
from src.services.inference import InferencePipeline
from src.services.model_loader import ModelLoader
from src.services.websocket_manager import WebSocketManager
from src.services.word_builder import WordBuilder
from green.green import verify_tag_file

# ==================================================
# INITIALIZATION
# ==================================================

# Validate tag file
if not verify_tag_file():
    print("🔴 .tag file missing or invalid! Exiting.")
    exit(1)

# Setup configuration
config = Config.from_env()

# Setup logging
setup_logging(log_file=config.LOG_FILE, level=config.LOG_LEVEL)
logger = get_logger(__name__)

logger.info("=" * 60)
logger.info("SignSpeak V2 - Starting up...")
logger.info(str(config))
logger.info("=" * 60)

# ==================================================
# FASTAPI APP
# ==================================================

app = FastAPI(
    title="SignSpeak V2 - ASL Interpreter API",
    version="2.0.0",
    description="Professional AI-powered sign language recognition platform",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
frontend_path = Path(__file__).parent / "frontend" / "dist"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")
    logger.info(f"Frontend mounted: {frontend_path}")

# ==================================================
# INITIALIZE SERVICES
# ==================================================

# Hand detector
detector = HandDetector(
    max_num_hands=config.MAX_HANDS,
    detection_confidence=config.DETECTION_CONFIDENCE,
    tracking_confidence=config.TRACKING_CONFIDENCE,
)
logger.info("Hand detector initialized")

# Model loader
model_loader = ModelLoader(model_path=config.MODEL_PATH, gpu_enabled=config.GPU_ENABLED)
try:
    model_loader.load()
    logger.info(f"Model loaded: {model_loader.get_health_status()}")
except Exception as e:
    logger.error(f"Model loading failed: {e}")
    model_loader = None

# Classifier
classifier = SignClassifier(model_loader=model_loader)
logger.info("Sign classifier initialized")

# Inference pipeline
inference_pipeline = InferencePipeline(
    frame_buffer_size=config.FRAME_BUFFER_SIZE,
    confidence_threshold=config.CONFIDENCE_THRESHOLD,
    letter_hold_frames=config.LETTER_HOLD_FRAMES,
    letter_cooldown_ms=config.LETTER_COOLDOWN_MS,
)
logger.info("Inference pipeline initialized")

# Word builder
word_builder = WordBuilder(pause_threshold_sec=2.0, max_word_length=50)
logger.info("Word builder initialized")

# WebSocket manager
ws_manager = WebSocketManager()
logger.info("WebSocket manager initialized")

# Translator (backward compatibility)
translator = Translator()
logger.info("Translator initialized")

# ==================================================
# CAMERA THREAD
# ==================================================

camera = cv2.VideoCapture(config.CAMERA_INDEX)
frame_lock = Lock()
latest_frame = None
start_time = time.time()


def camera_loop():
    """Background thread for camera capture."""
    global latest_frame
    logger.info("Camera thread started")
    while True:
        try:
            ret, frame = camera.read()
            if ret:
                with frame_lock:
                    latest_frame = frame.copy()
        except Exception as e:
            logger.error(f"Camera capture error: {e}")
            time.sleep(0.1)


def get_frame():
    """Get latest camera frame."""
    with frame_lock:
        if latest_frame is not None:
            return latest_frame.copy()
    return None


# Start camera thread
camera_thread = Thread(target=camera_loop, daemon=True)
camera_thread.start()
logger.info("Camera thread started")


# ==================================================
# ROUTES
# ==================================================


@app.get("/")
async def root():
    """Serve landing page."""
    landing_file = frontend_path / "landing.html"
    if landing_file.exists():
        return FileResponse(str(landing_file))
    
    app_file = frontend_path / "app.html"
    if app_file.exists():
        return FileResponse(str(app_file))
    
    index_file = frontend_path / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    
    return {"message": "SignSpeak V2 API running 🚀"}


@app.get("/app")
async def app_page():
    """Serve application page."""
    app_file = frontend_path / "app.html"
    if app_file.exists():
        return FileResponse(str(app_file))
    
    index_file = frontend_path / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    
    return {"message": "App not found"}


@app.get("/ping")
async def ping():
    """Health check endpoint."""
    return {"message": "pong 🟢"}


@app.get("/health")
async def health():
    """Detailed health status."""
    uptime = time.time() - start_time
    return {
        "status": "healthy" if model_loader and model_loader.model else "degraded",
        "camera": get_frame() is not None,
        "model": model_loader is not None and model_loader.model is not None,
        "uptime_seconds": int(uptime),
        "websocket_connections": ws_manager.get_connection_count(),
    }


@app.get("/stats")
async def stats():
    """Get current statistics."""
    pipeline_stats = inference_pipeline.get_stats()
    return {
        "fps": pipeline_stats.get("fps", 0),
        "avg_inference_ms": pipeline_stats.get("avg_inference_ms", 0),
        "frame_count": pipeline_stats.get("frame_count", 0),
        "uptime_seconds": int(time.time() - start_time),
        "websocket_connections": ws_manager.get_connection_count(),
    }


@app.get("/model-info")
async def model_info():
    """Get model information."""
    if model_loader is None:
        return {"error": "Model not loaded"}
    return model_loader.get_model_info()


# ==================================================
# STREAM ENDPOINT
# ==================================================


def generate_frames():
    """Generate MJPEG frames."""
    while True:
        frame = get_frame()
        if frame is None:
            continue

        _, buffer = cv2.imencode(".jpg", frame)
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
        )


@app.get("/stream")
async def stream():
    """Stream MJPEG video feed."""
    return StreamingResponse(
        generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame"
    )


# ==================================================
# WEBSOCKET: INFERENCE PIPELINE
# ==================================================


@app.websocket("/ws/decode")
async def decode_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time letter prediction."""
    await websocket.accept()
    await ws_manager.add_connection(websocket)
    logger.info(f"WebSocket connected. Total connections: {ws_manager.get_connection_count()}")

    try:
        while True:
            # Get frame
            frame = get_frame()
            if frame is None:
                await websocket.send_json(
                    {"letter": None, "status": "no_frame", "confidence": 0.0}
                )
                await asyncio.sleep(0.05)
                continue

            # Convert to RGB
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Detect landmarks
            landmarks = detector.detect(rgb)
            if landmarks is None:
                await websocket.send_json(
                    {"letter": None, "status": "no_hand", "confidence": 0.0}
                )
                await asyncio.sleep(0.05)
                continue

            # Classify
            start_inference = time.time()
            prediction, confidence = classifier.classify_with_confidence(landmarks)
            inference_time_ms = (time.time() - start_inference) * 1000

            if prediction is None:
                await websocket.send_json(
                    {"letter": None, "status": "low_confidence", "confidence": 0.0}
                )
                await asyncio.sleep(0.05)
                continue

            # Get top 3
            top_3 = classifier.get_top_predictions(landmarks, k=3)

            # Process through inference pipeline
            result = inference_pipeline.process(
                prediction=prediction,
                confidence=confidence,
                inference_time_ms=inference_time_ms,
                top_3_predictions=top_3,
            )

            # Add letter to word builder if accepted
            if result["letter"]:
                word_builder.add_letter(result["letter"])

            # Send response
            await websocket.send_json(
                {
                    "letter": result["letter"],
                    "confidence": result["confidence"],
                    "top_3": result["top_3"],
                    "state": result["state"],
                    "fps": result["fps"],
                    "current_word": word_builder.get_current_word(),
                    "sentence": word_builder.get_sentence(),
                    "landmarks": landmarks.tolist() if isinstance(landmarks, np.ndarray) else landmarks,
                }
            )

            await asyncio.sleep(0.05)

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await ws_manager.remove_connection(websocket)
        logger.info(f"Connection closed. Total connections: {ws_manager.get_connection_count()}")


# ==================================================
# STARTUP/SHUTDOWN
# ==================================================


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("Application started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Application shutting down...")
    camera.release()
    await ws_manager.disconnect_all()
    logger.info("Application stopped")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.RELOAD,
        log_level=config.LOG_LEVEL.lower(),
    )