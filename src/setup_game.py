from dataclasses import dataclass
import json
import raylibpy as rl
from utils.buttons_etc import Button, SimpleFillinable, WrapFillinable
from utils.constants import BUTTON_WIDTH, WIDTH, HEIGHT
from utils.enums import GameState

class PlayerInfoHandler:
    def __init__ (
            self, name_fillinable, hobby_fillinable, food_fillinable, 
            anythingelse_fillinable):
        self.name_fillinable = name_fillinable
        self.hobby_fillinable = hobby_fillinable
        self.food_fillinable = food_fillinable
        self.anythingelse_fillinable = anythingelse_fillinable
        
    def construct_json(self):
        json_obj = {
            "name":         self.name_fillinable.field_value,
            "hobby":        self.hobby_fillinable.field_value,
            "food":         self.food_fillinable.field_value,
            "anythingelse": self.anythingelse_fillinable.field_value
        }
        with open(f"./data/{json_obj['name']}_player_info.json", "w") as f:
            json.dump(json_obj, f)
    
    def draw(self):
        self.name_fillinable.draw()
        self.hobby_fillinable.draw()
        self.food_fillinable.draw()
        self.anythingelse_fillinable.draw()
        
def setup_game(gs):
    """
    Handles the setup screen where the player selects an avatar,
    enters their name, and fills in additional information.
    """
    name_fillinable = SimpleFillinable(500, 100, "Name")
    hobby_fillinable = SimpleFillinable(500, 135, "Hobby")
    food_fillinable = SimpleFillinable(500, 170, "Food")
    anythingelse_fillinable = WrapFillinable(500, 205, "Tell us more!", 500, 500)

    pih = PlayerInfoHandler(
        name_fillinable, hobby_fillinable, food_fillinable, anythingelse_fillinable
    )

    def continue_action():
        nonlocal gs
        pih.construct_json()
        gs = GameState.PLAY  # Switch to play state
        print("Switching to play state...")

    continue_button = Button(
        x=(WIDTH - BUTTON_WIDTH) // 4, 
        y=HEIGHT - 60, 
        text="CONTINUE", 
        action=continue_action  # Assign the function reference correctly
    )

    while gs == GameState.SETUP:
        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)
        
        pih.draw()  # Draw Fillinables properly
        
        continue_button.draw()
        continue_button.click()

        rl.end_drawing()

    return gs
