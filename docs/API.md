# SignSpeak API Documentation

## Overview

SignSpeak provides a REST API and WebSocket interface for real-time American Sign Language gesture recognition.

## Base URL
```
http://localhost:8000
```

## Endpoints

### GET `/`
**Serve Web Frontend**
- **Description**: Returns the main web interface
- **Response**: HTML page with React/Vue frontend

### GET `/stream`
**MJPEG Video Stream**
- **Description**: Live video stream with hand landmark overlays
- **Response**: `multipart/x-mixed-replace` MJPEG stream
- **Content-Type**: `multipart/x-mixed-replace; boundary=frame`

### POST `/predict`
**Single Gesture Prediction**
- **Description**: Classify a single gesture from landmark data
- **Request Body**:
  ```json
  {
    "landmarks": [
      [0.5, 0.3, 0.1],  // x, y, z coordinates for landmark 0
      [0.6, 0.4, 0.2],  // landmark 1
      // ... 21 landmarks total
    ]
  }
  ```
- **Response**:
  ```json
  {
    "prediction": "A",
    "confidence": 0.95,
    "model": "mlp"
  }
  ```

### WebSocket `/ws/decode`
**Real-time Gesture Streaming**
- **Description**: Bidirectional WebSocket for continuous gesture recognition
- **Client → Server**: Send landmark data arrays
- **Server → Client**: Receive prediction results

**Message Format (Client → Server)**:
```json
{
  "landmarks": [[x1,y1,z1], [x2,y2,z2], ...],
  "timestamp": 1234567890
}
```

**Message Format (Server → Client)**:
```json
{
  "prediction": "HELLO",
  "confidence": 0.87,
  "landmarks_detected": true,
  "timestamp": 1234567890
}
```

## Data Formats

### Hand Landmarks
- **Format**: Array of 21 points, each with [x, y, z] coordinates
- **Normalization**: Coordinates are normalized (0-1) relative to hand bounding box
- **Origin**: Usually palm center or wrist landmark

### Supported Gestures

#### Alphabet Letters (MLP Model)
- A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z

#### Common Words (PyTorch Model)
- hello, bye, yes, no, stop, peace, thankyou, love, up, down

## Error Responses

```json
{
  "error": "No hand detected",
  "code": 400
}
```

```json
{
  "error": "Invalid landmark format",
  "code": 422
}
```

## Rate Limits
- **Stream endpoint**: 30 FPS maximum
- **Predict endpoint**: 100 requests per second
- **WebSocket**: Real-time (no explicit limit)

## Authentication
Currently no authentication required (development mode).

## Examples

### Python Client
```python
import requests
import json

# Single prediction
landmarks = [[0.5, 0.3, 0.0] for _ in range(21)]  # Mock landmarks
response = requests.post('http://localhost:8000/predict',
                        json={'landmarks': landmarks})
print(response.json())
```

### JavaScript WebSocket Client
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/decode');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Prediction:', data.prediction);
};

// Send landmark data
const landmarks = Array(21).fill([0.5, 0.3, 0.0]);
ws.send(JSON.stringify({landmarks: landmarks}));
```

## Health Check
```bash
curl http://localhost:8000/health
# Response: {"status": "healthy", "models_loaded": ["mlp", "pytorch"]}
```</content>
<parameter name="filePath">c:\Users\medhu\Desktop\Work\SignLanguage\SignSpeak_MAin\docs\API.md