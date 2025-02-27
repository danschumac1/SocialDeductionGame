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
from typing import List, Tuple, Union

from utils.enums_dcs import (Team, ActionOptionBM, DecideToRespondBM, DefendYourselfBM, 
    AccusePlayerBM, GameSummaryBM, PersonaBM)
from utils.chat.prompts import (
    chose_action_prompt, decide_to_respond_prompt, defend_yourself_prompt, accuse_player_prompt,
    generate_persona_prompt, game_summary_prompt, game_rules, introduce_yourself_prompt
)
from utils.logging_utils import StandAloneLogger

class AIPlayer:
    def __init__(
            self, code_name:str, color:Tuple[int,int,int,int] ,persona_to_steal: Union[None, PersonaBM], 
            is_persona_stealer: bool = True, 
            ):
        """Initializes AI player with a generated or stolen persona."""

        # Load LLM and LangChain setup
        self.code_name = code_name
        self.color = color
        self.logger = StandAloneLogger(
            log_path=f"./logs/ai_{self.code_name}.log", 
            clear=True, 
            init = True
        )
        self.client = self._load_env()
        self.llm = ChatOpenAI(temperature=0.7, model="gpt-4o-mini")
        self.memory = ConversationBufferMemory(return_messages=True)
        self.generate_persona_chain = generate_persona_prompt | self.llm
        self.system_prompt = None
        self.chose_action_chain = chose_action_prompt | self.llm
        self.introduce_chain = introduce_yourself_prompt | self.llm
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
        self.logger.info("API Key loaded successfully.")
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
            self.logger.error(f"Failed to parse LangChain response as JSON: {response_text}")
            raise ValueError(f" Failed to parse LangChain response as JSON: {response_text}")

    def _generate_persona(self):
        """Generates a random persona for the AI."""
        response = self.generate_persona_chain.invoke({})
        #  Ensure we extract text correctly from `AIMessage`
        generated_persona =  self._parse_response(response, PersonaBM)
        self.logger.info(f"Generated persona: {generated_persona}")
        return generated_persona
    
    def _steal_persona(self, persona: PersonaBM) -> PersonaBM:
        """Creates a modified copy of the human persona instead of modifying the original."""
        stolen_persona = PersonaBM(
            name=persona.name,
            code_name=self.code_name,  # Use AI's code name
            color=self.color,  # Use AI's color
            hobby=persona.hobby,
            food=persona.food,
            anythingelse=persona.anythingelse
        )
        self.logger.info(f"Stolen persona: {stolen_persona}")
        return stolen_persona

    def initialize_system_prompt(self, human_code_names: list, ai_code_names: list):
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
        ai_code_names_str = ", ".join(ai_code_names)
        human_code_names_str = ", ".join(human_code_names)

        game_state_str = (
            "You are a Robot player in a hidden identity game. "
            "Your goal is to avoid detection and help your team win. "
            f"The Robot players are [{ai_code_names_str}]. "
            f"The human players are [{human_code_names_str}]. "
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
                "players_alive": human_code_names + ai_code_names,  # Ensure unique entries
                "players_killed": [],
                "players_voted_off": [],
                "voting_history": {},
                "last_vote_outcome": "N/A",
                "summary": game_state_str,
            }
        }

        system_prompt = json.dumps(self.system_prompt, indent=4)
        self.system_prompt = system_prompt
        self.logger.info(f"Initialized system prompt: {system_prompt}")


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

        self.logger.info(f"Updated system prompt: {self.system_prompt}")
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
            respond = self.choose_action(message)
        else:
            respond = "Wait for next message"
        self.logger.info(f"AI decided to respond with: {respond}")
        return respond

    def choose_action(self, minutes: List[str]):
        """Determines the best action to take based on the game state."""
        messages = "\n".join(minutes)
        response = self.chose_action_chain.invoke({"previous_discussion": messages})
        
        action = self._parse_response(response, ActionOptionBM)
        self.logger.info(f"AI chose action: {action}")

        if action.introduce:
            return self.introduce()
        elif action.defend:
            return self.defend(messages)
        elif action.accuse:
            return self.accuse(action.accuse)
        elif action.joke:
            return action.joke  # AI tells a joke directly
        elif action.question:
            return action.question  # AI asks a question
        elif action.simple_phrase:
            return action.simple_phrase  # AI responds with a simple phrase
        return "No action taken."

    def introduce(self, minutes: str):
        """Handles AI introduction logic."""
        # TODO Maybe add a check to see if the AI has already introduced itself?

        introduction = self.introduce_chain.invoke({
            "system": self.system_prompt,
            "code_name": self.code_name,
            "minutes": minutes
        })

        # We don't need to validate the response here, because it's a simple string
        self.logger.info(f"AI introduced itself: {introduction.content}")
        return introduction.content

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