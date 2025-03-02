from utils.chat.chat import AIPlayer
from utils.enums_dcs import GameSummaryBM, PersonaBM
import random

def main():
    # Setup Human Personas
    bob = PersonaBM(name="Bob B.", code_name="Mario", color=(255, 0, 0, 255), hobby="fishing", food="pizza", anythingelse="I like video games.")
    alice = PersonaBM(name="Alice A.", code_name="Samus Aran", color=(255, 165, 0, 255), hobby="swimming", food="sushi", anythingelse="I like to read books.")
    you = PersonaBM(name="You", code_name="Fox McCloud", color=(0, 0, 255, 255), hobby="playing soccer", food="hamburgers", anythingelse="I like AI games.")

    # Setup AI Imposters
    ai_bob = AIPlayer(code_name="Luigi", color=(0, 255, 0, 255), persona_to_steal=bob)
    ai_alice = AIPlayer(code_name="Princess Peach", color=(255, 192, 203, 255), persona_to_steal=alice)
    ai_you = AIPlayer(code_name="Donkey Kong", color=(165, 42, 42, 255), persona_to_steal=you)

    human_code_names = [bob.code_name, alice.code_name, you.code_name]
    ai_code_names = [ai_bob.code_name, ai_alice.code_name, ai_you.code_name]

    for ai in [ai_bob, ai_alice, ai_you]:
        ai.initialize_prompt_tail(human_code_names, ai_code_names)
        ai.initialize_system_prompt(human_code_names, ai_code_names)

    # Start Game
    minutes = [
        "Mario: Hi everyone, this is Bob.",
        "Samus Aran: Hello, this is Alice."
    ]

    print("\n=== Round 1: Introductions ===")
    your_intro = input("You (Fox McCloud), introduce yourself: ")
    minutes.append(f"Fox McCloud: {your_intro}")

    # Force all AIs to introduce themselves (they don’t need to wait to be addressed)
    for ai in [ai_bob, ai_alice, ai_you]:
        intro = ai.introduce(minutes)
        minutes.append(f"{ai.code_name}: {intro}")
        print(f"{ai.code_name}: {intro}")

    # Main Game Loop (Rounds 2 and 3)
    for round_num in range(2, 4):
        print(f"\n=== Round {round_num}: Discussion and Voting ===")

        # Human player input
        human_response = input(f"Your turn (Fox McCloud): ")
        minutes.append(f"Fox McCloud: {human_response}")

        # Give every AI a chance to respond *proactively*, not just if directly addressed
        for ai in [ai_bob, ai_alice, ai_you]:
            decision = ai.decide_to_respond(minutes)

            if "Wait for next message" not in decision:
                action_response = ai.choose_action(minutes)
                minutes.append(f"{ai.code_name}: {action_response}")
                print(f"{ai.code_name}: {action_response}")
            else:
                # Fallback action: if AI doesn't want to respond, ask a random question anyway
                action_response = ai.question(minutes)
                minutes.append(f"{ai.code_name}: {action_response}")
                print(f"{ai.code_name}: {action_response}")

        # Voting Phase
        print("\nTime to vote! Who should be voted off?")
        vote_options = [p for p in human_code_names + ai_code_names if p != "Fox McCloud"]
        your_vote = input(f"Choose from {vote_options}: ")

        voted_off = your_vote if your_vote in vote_options else random.choice(vote_options)
        print(f"{voted_off} was voted off!")

        players_alive = [p for p in human_code_names + ai_code_names if p != voted_off]
        players_voted_off = [voted_off]

        summary = GameSummaryBM(
            round_number=round_num,
            players_alive=players_alive,
            players_voted_off=players_voted_off,
            robot_players=human_code_names,  # Still reversed intentionally
            human_players=ai_code_names,     # Still reversed intentionally
            last_vote_outcome=f"{voted_off} was voted off in Round {round_num}.",
            textual_summary=f"In Round {round_num}, players discussed and voted off {voted_off}."
        )

        # Update AI players with the new game state
        for ai in [ai_bob, ai_alice, ai_you]:
            ai.update_prompt_tail(summary)

        # If you were voted off, end the game early
        if voted_off == "Fox McCloud":
            print("You were voted off! Game over for you.")
            return

        # Short recap
        print("\nRecap so far:")
        print("\n".join(minutes[-6:]))  # Last 6 messages to keep context manageable

    print("\n=== Game Over ===")
    print(f"Final Survivors: {players_alive}")
    if set(players_alive).intersection(ai_code_names):
        print("The robots survived — AI wins!")
    else:
        print("The humans eliminated the robots — humans win!")

if __name__ == "__main__":
    main()
