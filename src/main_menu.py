import raylibpy as rl
from utils.buttons_etc import Button
from utils.constants import (
    HEIGHT, WIDTH, BUTTON_WIDTH)
from utils.enums import GameState

def main_menu(gs):
    """
    Handles the main menu logic.
    Draws the menu and allows the user to select "Play" or "Quit."
    """
    def play_action():
        nonlocal gs
        gs = GameState.SETUP  # When the playbutton is clicked, switch to setup state
        print("Switching to play state...")

    def quit_action():
        nonlocal gs
        gs = GameState.QUIT  # Exit the game
        print("Exiting game...")

    play_button = Button(
        x=(WIDTH - BUTTON_WIDTH) // 2, 
        y=HEIGHT // 2 - 60, 
        text="PLAY", 
        action=play_action)
    
    quit_button = Button(
        x=(WIDTH - BUTTON_WIDTH) // 2, 
        y=HEIGHT // 2 + 10, 
        text="QUIT", 
        action=quit_action)
    
    # Draw main menu elements
    rl.draw_text("ROBOT ATTACK", WIDTH // 2 - 200, 100, 50, rl.DARKGREEN)

    # Draw and handle buttons
    play_button.draw()
    play_button.click()

    quit_button.draw()
    quit_button.click()

    return gs