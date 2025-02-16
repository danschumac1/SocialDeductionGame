import asyncio
import websockets

class WebSocketClient:
    """Handles WebSocket communication with the server."""

    def __init__(self, uri: str, client_id: str, on_message_callback):
        """
        Initialize WebSocket Client.

        :param uri: The WebSocket server address (e.g., "ws://localhost:8000/ws/{client_id}")
        :param client_id: Unique identifier for the client
        :param on_message_callback: Function to process received messages
        """
        self.uri = f"{uri}/{client_id}"
        self.client_id = client_id
        self.on_message_callback = on_message_callback
        self.websocket = None
        self.running = True

    async def connect(self):
        """Connect to the WebSocket server and listen for messages."""
        async with websockets.connect(self.uri) as ws:
            self.websocket = ws
            while self.running:
                try:
                    message = await ws.recv()
                    if self.on_message_callback:
                        self.on_message_callback(message)
                except websockets.exceptions.ConnectionClosed:
                    print("Connection closed")
                    break

    async def send_message(self, message: str):
        """Send a message to the server."""
        if self.websocket:
            await self.websocket.send(message)

    def stop(self):
        """Stop the WebSocket client."""
        self.running = False
