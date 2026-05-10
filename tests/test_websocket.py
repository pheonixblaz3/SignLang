#!/usr/bin/env python
"""Simple WebSocket test to verify connection works"""
import asyncio
import websockets
import json

async def test_websocket():
    """Test WebSocket connection"""
    uri = "ws://127.0.0.1:8000/ws/decode"
    print(f"Attempting to connect to {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print(f"✓ WebSocket connected to {uri}")
            
            # Wait for first message
            message = await asyncio.wait_for(websocket.recv(), timeout=3.0)
            data = json.loads(message)
            print(f"✓ Received message: {data}")
            
            return True
    except asyncio.TimeoutError:
        print("✗ No message received within 3 seconds")
        return False
    except Exception as e:
        print(f"✗ WebSocket error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_websocket())
    exit(0 if result else 1)
