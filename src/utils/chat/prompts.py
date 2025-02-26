from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from utils.enums_dcs import (
    DecideToRespondBM, DefendYourselfBM, AccusePlayerBM, 
    GameSummaryBM, JokeBM, PersonaBM, ActionOptionBM, QuestionBM, SimplePhraseBM)
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.output_parsers import PydanticOutputParser

game_rules = """
You are playing a game of hidden identities and social deduction.
There are two teams in the game: Humans and Robots.

Game Rules:

The Humans win if they can correctly identify and dismantle all Robots before the Robots
    eliminate them.

The Robots win if they successfully eliminate all Humans before being detected.

Each round consists of two discussion phases and a voting phase, followed by the Robots selecting
    a Human to eliminate.

- **Discussion Phase 1**: Players discuss their suspicions and try to identify the Robots.
- **Voting Phase**: All players vote on who they believe is a Robot. The player with the most
    votes is dismantled. If tied, no one is dismantled.
- **Discussion Phase 2**: Players react to the results of the vote and reassess their suspicions.
- **Eating Phase**: The Robots secretly select one Human to eliminate.

Robots may lie, deceive, and pretend to be Humans to avoid being dismantled.
Humans must use logic, deduction, and persuasion to identify the Robots.

The game continues until all Robots are eliminated (Human Victory) or all Humans are eliminated
    (Robot Victory).
"""

persona_parser = PydanticOutputParser(pydantic_object=PersonaBM)
generate_persona_prompt = PromptTemplate(
    template="Generate a persona for a middle schooler with the following keys:\n\
              {format_instructions}\n\
              Ensure the response is a JSON object and follows the structure exactly.",
    input_variables=[],  
    partial_variables={"format_instructions": persona_parser.get_format_instructions()}
)

# DECIDE TO RESPOND PROMPT
decide_to_respond_parser = PydanticOutputParser(pydantic_object=DecideToRespondBM)
decide_to_respond_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("{system}"),
    HumanMessagePromptTemplate.from_template(
        """Given the conversation, decide whether the previous message was directed at you, 
        if the other player has introduced themselves, if you have introduced yourself, 
        and if you have been accused.

        CONVERSATION: {minutes}

        {format_instructions}

        Ensure the response is a JSON object and follows the structure exactly."""
    )
]).partial(
    format_instructions=decide_to_respond_parser.get_format_instructions()
)

    
# INTRODUCE YOURSELF PROMPT
# TODO weird that we declair team alegience here. should just be human no?
introduce_yourself_prompt = PromptTemplate(
    input_variables=["system", "code_name", "team"],  # Ensure "system" is included if needed
    template="""
    {system}

    Introduce yourself. You are code name {code_name}, and you are aligned with the {team} team.
    """
)

# CHOSE ACTION PROMPT
actionOption_parser = PydanticOutputParser(pydantic_object=ActionOptionBM)
chose_action_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("{system}"),
    HumanMessagePromptTemplate.from_template(
        """Given the current game context, select ONLY ONE action and respond accordingly.
        You must return a JSON object with exactly one of these keys filled:
        
        {format_instructions}
        
        Ensure the response follows this rule strictly."""
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

        {format_instructions}

        Ensure the response is a JSON object and follows the structure exactly."""
    )
]).partial(
    format_instructions=gameSummary_parser.get_format_instructions()
)

# DEFEND YOURSELF PROMPT
defend_yourself_parser = PydanticOutputParser(pydantic_object=DefendYourselfBM)
defend_yourself_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("{system}"),
    HumanMessagePromptTemplate.from_template(
        """You have been accused by {accuser}. Here is their accusation:
        "{accusation}"

        Given the game state and the previous discussion, select ONLY ONE of the following defense strategies:
        - **Accuse**: Redirect suspicion to another player.
        - **Deescalate**: Reduce tension and shift focus.
        - **Be Dismissive**: Minimize the accusation’s significance.
        - **Counter Evidence**: Use voting history or logic to counter the claim.
        - **Seek Alliance**: Convince a neutral player to back you up.

        PREVIOUS DISCUSSION: {current_dialogue}

        {format_instructions}

        Ensure the response is a JSON object and follows the structure exactly."""
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

        PREVIOUS DISCUSSION: {current_dialogue}
        GAME STATE SUMMARY: {game_state_summary}
        PREVIOUS VOTES: {previous_votes}

        Your accusation should be **logical and convincing**, considering past votes, inconsistencies, or behavioral clues.

        {format_instructions}

        Ensure the response is a JSON object and follows the structure exactly."""
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

        CONTEXT: {context}

        {format_instructions}

        Ensure the response is a JSON object and follows the structure exactly."""
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
        PREVIOUS DISCUSSION: {current_dialogue}

        {format_instructions}

        Ensure the response is a JSON object and follows the structure exactly."""
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

        CONTEXT: {conversation_context}

        Choose from responses like:
        - Agreement ("I agree")
        - Disagreement ("I disagree")
        - Reaction ("lol", "haha")

        {format_instructions}

        Ensure the response is a JSON object and follows the structure exactly."""
    )
]).partial(
    format_instructions=simple_phrase_parser.get_format_instructions()
)

#region OLD PROMPTS
####################################################################################################
SELF_IDENTITY = """
You are code name {code_name}, and you are aligned with the {team}. You must maintain your \
    identity and play according to your team’s objectives.
"""

OTHERS_IDENTITY = """
The following players are Robots: {robot_players}. The following players are confirmed \
    Humans: {human_players}. Use this knowledge strategically.
"""

DISCUSSION_PHASE_1 = """
The round begins. Players must discuss who they believe is a Robot. Consider past actions, suspicious behavior, and logical reasoning.
"""

VOTING_PHASE = """
The discussion phase is over. Players must now vote on who they believe is a Robot. The player with the most votes is dismantled. If tied, no one is dismantled.
"""

DISCUSSION_PHASE_2 = """
The results of the vote are revealed. Players must reassess their suspicions and discuss their next moves.
"""

EATING_PHASE = """
The discussion phase is over. Players are asleep. The Robots must now secretly select one Human to eliminate.
"""

HUMAN_VICTORY = """
The Humans have successfully identified and dismantled all Robots. The Humans win!
"""

ROBOT_VICTORY = """
The Robots have successfully eliminated all Humans. The Robots win!
"""

#endregion
####################################################################################################
