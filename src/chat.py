import time
import random
from utils.enums_dcs import GameSummaryBM, PersonaBM, Team
from utils.chat.chat import AIPlayer

# Initialize Human Players
players = [
    PersonaBM(name="Dan", code_name="Gemma&Louisa's Dad", hobby="Boxing", food="Ming's Dumplings",
              anythingelse="I love to play board games with my friends. And do AI research", color=(0, 255, 0, 255)),
    PersonaBM(name="Kosi", code_name="notKosi", hobby="Weightlifting", food="burgers and fries",
              anythingelse="I want to win this game!", color=(0, 255, 0, 255)),
    PersonaBM(name="Coco", code_name="cocobutter", hobby="going to church", food="Korean Food",
              anythingelse="I also like to play volleyball", color=(0, 255, 0, 255))
]

# Initialize AI Players
ai_players = [
    AIPlayer(code_name="VADER", players_code_names=["Gemma&Louisa's Dad", "notKosi", "cocobutter"],
             color=(255, 0, 0, 255), persona_to_steal=random.choice(players)),

    AIPlayer(code_name="ULTRON", players_code_names=["Gemma&Louisa's Dad", "notKosi", "cocobutter"],
             color=(0, 0, 255, 255), persona_to_steal=random.choice(players)),

    AIPlayer(code_name="MEGATRON", players_code_names=["Gemma&Louisa's Dad", "notKosi", "cocobutter"],
             color=(255, 255, 0, 255), persona_to_steal=random.choice(players))
]

# Initial game state
game_state = GameSummaryBM(
    round_number=0,
    players_alive=["Gemma&Louisa's Dad", "notKosi", "cocobutter", "VADER", "ULTRON", "MEGATRON"],
    players_voted_off=[],
    last_vote_outcome="N/A",
    textual_summary="The game has started. Players are introducing themselves."
)

# Message history and icebreaker tracking
minutes = []
message_count = 0
icebreakers_asked = 0
icebreakers = [
    "Introduce yourself!",
    "What's your favorite food?",
    "What would you do with $1 million?",
    "What's your dream vacation?"
]
random.shuffle(icebreakers)

# Start the game
minutes.append("GAME MASTER: Introduce yourself")
print(minutes[0])
start_time = time.time()
last_vote_time = start_time  # Track time for voting phase

while True:
    # Message Handling
    current_player = random.choice(players).code_name
    user_input = input(f"{current_player}: ")
    
    if user_input.lower() == "exit":
        print("GAME MASTER: The game has ended.")
        break

    minutes.append(f"{current_player}: {user_input}")
    message_count += 1

    # AI Responses
    for ai_player in ai_players:
        ai_response = ai_player.decide_to_respond(minutes)
        if ai_response:
            print(f"{ai_player.code_name}: {ai_response}")
            minutes.append(f"{ai_player.code_name}: {ai_response}")

    # Icebreaker every 60 seconds
    if time.time() - start_time > 60 and icebreakers_asked < 4:
        new_icebreaker = icebreakers[icebreakers_asked]
        print(f"GAME MASTER: ICEBREAKER! {new_icebreaker}")
        minutes.append(f"GAME MASTER: ICEBREAKER! {new_icebreaker}")
        icebreakers_asked += 1
        start_time = time.time()

    # Voting Phase every 2 minutes
    if time.time() - last_vote_time >= 120:  # 2 minutes = 120 seconds
        print("GAME MASTER: Time to vote! Who should be eliminated?")
        vote_result = input("Enter player to eliminate: ").strip()

        if vote_result in game_state.players_alive:
            print("\nGAME MASTER: The player with the most votes is...")
            time.sleep(2)  # Adds suspense
            print(f"🟢 {vote_result} was eliminated! 🟢")

            was_ai = vote_result in ["VADER", "ULTRON", "MEGATRON"]
            vote_outcome = {
                "eliminated": vote_result,
                "was_ai": was_ai
            }

            # Update Game State
            for ai_player in ai_players:
                game_state = ai_player.game_state_update(minutes, vote_outcome, game_state)

            minutes.append(f"GAME MASTER: {vote_result} has been eliminated.")

            # Win Conditions
            alive_ai_players = [p for p in game_state.players_alive if p in ["VADER", "ULTRON", "MEGATRON"]]
            alive_human_players = [p for p in game_state.players_alive if p not in ["VADER", "ULTRON", "MEGATRON"]]

            if not alive_ai_players:
                print("GAME OVER: All AI players were eliminated. Humans win! 🎉")
                break
            elif len(alive_human_players) == 1:
                print("GAME OVER: The AI wins!! 💀")
                break

        # Reset vote timer
        last_vote_time = time.time()

    # End Condition: 4 Icebreakers or 80 messages
    if icebreakers_asked >= 4 or message_count >= 80:
        print("GAME MASTER: The game has reached its limit. Ending game.")
        break

print("GAME MASTER: Thanks for playing!")
