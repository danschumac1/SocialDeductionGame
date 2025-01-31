"""
Created on 01/18/2025

@author: Dan
TO RUN:
python ./src/main.py
"""

from enum import Enum
import raylibpy as rl
from main_menu import main_menu
from utils.constants import WIDTH, HEIGHT
from game import play_game
from setup_game import setup_game
from utils.enums import GameState

def initialize_window():
    rl.init_window(WIDTH, HEIGHT, "Carcassonne")
    rl.set_target_fps(60)

def main():
    """
    The main function initializes the game window and runs the game loop.
    """
    initialize_window()

    state_handler = {
        GameState.MAIN_MENU: main_menu,
        GameState.SETUP: setup_game,
        GameState.PLAY: play_game,
    }

    gs = GameState.MAIN_MENU

    while not rl.window_should_close():
        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)  # Always clear at the start of each frame

        if gs in state_handler:
            next_state = state_handler[gs](gs)
            if next_state != gs:
                gs = next_state  # Switch state only if changed
        else:
            print("Invalid game state")
            break

        rl.end_drawing()

    rl.close_window()

if __name__ == "__main__":
    main()
