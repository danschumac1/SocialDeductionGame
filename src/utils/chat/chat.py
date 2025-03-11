import json
from typing import List, Tuple, Union
from utils.chat.prompter import OpenAIPrompter
from utils.logging_utils import StandAloneLogger
from utils.chat.examples import (
    GENERIC_PROMPT_HEADERS,
    CHOOSE_ACTION_MAIN_HEADER, CHOSE_ACTION_EXAMPLES, 
    DEFEND_MAIN_HEADER, DEFEND_EXAMPLES,
    ACCUSE_MAIN_HEADER, ACCUSE_EXAMPLES, 
    DTR_EXAMPLES, DTR_MAIN_HEADER,
    GSU_HEADERS,
    JOKE_MAIN_HEADER, JOKE_EXAMPLES,
    QUESTION_MAIN_HEADER, QUESTION_EXAMPLES,
    SIMPLE_PHRASE_MAIN_HEADER, SIMPLE_PHRASE_EXAMPLES,
    GSU_MAIN_HEADER, GSU_EXAMPLES
)
from utils.enums_dcs import (
    JokeBM, QuestionBM, SimplePhraseBM, Team, ActionOptionBM, DecideToRespondBM, 
    DefendYourselfBM, AccusePlayerBM, GameSummaryBM, PersonaBM
)

class AIPlayer:
    def __init__(
            self, code_name: str, color: Tuple[int, int, int, int], 
            persona_to_steal: Union[None, PersonaBM]):
        """Initializes AI player with a generated or stolen persona."""
        self.code_name = code_name
        self.color = color
        self.logger = StandAloneLogger(
            log_path=f"./logs/ai_{self.code_name}.log",
            clear=True,
            init=True
        )
        self.prompt_tail = None

        # AI Persona
        self.persona = self._steal_persona(persona_to_steal)
        self.system_prompt = (
            "You are a middle schooler playing a social deduction game with your friends. " 
            "You are a human trying to figure out who the robots are. " 
            "You must convince the other players that you are human while "
            "trying to identify the robots. "
            "Your persona is: " + self.persona.model_dump_json()
        )
        self.team = Team.HUMAN
        self.voting_history = []
        self.has_introduced = False
        self.is_accused = False
        self.is_questioned = False
        self.humans_introduced = 0

        # Initialize custom prompter_dict
        self.prompter_dict = {
            "choose_action": OpenAIPrompter(
                openai_dict_key="OPENAI_API_KEY",
                system_prompt=self.system_prompt,
                examples=CHOSE_ACTION_EXAMPLES,
                prompt_headers=GENERIC_PROMPT_HEADERS,
                output_format=ActionOptionBM,
                main_prompt_header=CHOOSE_ACTION_MAIN_HEADER
            ),
            "defend": OpenAIPrompter(
                openai_dict_key="OPENAI_API_KEY",
                system_prompt=self.system_prompt,
                examples=DEFEND_EXAMPLES,
                prompt_headers=GENERIC_PROMPT_HEADERS,
                output_format=DefendYourselfBM,
                main_prompt_header=DEFEND_MAIN_HEADER
            ),
            "accuse": OpenAIPrompter(
                openai_dict_key="OPENAI_API_KEY",
                system_prompt=self.system_prompt,
                examples=ACCUSE_EXAMPLES,
                prompt_headers=GENERIC_PROMPT_HEADERS,
                output_format=AccusePlayerBM,
                main_prompt_header=ACCUSE_MAIN_HEADER
            ),
            "joke": OpenAIPrompter(
                openai_dict_key="OPENAI_API_KEY",
                system_prompt=self.system_prompt,
                examples=JOKE_EXAMPLES,
                prompt_headers=GENERIC_PROMPT_HEADERS,
                output_format=JokeBM,
                main_prompt_header=JOKE_MAIN_HEADER
            ),
            "question": OpenAIPrompter(
                openai_dict_key="OPENAI_API_KEY",
                system_prompt=self.system_prompt,
                examples=QUESTION_EXAMPLES,
                prompt_headers=GENERIC_PROMPT_HEADERS,
                output_format=QuestionBM,
                main_prompt_header=QUESTION_MAIN_HEADER
            ),
            "simple_phrase": OpenAIPrompter(
                openai_dict_key="OPENAI_API_KEY",
                system_prompt=self.system_prompt,
                examples=SIMPLE_PHRASE_EXAMPLES,
                prompt_headers=GENERIC_PROMPT_HEADERS,
                output_format=SimplePhraseBM,
                main_prompt_header=SIMPLE_PHRASE_MAIN_HEADER
            ),
            "decide_to_respond": OpenAIPrompter(
                openai_dict_key="OPENAI_API_KEY",
                system_prompt=self.system_prompt,
                examples=DTR_EXAMPLES,
                prompt_headers=GENERIC_PROMPT_HEADERS,
                output_format=DecideToRespondBM,
                main_prompt_header=DTR_MAIN_HEADER
            ),
            "game_state_update": OpenAIPrompter(
                openai_dict_key="OPENAI_API_KEY",
                system_prompt=self.system_prompt,
                examples=GSU_EXAMPLES,
                prompt_headers=GSU_HEADERS,
                output_format=GameSummaryBM,
                main_prompt_header=GSU_MAIN_HEADER
            )
        }
    def _steal_persona(self, persona: PersonaBM) -> PersonaBM:
        """Creates a modified copy of the human persona instead of modifying the original."""
        stolen_persona = PersonaBM(
            name=persona.name,
            code_name=self.code_name,
            color=self.color,
            hobby=persona.hobby,
            food=persona.food,
            anythingelse=persona.anythingelse
        )
        self.logger.info(f"Stolen persona: {stolen_persona}")
        return stolen_persona

    def decide_to_respond(self, minutes: List[str]):
        """Determines whether AI should respond and what action to take."""
        print("MINUTES:", "\n".join(minutes))

        #  Get AI's decision
        response_json = self.prompter_dict["decide_to_respond"].get_completion({"minutes": minutes})
        print("\tresponse_json:", response_json)

        #  Ensure response_json is a string before validation
        decision = DecideToRespondBM.model_validate_json(json.dumps(response_json))

        #  Check if AI needs to introduce itself
        if not self.has_introduced and decision.havent_indroduced_self:
            introduction = self.introduce()
            self.has_introduced = True
            return introduction

        #  AI should respond if spoken to or accused
        if decision.directed_at_me or decision.accused:
            return self.choose_action({"minutes": message})

        return "Wait for next message"


    def choose_action(self, minutes: List[str]):
        """Determines the best action to take based on the game state."""

        response_json = self.prompter_dict["choose_action"].get_completion("\n".join(minutes))
        action = ActionOptionBM.model_validate_json(json.dumps(response_json))


        if action.introduce:
            return self.introduce()
        elif action.defend:
            return self.defend(minutes)
        elif action.accuse:
            return self.accuse(action.accuse)
        elif action.joke:
            return self.joke()
        elif action.question:
            return self.question()
        else: # we need to respond no matter what. 
            return self.simple_phrase()

    def introduce(self):
        """Handles AI introduction logic."""
        try:
            response_json = self.prompter_dict["choose_action"].get_completion(self.code_name)
            introduction = SimplePhraseBM.model_validate_json(response_json)
            self.logger.info(f"AI introduced itself: {introduction.phrase}")
            return introduction.phrase
        except Exception as e:
            self.logger.error(f"Error in introduce: {e}")
            return "Hey, I'm here!"

    def game_state_update(self, minutes: List[str], vote_result: dict, game_state):
        """Updates the game state based on vote results and discussion."""
        response_json = self.prompter_dict["game_state_update"].get_completion({
            "minutes": "\n".join(minutes),
            "game_state": json.loads(game_state.model_dump_json()),  #  Convert JSON string back into dict
            "vote_result": vote_result  # Already a dict, no need to modify
        })
        updated_game_state = GameSummaryBM.model_validate_json(response_json)
        return updated_game_state

    