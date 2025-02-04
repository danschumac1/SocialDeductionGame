import abc
import time
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
    
    def return_value(self):
        """Return the button's text value."""
        return self.text

class ColorButton(Button):
    '''
    This button displays a selectable color option.
    - Only one color button can be active at a time.
    - Pressing a button will draw a black border around it to indicate selection.
    - The selected color will be stored and available for retrieval.
    '''
    selected_color = None  # Class variable to track the selected color globally

    def __init__(self, x, y, color, color_name, index):
        super().__init__(x, y, BUTTON_WIDTH, BUTTON_HEIGHT, text="", color=color, hover_color=color, text_color=rl.BLACK, action=self.select_color)
        self.color_value = color
        self.color_name = color_name
        self.index = index  # To differentiate buttons

    def select_color(self):
        """Sets the selected color globally."""
        ColorButton.selected_color = self.color_value

    def draw(self):
        """Draw the color button with a selection indicator."""
        super().draw()  # Draw the button itself
        rl.draw_text(self.color_name, self.x, self.y, 20, rl.BLACK)

        if ColorButton.selected_color == self.color_value:
            rl.draw_rectangle_lines(self.x, self.y, self.width, self.height, rl.BLACK)

    @staticmethod
    def get_selected_color():
        """Retrieve the currently selected color."""
        return ColorButton.selected_color

class Fillinable(abc.ABC):
    """
    A base class for fillable text fields.
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

    @abc.abstractmethod
    def handle_input(self):
        """Handle keyboard input when the field is selected."""
        pass

    @abc.abstractmethod
    def draw(self):
        """Draw the fillable field and label."""
        pass

class SimpleFillinable(Fillinable):
    """A basic single-line text field that does not wrap text."""
    def __init__(self, x, y, field_name, width=200, height=30):
        super().__init__(x, y, field_name, width, height)
        self.last_backspace_time = 0

    def handle_input(self):
        """Handle keyboard input when the field is selected."""
        if not self.selected:
            return

        # Handle continuous backspace pressing
        if rl.is_key_down(rl.KEY_BACKSPACE) and len(self.field_value) > 0:
            self.field_value = self.field_value[:-1]
            current_time = time.time()
            if current_time - self.last_backspace_time > 0.1:  # 100ms delay
                self.field_value = self.field_value[:-1]
                self.last_backspace_time = current_time 


        key = rl.get_char_pressed()
        while key > 0:
            if 32 <= key <= 126 and rl.measure_text(self.field_value + chr(key), 20) < self.width - 10:
                self.field_value += chr(key)
            key = rl.get_char_pressed()

    def draw(self):
        """Draw the fillable field and label."""
        self.handle_click()
        self.handle_input()
        label_x = self.x - 150  # Adjust label positioning
        rl.draw_text(f"{self.field_name}:", label_x, self.y + 5, 20, rl.DARKGRAY)

        box_color = rl.LIGHTGRAY if self.selected else rl.GRAY
        rl.draw_rectangle(self.x, self.y, self.width, self.height, box_color)
        rl.draw_text(self.field_value, self.x + 10, self.y + 5, 20, rl.BLACK)

class WrapFillinable(Fillinable):
    def __init__(self, x, y, field_name, width=200, height=60):
        super().__init__(x, y, field_name, width, height)
        self.last_backspace_time = 0  # Track the last time backspace was pressed

    def handle_input(self):
        """Handle keyboard input when the field is selected, wrapping text if needed."""
        if not self.selected:
            return

        # Handle Backspace with proper delay
        if rl.is_key_down(rl.KEY_BACKSPACE) and len(self.field_value) > 0:
            current_time = time.time()
            if current_time - self.last_backspace_time > 0.1:  # 100ms delay
                self.field_value = self.field_value[:-1]
                self.last_backspace_time = current_time  # Update last backspace time

        # Handle normal character input
        key = rl.get_char_pressed()
        while key > 0:
            if 32 <= key <= 126:
                # Simulate adding the character to check text width
                lines = self.field_value.split("\n")
                current_line = lines[-1] if lines else ""
                test_value = current_line + chr(key)
                text_width = rl.measure_text(test_value, 20)

                # If the text width exceeds the box, wrap it to a new line
                if text_width >= self.width - 10:
                    self.field_value += "\n"

                self.field_value += chr(key)
            key = rl.get_char_pressed()


    def draw(self):
        """Draw the multi-line fillable field and label with text wrapping."""
        self.handle_click()
        self.handle_input()
        label_x = self.x - 150  # Adjust label positioning
        rl.draw_text(f"{self.field_name}:", label_x, self.y + 5, 20, rl.DARKGRAY)

        box_color = rl.LIGHTGRAY if self.selected else rl.GRAY
        rl.draw_rectangle(self.x, self.y, self.width, self.height, box_color)

        # Draw wrapped text
        lines = self.field_value.split("\n")
        for i, line in enumerate(lines):
            rl.draw_text(line, self.x + 10, self.y + 5 + (i * 20), 20, rl.BLACK)

class ChatWindow:
    """A simple chat window where players can type and send messages."""
    
    def __init__(self, x, y, width=400, height=200, max_messages=10):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.input_text = ""
        self.messages = []
        self.max_messages = max_messages
        self.selected = False  # If the input field is active
        self.last_backspace_time = 0  # Track backspace timing
        
        # Submit button using the existing Button class
        self.submit_button = Button(
            x=self.x + self.width + 10,
            y=self.y + self.height,
            width=60,
            height=30,
            text="SEND",
            color=rl.DARKGRAY,
            hover_color=rl.GRAY,
            text_color=rl.WHITE,
            action=self.submit_message
        )

    def is_mouse_over_input(self):
        """Check if the mouse is over the input box."""
        return rl.check_collision_point_rec(
            rl.get_mouse_position(), rl.Rectangle(self.x, self.y + self.height, self.width, 30)
        )

    def handle_click(self):
        """Handle mouse clicks to activate the input box."""
        if rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON):
            self.selected = self.is_mouse_over_input()

    def handle_input(self):
        """Handle keyboard input when the input field is selected."""
        if not self.selected:
            return

        # Handle continuous backspace pressing
        if rl.is_key_down(rl.KEY_BACKSPACE) and len(self.input_text) > 0:
            current_time = time.time()
            if current_time - self.last_backspace_time > 0.1:  # 100ms delay
                self.input_text = self.input_text[:-1]
                self.last_backspace_time = current_time

        key = rl.get_char_pressed()
        while key > 0:
            if 32 <= key <= 126:  # Printable characters
                self.input_text += chr(key)
            key = rl.get_char_pressed()

        # Submit message when Enter is pressed
        if rl.is_key_pressed(rl.KEY_ENTER) and self.input_text.strip():
            self.submit_message()

    def submit_message(self):
        """Submit the current message and clear input."""
        self.messages.append(self.input_text.strip())  
        self.input_text = ""  # Clear input box
        
        # Limit the message list size
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)

    def draw(self):
        """Draw the chat window and input box."""
        self.handle_click()
        self.handle_input()

        # Draw the chat history
        chat_bg_color = rl.LIGHTGRAY
        rl.draw_rectangle(self.x, self.y, self.width, self.height, chat_bg_color)

        for i, msg in enumerate(reversed(self.messages)):
            rl.draw_text(msg, self.x + 5, self.y + self.height - (i + 1) * 20 - 10, 20, rl.BLACK)

        # Draw the input box
        input_color = rl.DARKGRAY if self.selected else rl.GRAY
        rl.draw_rectangle(self.x, self.y + self.height, self.width, 30, input_color)
        rl.draw_text(self.input_text, self.x + 5, self.y + self.height + 5, 20, rl.WHITE)

        # Draw and handle the submit button
        self.submit_button.draw()
        self.submit_button.click()