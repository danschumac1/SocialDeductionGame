from langchain_core.prompts import PromptTemplate

action_prompt = PromptTemplate(
    input_variables=["summary", "minutes", "role", "rules", "request"],
    template= "You are playing a game. Your role: {role}."
        "Here are the rules: {rules}."
        "Summary of the game so far: {summary}."
        "Here is the latest discussion: {minutes}."
        "{request}"
        "Respond with what action you will take."
        )

parse_prompt = PromptTemplate(
    input_variables=["raw_response"],
    template="Parse the following response: {raw_response}."
    )

summarize_prompt = PromptTemplate(
    input_variables=["minutes"],
    template="Summarize the following discussion. Pay special attention to the players' suspicions and voting patterns in the game: {minutes}."
    )

discussion_prompt = PromptTemplate(
    input_variables=["minutes"],
    template="Generate a response to the following discussion. React to the players' suspicions and voting patterns: {minutes}."
    )

GAME_RULES = """
You are playing a game of hidden identities and social deduction.
There are two teams in the game: Humans and Robots.

Game Rules:

The Humans win if they can correctly identify and dismantle all Robots before the Robots eliminate them.

The Robots win if they successfully eliminate all Humans before being detected.

Each round consists of two discussion phases and a voting phase, followed by the Robots selecting a Human to eliminate.

- **Discussion Phase 1**: Players discuss their suspicions and try to identify the Robots.
- **Voting Phase**: All players vote on who they believe is a Robot. The player with the most votes is dismantled. If tied, no one is dismantled.
- **Discussion Phase 2**: Players react to the results of the vote and reassess their suspicions.
- **Eating Phase**: The Robots secretly select one Human to eliminate.

Robots may lie, deceive, and pretend to be Humans to avoid being dismantled.
Humans must use logic, deduction, and persuasion to identify the Robots.

The game continues until all Robots are eliminated (Human Victory) or all Humans are eliminated (Robot Victory).
"""

SELF_IDENTITY = """
You are code name {code_name}, and you are aligned with the {team}. You must maintain your identity and play according to your team’s objectives.
"""

OTHERS_IDENTITY = """
The following players are Robots: {robot_players}. The following players are confirmed Humans: {human_players}. Use this knowledge strategically.
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