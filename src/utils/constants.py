import raylibpy as rl

WIDTH = 1200
HEIGHT = 750
PADDING = HEIGHT // 25

# BUTTONS
BUTTON_WIDTH = WIDTH // 10
BUTTON_HEIGHT = HEIGHT // 20
BUTTON_COLOR = rl.LIGHTGRAY
HOVER_COLOR = rl.GRAY
TEXT_COLOR = rl.DARKGRAY

COLOR_1 = rl.Color(0, 114, 178, 255)  # Blue
COLOR_2 = rl.Color(230, 159, 0, 255)  # Orange
COLOR_3 = rl.Color(86, 180, 233, 255) # Sky Blue
COLOR_4 = rl.Color(0, 158, 115, 255)  # Teal/Green
COLOR_5 = rl.Color(204, 121, 167, 255) # Pink/Magenta

PLAYER_COLORS = (
    (COLOR_1, "Blue"), (COLOR_2, "Orange"), 
    (COLOR_3, "Light Blue"), (COLOR_4, "Green"), (COLOR_5, "Pink"))