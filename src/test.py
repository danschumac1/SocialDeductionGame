"""
@author: Dan Schumacher
TO RUN:
python ./src/test.py
"""
import raylibpy as rl
from utils.buttons_etc import Fillable

WIDTH = 1200
HEIGHT = 750

def initialize_window():
    rl.init_window(WIDTH, HEIGHT, "Carcassonne")
    rl.set_target_fps(60)

def main():
    """
    The main function initializes the game window and runs the game loop.
    """
    initialize_window()
    name_fillinable = Fillable(500, 100, "Name")
    hobby_fillinable = Fillable(500, 135, "Hobby")
    food_fillinable = Fillable(500, 170, "Food")
    anythingelse_fillable = Fillable(500, 205, "Tell us more!", 500, 500)
    fill_in = [name_fillinable, hobby_fillinable, food_fillinable, anythingelse_fillable]


    while not rl.window_should_close():
        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)  # Always clear at the start of each frame
        ###########################################################################
        # TEST CODE GOES HERE.
        for fillable in fill_in:
            fillable.draw()
        
        ###########################################################################
        rl.end_drawing()

    rl.close_window()

if __name__ == "__main__":
    main()
