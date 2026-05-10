"""WebSocket connection manager."""

from typing import Set, Optional
import asyncio
from fastapi import WebSocket
from src.core.logger import get_logger

logger = get_logger(__name__)


class WebSocketManager:
    """Manage active WebSocket connections."""

    def __init__(self):
        """Initialize WebSocket manager."""
        self.active_connections: Set[WebSocket] = set()
        self.lock = asyncio.Lock()

    async def add_connection(self, websocket: WebSocket) -> None:
        """
        Add a new WebSocket connection.

        Args:
            websocket: WebSocket connection
        """
        async with self.lock:
            self.active_connections.add(websocket)
            logger.debug(f"Connection added. Total: {len(self.active_connections)}")

    async def remove_connection(self, websocket: WebSocket) -> None:
        """
        Remove a WebSocket connection.

        Args:
            websocket: WebSocket connection
        """
        async with self.lock:
            self.active_connections.discard(websocket)
            logger.debug(f"Connection removed. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict) -> None:
        """
        Broadcast message to all connected clients.

        Args:
            message: Message to broadcast
        """
        async with self.lock:
            disconnected = []
            for connection in self.active_connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.warning(f"Failed to send message to connection: {e}")
                    disconnected.append(connection)

            # Remove disconnected connections
            for connection in disconnected:
                self.active_connections.discard(connection)

    def get_connection_count(self) -> int:
        """Get number of active connections."""
        return len(self.active_connections)

    async def disconnect_all(self) -> None:
        """Disconnect all active connections."""
        async with self.lock:
            for connection in self.active_connections:
                try:
                    await connection.close()
                except Exception as e:
                    logger.warning(f"Error closing connection: {e}")
            self.active_connections.clear()
            logger.info("All connections disconnected")
