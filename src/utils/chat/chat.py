import json
from typing import List, Tuple, Union
from utils.chat.prompter import OpenAIPrompter
from utils.logging_utils import StandAloneLogger
from utils.chat.examples import (
    GENERIC_PROMPT_HEADERS, CHOOSE_ACTION_MAIN_HEADER, CHOSE_ACTION_EXAMPLES, 
    DEFEND_MAIN_HEADER, DEFEND_EXAMPLES, ACCUSE_MAIN_HEADER, ACCUSE_EXAMPLES, 
    DTR_EXAMPLES, DTR_MAIN_HEADER,GSU_HEADERS, INTRO_EXAMPLES, INTRO_MAIN_HEADER, INTRO_PROMPT_HEADERS, 
    JOKE_MAIN_HEADER, JOKE_EXAMPLES, QUESTION_MAIN_HEADER, QUESTION_EXAMPLES, 
    SIMPLE_PHRASE_MAIN_HEADER, SIMPLE_PHRASE_EXAMPLES, GSU_MAIN_HEADER, GSU_EXAMPLES
)
from utils.enums_dcs import (
    IntroBM, JokeBM, QuestionBM, SimplePhraseBM, Team, ActionOptionBM, DecideToRespondBM, 
    DefendYourselfBM, AccusePlayerBM, GameSummaryBM, PersonaBM
)

class AIPlayer:
    def __init__(
            self, code_name: str, color: Tuple[int, int, int, int], players_code_names: List[str],
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
        self.players_code_names = players_code_names
        self.team = Team.HUMAN
        self.voting_history = []
        self.has_introduced = False
        self.is_accused = False
        self.is_questioned = False
        self.humans_introduced = 0
        self.persona = self._steal_persona(persona_to_steal)
        self.system_prompt = (
            "You are a middle schooler playing a social deduction game with your friends. " 
            "You are a human trying to figure out who the AI players are. " 
            "You must convince the other players that you are human while "
            "trying to identify the AI players. "
            "Your persona is: " + self.persona.model_dump_json()
        )
        self.game_summary = self._initialize_game_summary()

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
            "introduce": OpenAIPrompter(
                openai_dict_key="OPENAI_API_KEY",
                system_prompt=self.system_prompt,
                examples=INTRO_EXAMPLES,
                prompt_headers=GENERIC_PROMPT_HEADERS,
                output_format=IntroBM,
                main_prompt_header=INTRO_MAIN_HEADER
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
            "game_summary_update": OpenAIPrompter(
                openai_dict_key="OPENAI_API_KEY",
                system_prompt=self.system_prompt,
                examples=GSU_EXAMPLES,
                prompt_headers=GSU_HEADERS,
                output_format=GameSummaryBM,
                main_prompt_header=GSU_MAIN_HEADER
            )
        }
    def _initialize_game_summary(self) -> str:
        """Initializes the game summary for the AI player."""
        self.game_summary = GameSummaryBM(
            round_number=0,
            players_alive=self.players_code_names,
            players_voted_off=[],
            last_vote_outcome="N/A",
            textual_summary="The game has started. Players are introducing themselves."
        ).model_dump_json()
        return self.game_summary

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
        print("--- decide_to_respond ---")
        """Determines whether AI should respond and what action to take."""
        # print("MINUTES:", "\n".join(minutes))

        #  Get AI's decision
        response_json = self.prompter_dict["decide_to_respond"].get_completion({
            "minutes": minutes,
            "game_summary": self.game_summary
            })
        # print("\tresponse_json:", response_json)

        #  Ensure response_json is a string before validation
        decision = DecideToRespondBM.model_validate_json(json.dumps(response_json))

        #  Check if AI needs to introduce itself
        if not self.has_introduced and decision.havent_indroduced_self:
            introduction = self.introduce(minutes)
            return introduction

        #  AI should respond if spoken to or accused
        if decision.directed_at_me or decision.accused:
            return self.choose_action(minutes)

        return "Wait for next message"

    def choose_action(self, minutes: List[str]):
        """Determines the best action to take based on the minutes and game summary."""
        print("--- CHOOSE ACTION ---")
        response_json = self.prompter_dict["choose_action"].get_completion({
            "minutes": minutes,
            "game_summary": self.game_summary
        })
        action = ActionOptionBM.model_validate_json(json.dumps(response_json))

        if action.introduce:
            return self.introduce(minutes)
        elif action.defend:
            return self.defend(minutes)
        elif action.accuse:
            return self.accuse(minutes)
        elif action.joke:
            return self.joke(minutes)
        elif action.question:
            return self.question(minutes)
        else: # if action.simple_phrase or error
            return self.simple_phrase(minutes)


    def introduce(self, minutes: List[str]):
        """Introduces the AI player to the game."""
        print("--- INTRODUCE ---")
        response_json = self.prompter_dict["introduce"].get_completion({
            "minutes": minutes,
            "game_summary": self.game_summary
        })
        # print("INTRO RESPONSE:", response_json)
        self.has_introduced = True
        # print(type(response_json))
        return IntroBM.model_validate_json(json.dumps(response_json)).output_text
    
    def defend(self, minutes: List[str]):
        print("--- DEFEND ---")
        """Defends the AI player from accusations."""
        response_json = self.prompter_dict["defend"].get_completion({
            "minutes": minutes,
            "game_summary": self.game_summary
        })
        return DefendYourselfBM.model_validate_json(json.dumps(response_json)).output_text
    
    def accuse(self, minutes: List[str]):
        """Accuses another player of being a robot."""
        print("--- ACCUSE ---")
        response_json = self.prompter_dict["accuse"].get_completion({
            "minutes": minutes,
            "game_summary": self.game_summary
        })
        return AccusePlayerBM.model_validate_json(json.dumps(response_json)).output_text
    
    def joke(self, minutes: List[str]):
        """Tells a joke to lighten the mood."""
        print("--- JOKE ---")
        response_json = self.prompter_dict["joke"].get_completion({
            "minutes": minutes,
            "game_summary": self.game_summary
        })
        return JokeBM.model_validate_json(json.dumps(response_json)).output_text
    
    def question(self, minutes: List[str]):
        """Asks another player a question."""
        print("--- QUESTION ---")
        response_json = self.prompter_dict["question"].get_completion({
            "minutes": minutes,
            "game_summary": self.game_summary
        })
        return QuestionBM.model_validate_json(json.dumps(response_json)).output_text
    
    def simple_phrase(self, minutes: List[str]):
        """Says a simple phrase to keep the conversation going."""
        print("--- SIMPLE PHRASE ---")
        response_json = self.prompter_dict["simple_phrase"].get_completion({
            "minutes": minutes,
            "game_summary": self.game_summary
        })
        return SimplePhraseBM.model_validate_json(json.dumps(response_json)).output_text
    
    def game_summary_update(self, minutes: List[str], vote_result: dict, game_summary):
        """Updates the game state based on vote results and discussion."""
        print("--- GAME SUMMARY UPDATE ---")
        response_json = self.prompter_dict["game_summary_update"].get_completion({
            "minutes": "\n".join(minutes),
            "game_summary": json.loads(game_summary.model_dump_json()),  #  Convert JSON string back into dict
            "vote_result": vote_result  # Already a dict, no need to modify
        })
        updated_game_summary = GameSummaryBM.model_validate_json(json.dumps(response_json))
        self.game_summary = json.loads(updated_game_summary.model_dump_json())

    