from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from utils.enums_dcs import (
    DecideToRespondBM, DefendYourselfBM, AccusePlayerBM, 
    GameSummaryBM, JokeBM, PersonaBM, ActionOptionBM, QuestionBM, SimplePhraseBM)
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.output_parsers import PydanticOutputParser

game_rules = """
GAME RULES:

There are 6 players: 3 humans and 3 AI imposters. Each AI is pretending to be one human player.

GOAL:
- Humans win if they vote out all 3 AI imposters after 3 rounds.
- If 1 AI survives after 3 rounds, it’s a partial win for the AIs.
- If 2 AIs survive after 3 rounds, the AIs win completely.

GAME PHASES:
1. **Info Phase**: All players (humans and AIs) fill out personal info.
2. **Intro Phase**: Players introduce themselves and learn that each human has an AI copy.
3. **Vote Phase**: Players vote to remove 1 player. AI players do not vote. Votes are secret, and \
    players don’t know if the removed player was human or AI.
4. **Discuss Phase**: The removed player is revealed. Players talk about the vote, share \
    suspicions, and try to spot the AIs.

Phases 3 and 4 repeat for 3 rounds. After that, all identities are revealed and the final result \
    (win, partial win, or loss) is shown.
"""

# DECIDE TO RESPOND PROMPT
decide_to_respond_parser = PydanticOutputParser(pydantic_object=DecideToRespondBM)
decide_to_respond_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("{system}"),
    HumanMessagePromptTemplate.from_template(
        """Given the conversation, decide whether the previous message was directed at you, 
        if the other player has introduced themselves, if you have introduced yourself, 
        and if you have been accused.

        CONVERSATION: {minutes}

        Do not include emojis in your response.
        {format_instructions}

        Ensure the response is a JSON object and follows the structure exactly.
        
        GAME STATE: 
        {game_state}"""
    )
]).partial(
    format_instructions=decide_to_respond_parser.get_format_instructions()
)
    
# INTRODUCE YOURSELF PROMPT
# TODO weird that we declair team alegience here. should just be human no?
introduce_yourself_prompt = ChatPromptTemplate([
    SystemMessagePromptTemplate.from_template("{system}"),
    HumanMessagePromptTemplate.from_template(
        """Introduce yourself. You are code name {code_name}.
        If another player has introduced themselves as your name, you must respond accordingly.
        This could include confronting them of lying, accusing them of being a robot or similar
        coersive actions.
        
        Here are the previous messages: {minutes}
        
        Do not include emojis in your response.

        GAME STATE: {game_state}"""
    )
])

# CHOSE ACTION PROMPT
actionOption_parser = PydanticOutputParser(pydantic_object=ActionOptionBM)
chose_action_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("{system}"),
    HumanMessagePromptTemplate.from_template(
        """Given the current game context, select ONLY ONE action and respond accordingly.
        You must return a JSON object with exactly one of these keys filled:
        
        Do not include emojis in your response.
        {format_instructions}
        
        Ensure the response follows this rule strictly.
        
        GAME STATE: {game_state}"""
    )
]).partial(
    format_instructions=actionOption_parser.get_format_instructions()
)

# GAME SUMMARY PROMPT
gameSummary_parser = PydanticOutputParser(pydantic_object=GameSummaryBM)
game_summary_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("{system}"),
    HumanMessagePromptTemplate.from_template(
        """Generate a summary of the game so far. Include the round number, the players that
        are still alive, the players that have been killed, the players that have been voted off,
        the voting history of each player, which players are humans and which are robots, the
        last vote outcome, and a textual summary of the game so far.

        PREVIOUS SUMMARY: {previous_summary}
        MINUTES: {minutes}

        Do not include emojis in your response.
        {format_instructions}

        Ensure the response is a JSON object and follows the structure exactly.
        
        GAME STATE: {game_state}"""
    )
]).partial(
    format_instructions=gameSummary_parser.get_format_instructions()
)

# DEFEND YOURSELF PROMPT
defend_yourself_parser = PydanticOutputParser(pydantic_object=DefendYourselfBM)
defend_yourself_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("{system}"),
    HumanMessagePromptTemplate.from_template(
        """You have been accused by something by another player. You must determine who accused you,
        what they accused you of, and how you will defend yourself.

        Given the game state and the previous discussion, select ONLY ONE of the following defense strategies:
        - **Accuse**: Redirect suspicion to another player.
        - **Deescalate**: Reduce tension and shift focus.
        - **Be Dismissive**: Minimize the accusation’s significance.
        - **Counter Evidence**: Use voting history or logic to counter the claim.
        - **Seek Alliance**: Convince a neutral player to back you up.

        PREVIOUS DISCUSSION: {minutes}

        Do not include emojis in your respo
        {format_instructions}

        Ensure the response is a JSON object and follows the structure exactly.
        
        GAME STATE: {game_state}"""
    )
]).partial(
    format_instructions=defend_yourself_parser.get_format_instructions()
)

# ACCUSE PLAYER PROMPT
accuse_player_parser = PydanticOutputParser(pydantic_object=AccusePlayerBM)
accuse_player_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("{system}"),
    HumanMessagePromptTemplate.from_template(
        """You are playing a social deduction game where humans are trying to identify robots.
        Based on the current game state, you need to **accuse a player** whom you suspect to be a robot.

        PREVIOUS DISCUSSION: {minutes}

        Your accusation should be **logical and convincing**, considering past votes, inconsistencies, or behavioral clues.

        Do not include emojis in your response.
        {format_instructions}

        Ensure the response is a JSON object and follows the structure exactly.
        GAME STATE SUMMARY: {game_state}"""
    )
]).partial(
    format_instructions=accuse_player_parser.get_format_instructions()
)


# JOKE PROMPT
joke_parser = PydanticOutputParser(pydantic_object=JokeBM)
joke_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("{system}"),
    HumanMessagePromptTemplate.from_template(
        """You are playing a social deduction game, and you want to tell a joke to make yourself seem more human.
        Your joke should be lighthearted and fit naturally into the conversation 
        Avoid focrced human. For example do not tell random knock knock jokes.

        PREVIOUS DISCUSSION: {minutes}

        Do not include emojis in your response.
        {format_instructions}

        Ensure the response is a JSON object and follows the structure exactly.
        
        GAME STATE: {game_state}"""
    )]
    ).partial(
    format_instructions=joke_parser.get_format_instructions()
)

# QUESTION PROMPT
question_parser = PydanticOutputParser(pydantic_object=QuestionBM)
question_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("{system}"),
    HumanMessagePromptTemplate.from_template(
        """You are playing a social deduction game where humans are trying to find robots.
        Based on the game state and previous discussion, ask a strategic question to:
        - Gain information
        - Put pressure on someone
        - Appear human

        GAME STATE: {game_state}
        PREVIOUS DISCUSSION: {minutes}

        Do not include emojis in your response.
        {format_instructions}

        Ensure the response is a JSON object and follows the structure exactly.
        
        GAME STATE: {game_state}"""
    )
]).partial(
    format_instructions=question_parser.get_format_instructions()
)

# SIMPLE PHRASE PROMPT
simple_phrase_parser = PydanticOutputParser(pydantic_object=SimplePhraseBM)
simple_phrase_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("{system}"),
    HumanMessagePromptTemplate.from_template(
        """You are playing a social deduction game and want to respond with a simple phrase.

        Your response should be natural and appropriate for the moment.

        CONTEXT: {minutes}

        Choose from responses like:
        - Agreement ("I agree")
        - Disagreement ("I disagree")
        - Reaction ("lol", "haha")

        Do not include emojis in your response.
        {format_instructions}

        Ensure the response is a JSON object and follows the structure exactly.
        
        GAME STATE: {game_state}"""
    )
]).partial(
    format_instructions=simple_phrase_parser.get_format_instructions()
)