from fastapi import WebSocket, Request
from fastapi.responses import JSONResponse, StreamingResponse
import asyncio
import time
import io
import os
import joblib
import numpy as np
import cv2
import logging

from ..capture import WebcamCapture
from ..detector import HandDetector
from ..classifier import SignClassifier
from ..translator import Translator
from config.settings import FRAME_RATE

logger = logging.getLogger(__name__)


# Components are initialized lazily so imports are cheap and startup
# doesn't try to open camera devices in import-time (which breaks CI and
# multiple worker deployments).
capture = None
detector = None
classifier = None
translator = None
decoding = False


def init_components(video_source=0):
    """Initialize capture/detector/classifier/translator if not already."""
    global capture, detector, classifier, translator
    if capture is None:
        try:
            capture = WebcamCapture(video_source=video_source)
        except Exception:
            capture = None
    if detector is None:
        try:
            detector = HandDetector()
        except Exception:
            detector = None
    if classifier is None:
        try:
            classifier = SignClassifier()
        except Exception:
            classifier = None
    if translator is None:
        try:
            translator = Translator()
        except Exception:
            translator = None


def release_components():
    global capture
    try:
        if capture is not None:
            capture.release()
    except Exception:
        pass


def get_capture():
    init_components()
    return capture


def get_detector():
    init_components()
    return detector


def get_classifier():
    init_components()
    return classifier


def get_translator():
    init_components()
    return translator


# Try to load a trained model (optional). Point to models/landmark_mlp_recorded.joblib by default.
MODEL_PATH = os.environ.get('LANDMARK_MODEL_PATH', os.path.join('models', 'landmark_mlp_recorded.joblib'))
_MODEL_OBJ = None
_MODEL = None
_LABEL_ENCODER = None

def load_model_if_needed():
    """Attempt to load the model lazily. Failures are caught so startup isn't blocked by incompatible binaries."""
    global _MODEL_OBJ, _MODEL, _LABEL_ENCODER
    if _MODEL is not None:
        return
    if not os.path.exists(MODEL_PATH):
        return
    try:
        _MODEL_OBJ = joblib.load(MODEL_PATH)
        if isinstance(_MODEL_OBJ, dict):
            _MODEL = _MODEL_OBJ.get('model') or _MODEL_OBJ.get('clf')
            _LABEL_ENCODER = _MODEL_OBJ.get('label_encoder') or _MODEL_OBJ.get('le')
        else:
            _MODEL = _MODEL_OBJ
    except Exception:
        # leave _MODEL as None and don't propagate exception (backend should still start)
        _MODEL_OBJ = None


def predict_from_landmarks(landmarks_np):
    """Return predicted label (str) and optional probabilities given landmarks numpy array."""
    global _MODEL, _LABEL_ENCODER
    # ensure model is loaded on first use (lazy)
    load_model_if_needed()
    if _MODEL is None:
        return None, None
    x = np.asarray(landmarks_np)
    if x.ndim == 2:
        x = x.flatten()
    x = x.reshape(1, -1)
    pred_idx = _MODEL.predict(x)
    proba = _MODEL.predict_proba(x).tolist() if hasattr(_MODEL, 'predict_proba') else None
    if _LABEL_ENCODER is not None:
        try:
            pred_label = _LABEL_ENCODER.inverse_transform(pred_idx)[0]
        except Exception:
            pred_label = pred_idx[0]
    else:
        pred_label = pred_idx[0]
    return pred_label, proba


async def websocket_decode(websocket: WebSocket):
    """WebSocket handler for real-time sign detection."""
    try:
        logger.info("Accepting WebSocket connection")
        await websocket.accept()
        logger.info("WebSocket connection accepted")
    except Exception as e:
        logger.error(f"Failed to accept WebSocket connection: {e}", exc_info=True)
        return
    
    global decoding
    decoding = True
    try:
        logger.info("Starting WebSocket decode loop")
        while decoding:
            try:
                cap = get_capture()
                det = get_detector()
                clf = get_classifier()
                tr = get_translator()
            except Exception as e:
                logger.error(f"Error initializing components: {e}", exc_info=True)
                try:
                    await websocket.send_text(f"Error: {str(e)}")
                except Exception:
                    break
                await asyncio.sleep(FRAME_RATE)
                continue
                
            if cap is None:
                try:
                    await websocket.send_text("No camera available")
                except Exception:
                    break
                await asyncio.sleep(FRAME_RATE)
                continue
            frame = cap.get_frame()
            if frame is not None and det is not None and clf is not None and tr is not None:
                landmarks = det.detect(frame)
                sign = clf.classify(landmarks)
                try:
                    tr.add_sign(sign)
                except Exception:
                    pass
                text = tr.get_text() if tr is not None else None
                # include model prediction when available
                pred, proba = (None, None)
                if landmarks is not None:
                    pred, proba = predict_from_landmarks(landmarks)
                # determine a single-letter suggestion (prefer model pred, fall back to classifier sign)
                next_letter = None
                try:
                    if pred and isinstance(pred, str) and len(pred) == 1 and pred.isalpha():
                        next_letter = pred
                    elif sign and isinstance(sign, str) and len(sign) == 1 and sign.isalpha():
                        next_letter = sign
                except Exception:
                    next_letter = None
                # send landmarks as list so frontend can overlay
                lm_list = None
                try:
                    if landmarks is not None:
                        lm_list = [[float(x), float(y), float(z)] for (x, y, z) in landmarks]
                except Exception:
                    lm_list = None
                try:
                    await websocket.send_json({"text": text, "sign": sign, "model_pred": pred, "proba": proba, "next_letter": next_letter, "landmarks": lm_list})
                except Exception as e:
                    logger.error(f"WebSocket send error: {e}")
                    break
            await asyncio.sleep(FRAME_RATE)
    except Exception as e:
        logger.error(f"WebSocket loop error: {e}", exc_info=True)
    finally:
        decoding = False
        logger.info("Closing WebSocket connection")
        try:
            await websocket.close()
        except Exception:
            pass


def start_decoding():
    global decoding
    decoding = True
    return JSONResponse({"status": "Decoding started"})


def stop_decoding():
    global decoding
    decoding = False
    tr = get_translator()
    text = tr.get_text() if tr is not None else None
    return JSONResponse({"status": "Decoding stopped", "text": text})


def get_decoded_text():
    tr = get_translator()
    return JSONResponse({"text": tr.get_text() if tr is not None else None})


def post_predict(landmarks):
    """API helper to predict from posted landmarks array (list or nested list)."""
    pred, proba = predict_from_landmarks(landmarks)
    if pred is None:
        return JSONResponse({"error": "No model loaded"}, status_code=503)
    # also provide a single-letter suggestion when possible
    next_letter = None
    try:
        if isinstance(pred, str) and len(pred) == 1 and pred.isalpha():
            next_letter = pred
    except Exception:
        next_letter = None
    return JSONResponse({"label": pred, "proba": proba, "next_letter": next_letter})


def _encode_jpeg(frame_bgr):
    ret, buf = cv2.imencode('.jpg', frame_bgr)
    if not ret:
        return None
    return buf.tobytes()


def mjpeg_generator(frame_rate=30):
    """Yield multipart/x-mixed-replace JPEG frames with optional overlayed prediction."""
    # convert frame rate to sleep time
    sleep_time = 1.0 / frame_rate if frame_rate > 0 else 0.03
    boundary = b'--frame'
    while True:
        cap = get_capture()
        det = get_detector()
        if cap is None:
            time.sleep(sleep_time)
            continue
        frame = cap.get_frame()
        if frame is None:
            time.sleep(sleep_time)
            continue
        # frame is RGB; convert to BGR for cv2
        disp = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        landmarks = None
        model_pred = None
        if det is not None:
            try:
                landmarks = det.detect(frame)
            except Exception:
                landmarks = None
        if landmarks is not None:
            # attempt prediction
            model_pred, _ = predict_from_landmarks(landmarks)
            # draw small circles for landmarks on disp
            try:
                h, w = disp.shape[:2]
                # landmarks are normalized around wrist; map to image center roughly
                for (x, y, z) in landmarks:
                    # landmarks from detector are normalized [0..1] with origin at image top-left
                    try:
                        cx = int(max(0, min(w - 1, x * w)))
                        cy = int(max(0, min(h - 1, y * h)))
                        cv2.circle(disp, (cx, cy), 3, (0, 255, 0), -1)
                    except Exception:
                        continue
            except Exception:
                pass
        if model_pred is not None:
            cv2.putText(disp, f"Model: {model_pred}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

        jpg = _encode_jpeg(disp)
        if jpg is None:
            time.sleep(sleep_time)
            continue
        # yield part
        yield (b'%b\r\nContent-Type: image/jpeg\r\n\r\n%b\r\n' % (boundary, jpg))
        time.sleep(sleep_time)
