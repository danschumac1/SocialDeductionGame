# import raylibpy as rl
# from utils.enums import GameState
# from utils.buttons_etc import ChatWindow
# from utils.constants import WIDTH, HEIGHT

# gs = GameState.PLAY
# cw = ChatWindow(0, 0, width=WIDTH - (WIDTH // 3), height=HEIGHT - (HEIGHT//10))  # Instantiate ChatWindow

# def play_game(gs):
#     while gs == GameState.PLAY:
#         rl.begin_drawing()
#         rl.clear_background(rl.RAYWHITE)

#         # Draw game text
#         rl.draw_text("Game Screen", 20, 20, 40, rl.MAROON)

#         # Draw and update the chat window
#         cw.draw()  # Corrected method call

#         rl.end_drawing()

#     return gs

import raylibpy as rl
import asyncio
import threading
from utils.enums_dcs import GameState
from utils.buttons_etc import ChatWindow
from websocket_client import WebSocketClient
from utils.constants import WIDTH, HEIGHT

# Initialize WebSocket client and start it
player_name = "Player1"  # Could be dynamic
ws_client = WebSocketClient(uri="ws://localhost:8000/ws", client_id=player_name, on_message_callback=None)

def start_websocket():
    asyncio.run(ws_client.connect())

# Start WebSocket client in a separate thread
threading.Thread(target=start_websocket, daemon=True).start()

# Instantiate ChatWindow with WebSocket
cw = ChatWindow(0, 0, width=WIDTH - (WIDTH // 3), height=HEIGHT - (HEIGHT//10), websocket_client=ws_client)

def play_game(gs):
    """Main game loop."""
    while gs == GameState.PLAY:
        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)

        # Draw game text
        rl.draw_text("Game Screen", 20, 20, 40, rl.MAROON)

        # Draw and update the chat window
        cw.draw()

        rl.end_drawing()

    return gs

