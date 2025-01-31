import raylibpy as rl
from utils.constants import WIDTH, HEIGHT
from utils.enums import GameState

# Placeholder for user input storage
user_data = {
    "name": "",
    "avatar": 0,
    "hobbies": "",
    "favorite_teacher": "",
    "pets": ""
}

avatars = ["A", "B", "C"]  # Example avatars
selected_avatar = 0
selected_field = "name"  # Track which field is selected

# Define text field positions
text_fields = {
    "name": (250, 100),
    "hobbies": (250, 350),
    "favorite_teacher": (250, 400),
    "pets": (250, 450)
}

def is_mouse_over_field(field):
    """Check if the mouse is over a text field."""
    x, y = text_fields[field]
    return rl.check_collision_point_rec(rl.get_mouse_position(), rl.Rectangle(x, y, 200, 30))

def setup_game(game_state):
    """
    Handles the setup screen where the player selects an avatar,
    enters their name, and fills in additional information.
    """
    global selected_avatar, selected_field

    # Display instructions
    rl.draw_text("Setup Screen", WIDTH // 2 - 100, 20, 30, rl.BLACK)
    rl.draw_text("Enter your name:", 50, 100, 20, rl.DARKGRAY)
    rl.draw_text("Select your avatar:", 50, 200, 20, rl.DARKGRAY)
    rl.draw_text("Fill in the following:", 50, 300, 20, rl.DARKGRAY)
    
    # Render input fields
    for field, (x, y) in text_fields.items():
        color = rl.LIGHTGRAY if selected_field == field else rl.GRAY
        rl.draw_rectangle(x, y, 200, 30, color)
        rl.draw_text(user_data[field], x + 10, y + 5, 20, rl.BLACK)
    
    # Render avatar selection
    rl.draw_text(f"{avatars[selected_avatar]}", 250, 200, 20, rl.BLACK)
    rl.draw_text("<", 220, 200, 20, rl.BLACK)
    rl.draw_text(">", 400, 200, 20, rl.BLACK)
    
    # Detect mouse clicks to select input fields
    if rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON):
        for field in text_fields:
            if is_mouse_over_field(field):
                selected_field = field
    
    # Handle user input for selected field
    key = rl.get_char_pressed()
    while key > 0:
        if key in (8, 127):  # Backspace/Delete key handling
            user_data[selected_field] = user_data[selected_field][:-1]
        elif 32 <= key <= 126 and len(user_data[selected_field]) < 15:  # Printable ASCII range
            user_data[selected_field] += chr(key)
        key = rl.get_char_pressed()
    
    # Avatar selection
    if rl.is_key_pressed(rl.KEY_LEFT):
        selected_avatar = (selected_avatar - 1) % len(avatars)
    if rl.is_key_pressed(rl.KEY_RIGHT):
        selected_avatar = (selected_avatar + 1) % len(avatars)
    
    # Proceed to next screen (GameState.PLAY) when Enter is pressed
    if rl.is_key_pressed(rl.KEY_ENTER) and user_data["name"]:
        return GameState.PLAY
    
    return game_state
