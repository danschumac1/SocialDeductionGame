import raylibpy as rl

from utils.constants import (
    BUTTON_HEIGHT, BUTTON_WIDTH, BUTTON_COLOR, HOVER_COLOR, TEXT_COLOR)

class Button:
    def __init__(
            self, x, y, width=BUTTON_WIDTH, 
            height=BUTTON_HEIGHT, text="", 
            color=BUTTON_COLOR, 
            hover_color=HOVER_COLOR, 
            text_color=TEXT_COLOR, action=None):
        """
        Initialize a Button instance.
        
        :param x: X-coordinate of the button
        :param y: Y-coordinate of the button
        :param width: Width of the button
        :param height: Height of the button
        :param text: Text to display on the button
        :param color: Default button color
        :param hover_color: Button color when hovered
        :param text_color: Text color
        :param action: Callable to execute when the button is clicked
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.action = action

    def is_hovered(self):
        """Check if the button is hovered."""
        mouse_pos = rl.get_mouse_position()
        return rl.check_collision_point_rec(
            mouse_pos, rl.Rectangle(self.x, self.y, self.width, self.height))

    def draw(self):
        """Draw the button, using hover color if hovered."""
        if self.is_hovered():
            rl.draw_rectangle(self.x, self.y, self.width, self.height, self.hover_color)
        else:
            rl.draw_rectangle(self.x, self.y, self.width, self.height, self.color)
        
        # Draw the text
        text_width = rl.measure_text(self.text, 30)
        rl.draw_text(
            self.text, 
            self.x + (self.width - text_width) // 2, 
            self.y + (self.height - 30) // 2, 30, 
            self.text_color
            )

    def click(self):
        """Execute the button's action if clicked."""
        if self.is_hovered() and rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON):
            if callable(self.action):
                self.action()

import raylibpy as rl

class Fillable:
    """
    A template for fillable fields.
    Displays the field name on the left and a text box on the right.
    Clicking the text box allows user input.
    """
    def __init__(self, x, y, field_name, width=200, height=30):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.field_name = field_name
        self.field_value = ""
        self.selected = False

    def is_mouse_over(self):
        """Check if the mouse is over the text field."""
        return rl.check_collision_point_rec(
            rl.get_mouse_position(), rl.Rectangle(self.x, self.y, self.width, self.height)
        )

    def handle_click(self):
        """Handle mouse clicks to toggle selection."""
        if rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON):
            self.selected = self.is_mouse_over()

    def handle_input(self):
        """Handle keyboard input when the field is selected."""
        if not self.selected:
            return

        key = rl.get_char_pressed()
        while key > 0:
            if key in (8, 127):  # Handle Backspace
                self.field_value = self.field_value[:-1]
            elif 32 <= key <= 126:  # Handle printable characters
                self.field_value += chr(key)
            key = rl.get_char_pressed()

    def draw(self):
        """Draw the fillable field and label."""
        self.handle_click()
        self.handle_input()
        label_x = self.x - 150  # Adjust label positioning
        rl.draw_text(self.field_name + ":", label_x, self.y + 5, 20, rl.DARKGRAY)

        box_color = rl.LIGHTGRAY if self.selected else rl.GRAY
        rl.draw_rectangle(self.x, self.y, self.width, self.height, box_color)
        rl.draw_text(self.field_value, self.x + 10, self.y + 5, 20, rl.BLACK)
