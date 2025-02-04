import raylibpy as rl
from utils.enums import GameState
from utils.buttons_etc import ChatWindow
from utils.constants import WIDTH, HEIGHT

gs = GameState.PLAY
cw = ChatWindow(0, 0, width=WIDTH - (WIDTH // 3), height=HEIGHT - (HEIGHT//10))  # Instantiate ChatWindow

def play_game(gs):
    while gs == GameState.PLAY:
        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)

        # Draw game text
        rl.draw_text("Game Screen", 20, 20, 40, rl.MAROON)

        # Draw and update the chat window
        cw.draw()  # Corrected method call

        rl.end_drawing()

    return gs
