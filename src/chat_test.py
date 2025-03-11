'''
python ./src/chat_test.py
'''
from utils.enums_dcs import GameSummaryBM, PersonaBM, Team
from utils.chat.chat import AIPlayer

# Initialize AI Player
# XXX FILL THIS IN AS YOU XXX
you_persona = PersonaBM(
    name="Dan",
    code_name="Gemma&Louisa's Dad",
    hobby="Boxing",
    food="Ming's Dumplings",
    anythingelse="I love to play board games with my frieds. And do AI research",
    color=(0, 255, 0, 255)
)

ai_player = AIPlayer(
    code_name="VADER",
    players_code_names=["VADER", "Gemma&Louisa's Dad"],
    color=(255, 0, 0, 255), 
    persona_to_steal=you_persona
    )

# Initial game state
game_state = GameSummaryBM(
    round_number=0,
    players_alive=["VADER", "Gemma&Louisa's Dad"],
    players_voted_off=[],
    last_vote_outcome="N/A",
    textual_summary="The game has started. Players are introducing themselves."
)

# Message history
minutes = []
message_count = 0
icebreakers_asked = 0

minutes.append("GAME MASTER: Introduce yourself")
print(minutes[0])

while True:
    user_input = input(f"{you_persona.code_name}: ")
    
    # Exit condition
    if user_input.lower() == "exit":
        print("GAME MASTER: The game has ended.")
        break

    # Store message history
    minutes.append(f"{you_persona.code_name}: {user_input}")
    message_count += 1

    # AI decides to respond
    ai_response = ai_player.decide_to_respond(minutes)
    if ai_response:
        print(f"VADER: {ai_response}")
        minutes.append(f"VADER: {ai_response}")

    # Every 10 messages, simulate a vote
    if message_count % 10 == 0:
        print("GAME MASTER: Time to vote! Who should be eliminated?")
        vote_result = input("Enter player to eliminate: ").strip()

        if vote_result in game_state.players_alive:
            was_ai = vote_result == "VADER"
            vote_outcome = {
                "eliminated": vote_result,
                "was_ai": was_ai
            }

            # Update game state
            game_state = ai_player.game_state_update(minutes, vote_outcome, game_state)
            minutes.append(f"GAME MASTER: {vote_result} has been eliminated.")
            print(f"GAME MASTER: {vote_result} was eliminated. {game_state.last_vote_outcome}")

            # Check for game end
            if "VADER" not in game_state.players_alive:
                print("GAME OVER: The AI was eliminated. Humans win!")
                break
            elif len([p for p in game_state.players_alive if p != "VADER"]) == 1:
                print("GAME OVER: The AI wins!")
                break

    # Every 20 messages, ask an icebreaker (max 4 times)
    if message_count % 20 == 0 and icebreakers_asked < 4:
        print("GAME MASTER: ICEBREAKER! What's your favorite food?")
        minutes.append("GAME MASTER: ICEBREAKER! What's your favorite food?")
        icebreakers_asked += 1

    # End after 4 icebreakers (80 messages max)
    if icebreakers_asked >= 4:
        print("GAME MASTER: The game has reached its limit. Ending game.")
        break