from enum import Enum
from typing import List, Optional, Tuple
from pydantic import BaseModel, Field, field_validator

class GameState(Enum):
    MAIN_MENU = 0
    SETUP = 1
    PLAY = 2
    QUIT = 3

class Team(Enum):
    HUMAN = 0
    ROBOT = 1

class PersonaBM(BaseModel):
    name: str
    code_name: str
    hobby: str
    food: str
    anythingelse: str
    # raylib color
    color: Tuple[int, int, int, int] = Field(..., description="Raylib color in (R, G, B, A) format")

class DecideToRespondBM(BaseModel):
    directed_at_me: Optional[bool] = False
    havent_indroduced_self: Optional[bool] = False
    accused: Optional[bool] = False
    havent_answered_latest_icebreaker: Optional[bool] = False
    speak_up: Optional[bool] = False
    reasoning: str # Explanation for why this action was chosen

class ActionOptionBM(BaseModel):
    introduce: Optional[bool] = None
    defend: Optional[bool] = None
    accuse: Optional[bool] = None
    joke: Optional[bool] = None
    question: Optional[bool] = None
    simple_phrase: Optional[bool] = None
    reasoning: str = None  # Explanation for why this action was chosen

    @field_validator("introduce", "defend", "accuse", "joke", "question", "simple_phrase", mode="before")
    @classmethod
    def enforce_single_response(cls, v, info):
        """Ensures only one response field is populated."""
        if v is not None:
            filled_fields = [key for key, value in info.data.items() if value is not None]
            if len(filled_fields) > 1:
                raise ValueError(f"Only one response can be provided at a time. Found: {filled_fields}")
        return v
        
class _DefenseChoices(BaseModel):
    accuse: Optional[str] = None  # Redirect suspicion to another player
    deescalate: Optional[str] = None  # Reduce tension and shift focus
    be_dismissive: Optional[str] = None  # Minimize the accusation’s significance
    counter_evidence: Optional[str] = None  # Use voting history or logic to counter the claim
    seek_alliance: Optional[str] = None  # Convince a neutral player to back you up

    def validate_single_choice(self):
        """Ensures that only ONE choice is made."""
        choices = [self.accuse, self.deescalate, self.be_dismissive, self.counter_evidence, self.seek_alliance]
        non_none_choices = [choice for choice in choices if choice is not None]
        if len(non_none_choices) != 1:
            raise ValueError(f"Only ONE defense choice can be selected. Given: {non_none_choices}")

class DefendYourselfBM(BaseModel):
    accuser: str
    accusation: str
    defense_choice: _DefenseChoices
    reasoning: str
    accusation_text: str # The AI's output for the chat

    def validate_defense(self):
        """Ensures the defense_choice is valid."""
        self.defense_choice.validate_single_choice()

class AccusePlayerBM(BaseModel):
    player_to_accuse: str  # The player being accused
    reasoning: str  # The AI's reasoning for the accusation
    accusation_text: str  # The AI's output for the chat

# Base Model for Simple Phrases (e.g., "I agree", "lol")
class SimplePhraseBM(BaseModel):
    phrase: str  # The short response AI gives

class GameSummaryBM(BaseModel):
    round_number: int
    players_alive: List[str]        # List of players still in the game
    players_voted_off: List[str]    # List of players voted off
    last_vote_outcome: str  
    textual_summary: str  # A human-readable summary of the game's progression

class JokeBM(BaseModel):
    joke_text: str
    reasoning: str  # Why did the AI pick this joke? What does it hope to achieve?
    joke_target: Optional[str] = None  # Is this aimed at a player, game event, or topic?
    joke_tone: Optional[str] = "lighthearted"  # Could be: lighthearted, awkward, self-deprecating, etc.

class QuestionBM(BaseModel):
    question_text: str
    context: Optional[str] = None  # Existing context is still useful
    intent: str  # What does the AI want to achieve with this question?
    target_player: Optional[str] = None  # Who is the question aimed at, if anyone?
    strategy_type: Optional[str] = "information"  # Could be: information, pressure, humor