# Configuration Guide

## Environment Variables

All configuration is managed through environment variables, with defaults provided in `src/core/config.py`.

### Quick Start

Copy `.env.example` to `.env` and adjust as needed:

```bash
cp .env.example .env
```

### Camera Configuration

```env
CAMERA_INDEX=0                 # Camera device index (0 = default)
MAX_HANDS=1                    # Maximum hands to detect
DETECTION_CONFIDENCE=0.7       # MediaPipe detection confidence
TRACKING_CONFIDENCE=0.5        # MediaPipe tracking confidence
```

### Inference Pipeline

These settings control prediction smoothing and debouncing:

```env
FRAME_BUFFER_SIZE=5            # Number of frames to aggregate (1-10)
CONFIDENCE_THRESHOLD=0.4       # Minimum confidence to accept (0.0-1.0)
LETTER_HOLD_FRAMES=3           # Frames prediction must be stable (1-5)
LETTER_COOLDOWN_MS=200         # Milliseconds between duplicate letters
```

**Tuning Guide**:
- Lower `CONFIDENCE_THRESHOLD` → More predictions but lower accuracy
- Higher `FRAME_BUFFER_SIZE` → Smoother but higher latency
- Higher `LETTER_HOLD_FRAMES` → More stable but slower response

### Model Settings

```env
MODEL_PATH=models/landmark_mlp_recorded.joblib
GPU_ENABLED=true               # Use GPU if available (requires CUDA)
```

### Server Settings

```env
HOST=0.0.0.0                   # Bind address
PORT=8000                      # Server port
RELOAD=false                   # Auto-reload on code change (dev only)
```

### Logging

```env
LOG_LEVEL=INFO                 # DEBUG | INFO | WARNING | ERROR | CRITICAL
LOG_FILE=logs/signspeak.log    # Log file path
```

## Loading Configuration

Configuration is automatically loaded on application startup:

```python
from src.core.config import Config

# Automatic from environment variables
config = Config.from_env()

# Access settings
print(config.CONFIDENCE_THRESHOLD)
print(config.GPU_ENABLED)
```

## Environment-Specific Profiles

### Development

```env
LOG_LEVEL=DEBUG
RELOAD=true
CONFIDENCE_THRESHOLD=0.3       # More lenient
```

### Production

```env
LOG_LEVEL=WARNING
RELOAD=false
CONFIDENCE_THRESHOLD=0.5       # More strict
GPU_ENABLED=true
```

### Testing

```env
LOG_LEVEL=ERROR
PORT=8001
FRAME_BUFFER_SIZE=3
```

## Camera Configuration

### Windows

Camera device numbering:
- `0` = Built-in webcam (default)
- `1+` = USB cameras in connection order

### Linux

Use v4l2-ctl to list devices:

```bash
v4l2-ctl --list-devices
```

Set CAMERA_INDEX accordingly.

### macOS

Typically `0` for built-in camera, check with:

```bash
ffmpeg -f avfoundation -list_devices true -i ""
```

## Performance Tuning

### For Real-time Performance

```env
FRAME_BUFFER_SIZE=3            # Reduce latency
LETTER_HOLD_FRAMES=2           # Faster response
CONFIDENCE_THRESHOLD=0.5       # Higher precision
```

### For Accuracy

```env
FRAME_BUFFER_SIZE=7            # More aggregation
LETTER_HOLD_FRAMES=4           # More stability
CONFIDENCE_THRESHOLD=0.3       # Lower threshold
```

### For GPU Acceleration

Ensure CUDA is installed and:

```env
GPU_ENABLED=true
```

Check GPU status in `/health` endpoint.

## Validation

Validate configuration on startup:

```bash
curl http://localhost:8000/health
# Response includes configuration status
```

Check model info:

```bash
curl http://localhost:8000/model-info
```

## Troubleshooting

### Camera not detected

1. Check CAMERA_INDEX:
   ```env
   CAMERA_INDEX=1  # Try next device
   ```

2. Verify camera is not in use by another application

3. Test with OpenCV:
   ```python
   import cv2
   cap = cv2.VideoCapture(0)
   print(cap.isOpened())
   ```

### Low predictions accuracy

1. Increase `CONFIDENCE_THRESHOLD`
2. Increase `FRAME_BUFFER_SIZE`
3. Check camera lighting
4. Ensure good hand visibility

### High latency

1. Decrease `FRAME_BUFFER_SIZE`
2. Decrease `LETTER_HOLD_FRAMES`
3. Enable GPU with `GPU_ENABLED=true`
4. Check system resources

### Model loading error

1. Verify model file path in `MODEL_PATH`
2. Check file permissions
3. Verify model file integrity
4. See logs for detailed error

## Advanced Configuration

### Custom Model

To use a different model:

```env
MODEL_PATH=models/my_custom_model.joblib
```

Ensure model is compatible with landmark input (63-dimensional vector).

### Custom Logging

Modify `src/core/logger.py` for custom log format or handlers.

### WebSocket Settings

Currently hardcoded in `main.py`. To customize:

```python
CONFIG.RECONNECT_INTERVAL = 3000  # milliseconds
CONFIG.MAX_HISTORY = 10           # predictions
```

## Configuration Validation

Run tests to validate configuration:

```bash
pytest tests/test_services.py -v
```

## Reference

For complete configuration options, see:
- `src/core/config.py` - Configuration class definition
- `.env.example` - Example environment file
- `main.py` - Usage in application
