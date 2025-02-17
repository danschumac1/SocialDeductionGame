'''
python ./src/utils/chat/chat.py
'''

import json
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
import os
from dotenv import load_dotenv
from typing import Union
import sys
sys.path.append("./src")
from utils.enums_dcs import (Team, ActionOptionBM, DecideToRespondBM, DefendYourselfBM, 
    AccusePlayerBM, GameSummaryBM, PersonaBM)
from prompts import (
    chose_action_prompt, decide_to_respond_prompt, defend_yourself_prompt, accuse_player_prompt,
    generate_persona_prompt, game_summary_prompt, GAME_RULES
)

class AIPlayer:
    def __init__(
            self, team: Team = Team.ROBOT, is_persona_stealer: bool = False, 
            persona: Union[None, str] = None):
        """Initializes AI player with a generated or stolen persona."""

        # Load LLM and LangChain setup
        self.client = self._load_env()
        self.llm = ChatOpenAI(temperature=0.7, model="gpt-4o-mini")
        self.memory = ConversationBufferMemory(return_messages=True)
        self.generate_persona_chain = generate_persona_prompt | self.llm
        self.chose_action_chain = chose_action_prompt | self.llm
        self.decide_to_respond_chain = decide_to_respond_prompt | self.llm
        self.defend_chain = defend_yourself_prompt | self.llm
        self.accuse_chain = accuse_player_prompt | self.llm
        self.summarize_chain = game_summary_prompt | self.llm

        self.persona = self._steal_persona(persona) if \
            is_persona_stealer else self._generate_persona()
        self.code_name = "Susan" # TODO FIX
        self.team = team
        self.is_persona_stealer = is_persona_stealer
        self.voting_history = []
        self.has_introduced = False
        self.is_accused = False
        self.is_questioned = False
        self.humans_introduced = 0

    def _load_env(self):
        """Loads OpenAI API key from .env"""
        load_dotenv("./resources/.env")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("API Key not found.")
        print("API Key loaded successfully.")
        return api_key
    
    def _parse_response(self, response, model_class):
        """
        Extracts text from an AIMessage response, removes Markdown artifacts, 
        parses JSON, and validates it using the provided Pydantic model.
        
        :param response: AIMessage response from LangChain
        :param model_class: Pydantic model class to validate the parsed JSON
        :return: Parsed and validated Pydantic model instance
        """
        if hasattr(response, "content"):  
            response_text = response.content  # ✅ Extracts text properly
        else:
            raise TypeError(f"❌ Unexpected response type: {type(response)} - {response}")

        try:
            # ✅ Clean Markdown formatting & parse JSON
            parsed_data = json.loads(response_text.strip("```json").strip("```").strip())
            return model_class.model_validate(parsed_data)
        except json.JSONDecodeError:
            raise ValueError(f"❌ Failed to parse LangChain response as JSON: {response_text}")

    def _generate_persona(self):
        """Generates a random persona for the AI."""
        response = self.generate_persona_chain.invoke({})

        # ✅ Ensure we extract text correctly from `AIMessage`
        if hasattr(response, "content"):  
            return response.content  # ✅ Use `.content` instead of `["text"]`
        
        raise TypeError(f"❌ Unexpected response type: {type(response)} - {response}")


    def _steal_persona(self, persona):
        """Steals a persona from a human player."""
        return {
            "name": persona["code_name"],
            "hobby": persona["hobby"],
            "favorite_food": persona["food"],
            "anythingelse": persona["anythingelse"]
        }

    def decide_to_respond(self, message):
        """Determines whether AI should respond and what action to take."""
        
        response = self.decide_to_respond_chain.invoke({"minutes": message})

        # ✅ Use DRY function to parse response
        decision = self._parse_response(response, DecideToRespondBM)

        # Store message in memory
        self.memory.save_context({"input": message}, {"output": ""})

        # ✅ Ensure AI Introduces Itself if Needed
        if not self.has_introduced and decision.introducing_done is False:
            introduction_response = self.introduce()
            self.has_introduced = True  # ✅ Mark AI as introduced
            return introduction_response

        # If AI should respond, choose an action
        if decision.directed_at_me or decision.accused:
            return self.choose_action(message)

        return "Wait for next message"


    def choose_action(self, message):
        """Determines the best action to take based on the game state."""
        
        response = self.chose_action_chain.invoke({"previous_discussion": message})
        
        action = self._parse_response(response, ActionOptionBM)

        if action.introduce:
            return self.introduce()
        elif action.defend:
            return self.defend(message)
        elif action.accuse:
            return self.accuse(action.accuse)
        elif action.joke:
            return action.joke  # AI tells a joke directly
        elif action.question:
            return action.question  # AI asks a question
        elif action.simple_phrase:
            return action.simple_phrase  # AI responds with a simple phrase
        return "No action taken."

    def introduce(self):
        """Handles AI introduction logic."""
        
        response = self.chose_action_chain.invoke({
            "code_name": self.code_name,
            "team": self.team.name
        })

        # ✅ Parse as ActionOptionBM, NOT PersonaBM
        action = self._parse_response(response, ActionOptionBM)

        if action.introduce:
            self.has_introduced = True  # ✅ Mark AI as introduced
            return action.introduce  # ✅ Return AI's introduction statement
        
        return "Error: Failed to generate introduction."

    def defend(self, message):
        """Handles AI defense when accused."""
        
        response = self.defend_chain.invoke({
            "accuser": "Unknown",
            "accusation": message,
            "current_dialogue": self.memory.load_memory_variables({})
        })

        defense = self._parse_response(response, DefendYourselfBM)

        return defense.response_text


    def accuse(self, player_to_accuse):
        """Handles AI accusation logic."""
        
        response = self.accuse_chain.invoke({
            "current_dialogue": self.memory.load_memory_variables({}),
            "game_state_summary": "Current game state summary placeholder",
            "player_to_accuse": player_to_accuse
        })

        accusation = self._parse_response(response, AccusePlayerBM)

        return accusation.response_text

    def update_game_state(self):
        """Updates AI's internal memory based on game events."""
        pass

# Testing AIPlayer
if __name__ == "__main__":
    print("\n🚀 Running AIPlayer Full Game Simulation...\n")

    # ✅ Initialize AI Player
    ai_player = AIPlayer()
    print("🤖 AI Player Initialized."
          "\n - Persona: ", ai_player.persona)
    print(" - Team: ", ai_player.team)
    print(" - Persona Stealer: ", ai_player.is_persona_stealer)
    print(" - Code Name: ", ai_player.code_name)

    # ✅ Initial AI State Check
    print("\n🔍 Initial AI State Check:"
          "\n - Has Introduced: ", ai_player.has_introduced,
          "\n - Voting History: ", ai_player.voting_history)

    # ✅ Round 0: AI Decides to Respond
    print("\n🔹 Round 0: AI Decides to Respond"
          "\n - No Introduction Yet")
    ai_player.decide_to_respond("Hello everyone, introduce yourselves!")

    # ✅ Check AI State After Decision
    print("\n🔍 AI State Check After Decision:"
          "\n - Has Introduced: ", ai_player.has_introduced,
          "\n - Voting History: ", ai_player.voting_history)
    
    # ✅ Reset AI State for Next Round
    print("\n🔹 Resetting AI State for Next Round..."
          "\n - No Introduction Yet")
    ai_player.has_introduced = False
    ai_player.voting_history = []

    # ✅ Check AI State After Reset
    print("\n🔍 AI State Check After Reset:"
          "\n - Has Introduced: ", ai_player.has_introduced,
          "\n - Voting History: ", ai_player.voting_history)
    

    assert ai_player.has_introduced is False
    assert ai_player.voting_history == []
    
    # ✅ Round 1: AI Introduces Itself
    print("\n🔹 Round 1: AI Introduces Itself")
    introduction_response = ai_player.decide_to_respond("Hello everyone, introduce yourselves!")
    print(f"🗣️ AI Response: {introduction_response}")
    assert ai_player.has_introduced is True  # Ensure AI introduced itself
    
    # ✅ Round 2: AI Gets Accused
    print("\n🔹 Round 2: AI is Accused")
    accusation_message = "I think AIPlayer is acting strange. They're a robot!"
    defense_response = ai_player.decide_to_respond(accusation_message)
    print(f"🛡️ AI Defense: {defense_response}")
    
    # ✅ Round 3: AI Accuses Another Player
    print("\n🔹 Round 3: AI Accuses Another Player")
    accusation_response = ai_player.accuse("Player2")
    print(f"🔍 AI Accusation: {accusation_response}")

    # ✅ Round 4: AI De-escalates Conflict
    print("\n🔹 Round 4: AI Attempts to De-escalate")
    deescalation_response = ai_player.decide_to_respond("Let's not jump to conclusions.")
    print(f"🤝 AI De-escalation: {deescalation_response}")

    # ✅ Round 5: AI Makes a Joke
    print("\n🔹 Round 5: AI Tells a Joke")
    joke_response = ai_player.decide_to_respond("Let's lighten the mood. Anyone got jokes?")
    print(f"🤣 AI Joke: {joke_response}")

    # ✅ Round 6: AI Asks a Question
    print("\n🔹 Round 6: AI Asks a Strategic Question")
    question_response = ai_player.decide_to_respond("Who do you think is the most suspicious?")
    print(f"❓ AI Question: {question_response}")

    # ✅ Round 7: AI Responds with a Simple Phrase
    print("\n🔹 Round 7: AI Uses a Simple Response")
    simple_phrase_response = ai_player.decide_to_respond("That’s a fair point.")
    print(f"💬 AI Simple Phrase: {simple_phrase_response}")

    # ✅ Round 8: AI Processes a Game Summary
    print("\n🔹 Round 8: AI Updates Game Summary")
    summary_response = ai_player.update_game_state()
    print(f"📊 AI Game Summary Updated: {summary_response}")

    # ✅ Final Check: AI Internal State
    print("\n🔍 Final AI State Check:")
    print(f" - Has Introduced: {ai_player.has_introduced}")
    print(f" - Voting History: {ai_player.voting_history}")
    print(f" - Humans Introduced: {ai_player.humans_introduced}")

    print("\n✅ AIPlayer Full Game Simulation Complete!\n")

