import raylibpy as rl
from utils.buttons_etc import Button, Fillable
from utils.constants import BUTTON_WIDTH, WIDTH, HEIGHT
from utils.enums import GameState
name_fillinable = Fillable(500, 100, "Name")
hobby_fillinable = Fillable(500, 135, "Hobby")
food_fillinable = Fillable(500, 170, "Food")
anythingelse_fillable = Fillable(500, 205, "Tell us more!", 500, 500)
fillable_fields = [
    name_fillinable, hobby_fillinable, food_fillinable, anythingelse_fillable]


def setup_game(gs):
    """
    Handles the setup screen where the player selects an avatar,
    enters their name, and fills in additional information.
    """
    name_fillinable = Fillable(500, 100, "Name")
    hobby_fillinable = Fillable(500, 135, "Hobby")
    food_fillinable = Fillable(500, 170, "Food")
    anythingelse_fillable = Fillable(500, 205, "Tell us more!", 500, 500)
    fillable_fields = [
        name_fillinable, hobby_fillinable, food_fillinable, anythingelse_fillable]
    
    def continue_action():
        nonlocal gs
        gs = GameState.PLAY  # When the playbutton is clicked, switch to setup state
        print("Switching to play state...")

    continue_button = Button(
        x=(WIDTH - BUTTON_WIDTH) // 4, 
        y=HEIGHT - 60, 
        text="CONTINUE", 
        action=continue_action)
    
    while gs == GameState.SETUP:
        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)
        for fillable in fillable_fields:
            fillable.draw()
        continue_button.draw()
        continue_button.click()
        rl.end_drawing()
        
    return gs
