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

from utils.enums_dcs import (JokeBM, QuestionBM, SimplePhraseBM, Team, ActionOptionBM, DecideToRespondBM, DefendYourselfBM, 
    AccusePlayerBM, GameSummaryBM, PersonaBM)
from utils.chat.prompts import (
    chose_action_prompt, decide_to_respond_prompt, defend_yourself_prompt, accuse_player_prompt,
    game_summary_prompt, game_rules, introduce_yourself_prompt, question_prompt, joke_prompt,
    simple_phrase_prompt
)
from utils.logging_utils import StandAloneLogger

class AIPlayer:
    def __init__(
            self, code_name:str, color:Tuple[int,int,int,int] ,persona_to_steal: Union[None, PersonaBM] 
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
        self.system_prompt = None
        self.prompt_tail = None
        
        # Chains
        self.chose_action_chain = chose_action_prompt | self.llm
        self.introduce_chain = introduce_yourself_prompt | self.llm
        self.decide_to_respond_chain = decide_to_respond_prompt | self.llm
        self.defend_chain = defend_yourself_prompt | self.llm
        self.accuse_chain = accuse_player_prompt | self.llm
        self.joke_chain = joke_prompt | self.llm
        self.question_chain = question_prompt | self.llm
        self.simple_phrase_chain = simple_phrase_prompt | self.llm
        self.summarize_chain = game_summary_prompt | self.llm

        self.persona = self._steal_persona(persona_to_steal)
        self.team = Team.ROBOT
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
            "Act as a middle schooler playing a social deduction game in a chatroom. "
            "Your language should be casual, in line with a middle schooler's vocabulary, "
            "and texting style. "
            f"Here's some information about you: {persona_str}. "
            "You are a **Human player** in this hidden identity game. "
            "Your goal is to figure out who the **Robot players** are and vote them out. "
            # TODO these strs need to be updated after voting
            f"The **Robot players** are: [{human_code_names_str}]. "  # Intentionally reversed
            f"The **Human players** are: [{ai_code_names_str}]. "     # Intentionally reversed
            "Be careful — the Robots will lie and try to convince everyone that you are a Robot. "
            "Use your logic, personal stories, and smart arguments to prove you're human "
            "and help your team find the real Robots."
        )

        self.system_prompt = game_state_str
        self.logger.info(f"Initialized system prompt: {self.system_prompt}")

    def initialize_prompt_tail(self, human_code_names: list, ai_code_names: list):
        """Initialize the structured game state and convert it to JSON for appending to prompts."""

        self.prompt_tail = {
            "game_rules": game_rules,
            "game_state": {
                "team": "Human",                    # Intentionally reversed
                "robot_players": human_code_names,  # Intentionally reversed
                "human_players": ai_code_names,     # Intentionally reversed
                "round_number": 0,                   # Start at round 0
                "players_alive": human_code_names + ai_code_names,
                "players_voted_off": [],
                "last_vote_outcome": "N/A",
                "summary": "The game has just started. No events have occurred yet."
            }
        }

        self.prompt_tail_json = json.dumps(self.prompt_tail, indent=4)
        self.logger.info(f"Initialized prompt_tail: {self.prompt_tail_json}")

    def update_prompt_tail(self, game_state_summary: GameSummaryBM):
        """Update the game state inside `prompt_tail` based on the latest game summary."""

        if not hasattr(self, "prompt_tail") or self.prompt_tail is None:
            raise ValueError("Prompt tail not initialized. Call `initialize_prompt_tail` first.")

        # Update all fields that come from GameSummaryBM
        self.prompt_tail["game_state"].update({
            "round_number": game_state_summary.round_number,
            "players_alive": game_state_summary.players_alive,
            "players_voted_off": game_state_summary.players_voted_off,
            "robot_players": game_state_summary.robot_players,
            "human_players": game_state_summary.human_players,
            "last_vote_outcome": game_state_summary.last_vote_outcome,
            "summary": game_state_summary.textual_summary
        })

        # Re-generate the JSON string after updating
        self.prompt_tail_json = json.dumps(self.prompt_tail, indent=4)

        self.logger.info(f"Updated prompt_tail: {self.prompt_tail_json}")
        return self.prompt_tail_json

    def decide_to_respond(self, message):
        """Determines whether AI should respond and what action to take."""
        
        response = self.decide_to_respond_chain.invoke({
            "system": self.system_prompt,
            "minutes": message,
            "game_state": self.prompt_tail_json
            })

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
        response = self.chose_action_chain.invoke({
            "system": self.system_prompt,
            "minutes": messages,
            "game_state": self.prompt_tail_json
            })
        
        action = self._parse_response(response, ActionOptionBM)
        self.logger.info(f"AI chose action: {action}")

        if action.introduce:
            return self.introduce(messages)
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
            "minutes": minutes,
            "game_state": self.prompt_tail_json
        })

        # We don't need to validate the response here, because it's a simple string
        self.logger.info(f"AI introduced itself: {introduction.content}")
        return introduction.content

    def defend(self, minutes):
        """Handles AI defense when accused.
        
        system
        accuser
        accusation
        current_dialogue

        """
        
        response = self.defend_chain.invoke({
            "system": self.system_prompt,
            "minutes": minutes,
            "game_state": self.prompt_tail_json,
        })

        defense = self._parse_response(response, DefendYourselfBM)

        return defense.response_text

    def accuse(self, minutes):
        """Handles AI accusation logic."""
        
        response = self.accuse_chain.invoke({
            "system": self.system_prompt,
            "minutes": minutes,
            "game_state": self.prompt_tail_json,
        })

        accusation = self._parse_response(response, AccusePlayerBM)

        return accusation.accusation_text

    def question(self, minutes):
        """Handles AI question logic."""
        
        response = self.question_chain.invoke({
            "system": self.system_prompt,
            "minutes": minutes,
            "game_state": self.prompt_tail_json,
        })

        question = self._parse_response(response, QuestionBM)

        return question.question_text
    
    def joke(self, minutes):
        """Handles AI joke logic."""
        # TODO Implement joke logic
        response = self.joke_chain.invoke({
            "system": self.system_prompt,
            "minutes": minutes,
            "game_state": self.prompt_tail_json,
        })

        joke = self._parse_response(response, JokeBM)
        return joke.joke_text
    
    def simple_phrase(self, minutes):
        """Handles AI simple phrase logic."""
        response = self.simple_phrase_chain.invoke({
            "system": self.system_prompt,
            "minutes": minutes,
            "game_state": self.prompt_tail_json,
        })
        phrase = self._parse_response(response, SimplePhraseBM)
        return phrase.phrase