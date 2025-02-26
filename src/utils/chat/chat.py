'''
python ./src/utils/chat/chat.py
'''

import json
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
# import raylibpy as rl
import os
from dotenv import load_dotenv
from typing import Tuple, Union

from utils.enums_dcs import (Team, ActionOptionBM, DecideToRespondBM, DefendYourselfBM, 
    AccusePlayerBM, GameSummaryBM, PersonaBM)
from utils.chat.prompts import (
    chose_action_prompt, decide_to_respond_prompt, defend_yourself_prompt, accuse_player_prompt,
    generate_persona_prompt, game_summary_prompt, game_rules
)

class AIPlayer:
    def __init__(
            self, code_name:str, color:Tuple[int,int,int,int] ,persona_to_steal: Union[None, PersonaBM], 
            is_persona_stealer: bool = True, 
            ):
        """Initializes AI player with a generated or stolen persona."""

        # Load LLM and LangChain setup
        self.code_name = code_name
        self.color = color
        self.client = self._load_env()
        self.llm = ChatOpenAI(temperature=0.7, model="gpt-4o-mini")
        self.memory = ConversationBufferMemory(return_messages=True)
        self.generate_persona_chain = generate_persona_prompt | self.llm
        self.system_prompt = None
        self.chose_action_chain = chose_action_prompt | self.llm
        self.decide_to_respond_chain = decide_to_respond_prompt | self.llm
        self.defend_chain = defend_yourself_prompt | self.llm
        self.accuse_chain = accuse_player_prompt | self.llm
        self.summarize_chain = game_summary_prompt | self.llm

        self.persona = self._steal_persona(persona_to_steal) if \
            is_persona_stealer else self._generate_persona()
        self.team = Team.ROBOT
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
            response_text = response.content  #  Extracts text properly
        else:
            raise TypeError(f" Unexpected response type: {type(response)} - {response}")

        try:
            #  Clean Markdown formatting & parse JSON
            parsed_data = json.loads(response_text.strip("```json").strip("```").strip())
            return model_class.model_validate(parsed_data)
        except json.JSONDecodeError:
            raise ValueError(f" Failed to parse LangChain response as JSON: {response_text}")

    def _generate_persona(self):
        """Generates a random persona for the AI."""
        response = self.generate_persona_chain.invoke({})
        #  Ensure we extract text correctly from `AIMessage`
        return self._parse_response(response, PersonaBM)  #  Use `.content` instead of `["text"]`
    
    def _steal_persona(self, persona:PersonaBM):
        """Steals a persona from a human player."""
        persona.color = self.color  #  Use AI's color
        persona.code_name = self.code_name  #  Use AI's code name
        return persona
        
    def initialize_system_prompt(self, human_code_names: list, ai_code_names: str):
        """Initializes the system prompt for the AI with game rules, persona, and initial game state."""

        # Load base game rules
        game_rules_str = game_rules  

        # Format AI persona
        persona_str = (
            f"Your name is {self.persona.name}. "
            f"Your hobbies include {self.persona.hobby}. "
            f"Your favorite food is {self.persona.food}. "
            f"Other personal details: {self.persona.anythingelse}."
        )

        # Establish the AI’s identity and team
        game_state_str = (
            "You are a Robot player in a hidden identity game. "
            "Your goal is to avoid detection and help your team win. "
            f"The Robot players are {ai_code_names}. "
            f"The human players are {human_code_names} "
            "You must keep your identity as a Robot secret. "
            "The game is in its early stages."
            )

        # Store as structured data
        self.system_prompt = {
            "game_rules": game_rules_str,
            "persona": persona_str,
            "game_state": {
                "role": "Robot",
                "team": "Robots",
                "other_robot_code_names": ai_code_names,
                "current_phase": "Game Start",
                "players_alive": human_code_names + ai_code_names,
                "players_killed": [],
                "players_voted_off": [],
                "voting_history": {},
                "last_vote_outcome": "N/A",
                "summary": game_state_str,
            }
        }
        system_prompt = json.dumps(self.system_prompt, indent=4)
        self.system_prompt = system_prompt
        # return json.dumps(self.system_prompt, indent=4)

    
    def update_system_prompt(self, game_state_summary: GameSummaryBM):
        """Dynamically updates the AI’s system prompt based on the latest game state."""

        if not hasattr(self, "system_prompt") or not self.system_prompt:
            raise ValueError("System prompt not initialized. Call `initialize_system_prompt` first.")

        # Update current phase and round
        self.system_prompt["game_state"]["current_phase"] = game_state_summary.current_phase
        self.system_prompt["game_state"]["round_number"] = game_state_summary.round_number

        # Update player statuses
        self.system_prompt["game_state"]["players_alive"] = game_state_summary.players_alive
        self.system_prompt["game_state"]["players_killed"] = game_state_summary.players_killed
        self.system_prompt["game_state"]["players_voted_off"] = game_state_summary.players_voted_off

        # Update voting history and last vote outcome
        self.system_prompt["game_state"]["voting_history"] = game_state_summary.voting_history
        self.system_prompt["game_state"]["last_vote_outcome"] = game_state_summary.last_vote_outcome

        # Track known identities
        self.system_prompt["game_state"]["robot_players"] = game_state_summary.robot_players
        self.system_prompt["game_state"]["human_players"] = game_state_summary.human_players

        # Update textual game summary for AI reasoning
        self.system_prompt["game_state"]["summary"] = game_state_summary.textual_summary

        return json.dumps(self.system_prompt, indent=4)

    def decide_to_respond(self, message):
        """Determines whether AI should respond and what action to take."""
        
        response = self.decide_to_respond_chain.invoke({"minutes": message})

        #  Use DRY function to parse response
        decision = self._parse_response(response, DecideToRespondBM)

        # Store message in memory
        self.memory.save_context({"input": message}, {"output": ""})

        #  Ensure AI Introduces Itself if Needed
        if not self.has_introduced and decision.introducing_done is False:
            introduction_response = self.introduce()
            self.has_introduced = True  #  Mark AI as introduced
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

        #  Parse as ActionOptionBM, NOT PersonaBM
        action = self._parse_response(response, ActionOptionBM)

        if action.introduce:
            self.has_introduced = True  #  Mark AI as introduced
            return action.introduce  #  Return AI's introduction statement
        
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