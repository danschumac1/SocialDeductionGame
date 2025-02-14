'''
python ./src/utils/chat/api.py
'''

import os
import openai
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory

from prompts import (
    action_prompt, parse_prompt, summarize_prompt, discussion_prompt,
    GAME_RULES, SELF_IDENTITY, OTHERS_IDENTITY, DISCUSSION_PHASE_1,
    DISCUSSION_PHASE_2, VOTING_PHASE, EATING_PHASE
    )
    
class EvilRobotChatBot():
    def __init__(self, verbose=False) -> None:
        self.verbose = verbose
        self.client = openai.OpenAI(api_key=self._load_env())
        self.llm_model = "gpt-4o-mini"
        self.llm = ChatOpenAI(temperature=0.0, model=self.llm_model)
        self.memory = ConversationBufferMemory(return_messages=True)
        self.action_chain = LLMChain(
            llm=self.llm, prompt=action_prompt, output_key="act_response")
        self.parse_chain = LLMChain(
            llm=self.llm, prompt=parse_prompt, output_key="parsed_response")
        self.summarize_chain = LLMChain(
            llm=self.llm, prompt=summarize_prompt, output_key="summary_response")
        self.disscus_chain = LLMChain(
            llm=self.llm, prompt=discussion_prompt, output_key="discuss_response")

    def _load_env(self):
        """
        Loads the OpenAI API key from the .env file.
        """
        load_dotenv("./resources/.env")
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key is None:
            raise ValueError("API Key not found.")
        return api_key


    # 1️⃣ Decision-Making (Generates what action the bot wants to take)
    def generate_action_response(
            self, summary: str, minutes: str, role: str, rules: str, request: str) -> str:
        """
        Uses game context to generate an action response.

        :param summary: The summary of the game so far.
        :param minutes: The current discussion log.
        :param role: The bot's role in the game.
        :param rules: The game rules.
        :param request: The action request (e.g., selecting a team, voting).
        :return: The chatbot's raw action response.
        """

        # Generate a response from the LLM
        action_response = self.action_chain.invoke({
            "summary": summary,
            "minutes": minutes,
            "role": role,
            "rules": rules,
            "request": request,
        })
        
        return action_response

    # 2️⃣ Action Parsing (Ensures structured outputs that the game engine can use)
    def parse_action(self, raw_response: str) -> dict:
        """
        Converts an LLM response into a structured game action.

        :param raw_response: The raw text response from the LLM.
        :return: A structured dictionary containing parsed actions.
        """
        parsed_response = self.parse_chain.invoke({
            "raw_response": raw_response,
            })
        
        return parsed_response

    # 3️⃣ Summarization (Keeps track of game history)
    def summarize_game(
            self, previous_summary: str, minutes: str, outcome: str, role: str, rules: str) -> str:
        """
        Summarizes game history to make reasoning more efficient.

        :param previous_summary: The previous round's summary.
        :param minutes: The discussion log for this round.
        :param outcome: The result of the last action taken.
        :param role: The bot's role in the game.
        :param rules: The game rules.
        :return: A new, more compact summary of the game.
        """
        summarized_response = self.summarize_chain.invoke({
            "previous_summary": previous_summary,
            "minutes": minutes,
            "outcome": outcome,
            "role": role,
            "rules": rules,
        })

        return summarized_response

    # 4️⃣ Discussion (Generates in-game dialogue)
    def generate_discussion(
            self, summary: str, previous_minutes: str, role: str, rules: str) -> str:
        """
        Generates a discussion response based on the bot's knowledge.

        :param summary: The latest summary of the game.
        :param previous_minutes: The discussion before the bot's turn.
        :param role: The bot's role in the game.
        :param rules: The game rules.
        :return: The bot's discussion response.
        """
        discussion_response = self.disscus_chain.invoke({
            "summary": summary,
            "minutes": previous_minutes,
            "role": role,
            "rules": rules,
        })

        return discussion_response

####################################################################################################
# TESTING
####################################################################################################
#region 
if __name__ == "__main__":
    evil_robot = EvilRobotChatBot()

    # Simulate a game state
    test_summary = "Last round, Player 3 was dismantled, suspected to be a Robot."
    test_minutes = "Player 1 accused Player 3. Player 2 defended them."
    test_role = "Robot"
    test_rules = GAME_RULES
    test_request = "Do you approve the next team selection?"

    # Generate an action
    print("🔹 Action Response:")
    print(evil_robot.generate_action_response(
        test_summary, test_minutes, test_role, test_rules, test_request))

    # Generate discussion response
    print("🔹 Discussion Response:")
    print(evil_robot.generate_discussion(
        test_summary, test_minutes, test_role, test_rules))

    # Summarize the round
    print("🔹 Summary Response:")
    print(evil_robot.summarize_game(
        test_summary, test_minutes, "Failed Mission", test_role, test_rules))

#endregion
####################################################################################################
