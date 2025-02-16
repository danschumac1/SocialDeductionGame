from fastapi import FastAPI, WebSocket
import asyncio

app = FastAPI()
connected_users = {}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """Handles WebSocket connections and broadcasts messages."""
    await websocket.accept()
    connected_users[client_id] = websocket
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Message from {client_id}: {data}")

            # Broadcast message to all connected users
            for user, ws in connected_users.items():
                if user != client_id:
                    await ws.send_text(f"{client_id}: {data}")
    except:
        del connected_users[client_id]

# Run with Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
