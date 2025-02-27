'''
python ./src/chat_test.py
'''

# Testing AIPlayer
from utils.chat.chat import AIPlayer
from utils.enums_dcs import PersonaBM


def main():
    bob = PersonaBM(
        name="Bob B.",
        code_name="Mario",
        color = (255, 0, 0, 255), # red
        hobby="fishing",
        food="pizza",
        anythingelse="I like to play video games",
    )
    alice = PersonaBM(
        name="Alice A.",
        code_name="Samus Aran",
        color = (255, 165, 0, 255), # orange
        hobby="swimming",
        food="sushi",
        anythingelse="I like to read books",
    )
    carlos = PersonaBM(
        name="Carlos C.",
        code_name="Fox McCloud",
        color = (0, 0, 255, 255), # blue
        hobby="playing soccer",
        food="hamburgers",
        anythingelse="I like to watch movies with my dad and build model airplanes",
    )

    ai_bob = AIPlayer(
        code_name="Luigi",
        color = (0, 255, 0, 255), # green
        persona_to_steal=bob
    )
    ai_alice = AIPlayer(
        code_name="Princess Peach",
        color = (255, 192, 203, 255), # pink
        persona_to_steal=alice
    )
    ai_carlos = AIPlayer(
        code_name="Donkey Kong",
        color = (165, 42, 42, 255), # brown
        persona_to_steal=carlos
    )

    # initialize ai
    human_code_names = [player.code_name for player in [bob, alice, carlos]]
    ai_code_names = [player.code_name for player in [ai_bob, ai_alice, ai_carlos]]

    # Initialize a fake chat history
    minutes = [
        "Mario: Hi everyone, this is Bob",
        "Samus Aran: Hello, this is Alice",
        "Fox McCloud: Hi, this is Carlos",
        ]
    
    for i, ai in enumerate([ai_bob, ai_alice, ai_carlos]):
        ai.initialize_system_prompt(human_code_names, ai_code_names)
        print(ai.introduce(minutes))


if __name__ == "__main__":
    main()