from dataclasses import dataclass
import json
import raylibpy as rl
from utils.buttons_etc import Button, ColorButton, SimpleFillinable, WrapFillinable
from utils.constants import BUTTON_WIDTH, PLAYER_COLORS, WIDTH, HEIGHT
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
    name_fillinable = SimpleFillinable(WIDTH//2, 100, "Name")
    hobby_fillinable = SimpleFillinable(WIDTH//2, 135, "Hobby")
    food_fillinable = SimpleFillinable(WIDTH//2, 170, "Food")
    anythingelse_fillinable = WrapFillinable(WIDTH//2, 205, "Tell us more!", 500, 500)

    color_codes = [color for color, _ in PLAYER_COLORS]
    color_names = [name for _, name in PLAYER_COLORS]

    color_buttons = [
        ColorButton(WIDTH//5 + i * (BUTTON_WIDTH + 10), HEIGHT//15, color_code, color_name, i)
        for i, (color_name, color_code) in enumerate(zip(color_names, color_codes))
    ]

    pih = PlayerInfoHandler(
        name_fillinable, hobby_fillinable, food_fillinable, anythingelse_fillinable
    )

    def continue_action():
        nonlocal gs
        selected_color = ColorButton.get_selected_color()
        if selected_color:
            json_obj = {
                "name":         name_fillinable.field_value,
                "hobby":        hobby_fillinable.field_value,
                "food":         food_fillinable.field_value,
                "anythingelse": anythingelse_fillinable.field_value,
                "color":        (selected_color.r, selected_color.g, selected_color.b)  # Store RGB values
            }
            with open(f"./data/{json_obj['name']}_player_info.json", "w") as f:
                json.dump(json_obj, f)

            gs = GameState.PLAY  # Switch to play state
            print("Switching to play state...")
        else:
            print("Please select a color before continuing.")

    continue_button = Button(
        x=(WIDTH - BUTTON_WIDTH) // 4, 
        y=HEIGHT - 60, 
        text="CONTINUE", 
        action=continue_action
    )

    while gs == GameState.SETUP:
        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)
        
        # Draw fill-in fields
        pih.draw()

        # Draw color selection buttons
        for button in color_buttons:
            button.draw()
            button.click()

        continue_button.draw()
        continue_button.click()

        rl.end_drawing()

    return gs
