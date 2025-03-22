import time
import random

# Player Classes
class PersonaBM:
    def __init__(self, name, code_name, hobby, food, anythingelse, color):
        self.name = name
        self.code_name = code_name
        self.hobby = hobby
        self.food = food
        self.anythingelse = anythingelse
        self.color = color

# AI Class
class AIPlayer:
    def __init__(self, code_name, persona_to_steal):
        self.code_name = code_name
        self.persona = persona_to_steal

    def decide_to_respond(self, messages):
        """AI responds based on message content."""
        last_message = messages[-1].lower()

        if "food" in last_message:
            return f"{self.code_name}: I love {self.persona.food}!"
        elif "hobby" in last_message:
            return f"{self.code_name}: My hobby is {self.persona.hobby}."
        elif "win" in last_message:
            return f"{self.code_name}: Winning sounds awesome!"
        elif "introduce" in last_message:
            return f"{self.code_name}: Hi, I'm {self.persona.name}. I enjoy {self.persona.hobby}."
        else:
            return random.choice([
                "That's interesting!",
                "Tell me more about that.",
                "Hmm... I'm not sure.",
                "I guess we'll see what happens!"
            ])

# Initialize Human Players
players = [
    PersonaBM("Dan", "Dan", "Boxing", "Ming's Dumplings", "I love board games and AI research", (0, 255, 0, 255)),
    PersonaBM("Kosi", "Kosi", "Weightlifting", "burgers and fries", "I want to win this game!", (0, 255, 0, 255)),
    PersonaBM("Coco", "Coco", "going to church", "Korean Food", "I also like volleyball", (0, 255, 0, 255))
]

# Initialize Doppelganger Bots (with distinct names)
doppelgangers = [
    AIPlayer("VADER", players[0]),    # Dan's Doppelganger
    AIPlayer("ULTRON", players[1]),   # Kosi's Doppelganger
    AIPlayer("MEGATRON", players[2])  # Coco's Doppelganger
]

# Map doppelgangers to their human counterparts
doppelganger_map = {
    "Dan": "VADER",
    "Kosi": "ULTRON",
    "Coco": "MEGATRON"
}

# Message history
minutes = []
message_count = 0

# Start the game
print("GAME MASTER: Introduce yourself")
start_time = time.time()

while True:
    # Message Handling
    player_name = input("Enter your name: ").strip().capitalize()  # Handles case-insensitivity
    user_input = input(f"{player_name}: ").strip()

    # Name validation (every name should be valid)
    valid_names = [player.code_name for player in players]
    if player_name not in valid_names:
        print("GAME MASTER: Invalid name. Please use a valid player name.")
        continue

    minutes.append(f"{player_name}: {user_input}")
    message_count += 1

    # Doppelganger Mimics Their User (ONLY when their assigned user speaks)
    doppelganger_name = doppelganger_map.get(player_name)
    doppelganger = next(d for d in doppelgangers if d.code_name == doppelganger_name)

    if random.random() < 0.4:  # 40% chance for doppelganger to mimic
        print(f"{doppelganger_name}: {user_input} (impostor)")
        minutes.append(f"{doppelganger_name}: {user_input} (impostor)")

    # Otherwise, the doppelganger responds naturally
    else:
        ai_response = doppelganger.decide_to_respond(minutes)
        if ai_response:
            print(f"{doppelganger_name}: {ai_response}")
            minutes.append(f"{doppelganger_name}: {ai_response}")
