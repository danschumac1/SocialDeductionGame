from enum import Enum
from typing import Dict, List, Optional, Tuple
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
    hobby: str
    food: str
    anythingelse: str
    color: Tuple[int, int, int]

class DecideToRespondBM(BaseModel):
    directed_at_me: Optional[bool] = None
    introduced_self: Optional[bool] = None
    introducing_done: Optional[bool] = None
    accused: Optional[bool] = None

class ActionOptionBM(BaseModel):
    introduce: Optional[str] = None
    defend: Optional[str] = None
    accuse: Optional[str] = None
    joke: Optional[str] = None
    question: Optional[str] = None
    simple_phrase: Optional[str] = None
    context: Optional[str] = None  # Explanation for why this action was chosen

    @field_validator("introduce", "defend", "accuse", "joke", "question", "simple_phrase", mode="before")
    @classmethod
    def enforce_single_response(cls, v, info):
        """Ensures only one response field is populated."""
        if v is not None:
            filled_fields = [key for key, value in info.data.items() if value is not None]
            if len(filled_fields) > 1:
                raise ValueError(f"❌ Only one response can be provided at a time. Found: {filled_fields}")
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
            raise ValueError(f"❌ Only ONE defense choice can be selected. Given: {non_none_choices}")

class DefendYourselfBM(BaseModel):
    accuser: str
    accusation: str
    defense_choice: _DefenseChoices
    reasoning: str
    response_text: str # The AI's output for the chat

    def validate_defense(self):
        """Ensures the defense_choice is valid."""
        self.defense_choice.validate_single_choice()

class AccusePlayerBM(BaseModel):
    player_to_accuse: str  # The player being accused
    reasoning: str  # The AI's reasoning for the accusation
    response_text: str  # The AI's output for the chat
    previous_votes: Optional[List[str]]  # List of players this player has voted for

# Base Model for Jokes
class JokeBM(BaseModel):
    joke_text: str  # The joke AI wants to tell

# Base Model for Asking a Question
class QuestionBM(BaseModel):
    question_text: str  # The question AI asks
    context: Optional[str] = None  # Optional context for why the AI is asking

# Base Model for Simple Phrases (e.g., "I agree", "lol")
class SimplePhraseBM(BaseModel):
    phrase: str  # The short response AI gives

class _PlayerVotingHistory(BaseModel):
    player_name: str
    votes_cast: List[str]  # List of player names this player has voted for
    times_accused: int  # How many times this player has been accused

class GameSummaryBM(BaseModel):
    round_number: int
    players_alive: List[str] # List of players still in the game
    players_killed: List[str] # List of eliminated players (who & when)
    players_voted_off: List[str]  # List of players voted off 
    voting_history: Dict[str, _PlayerVotingHistory]  # Key = player name, Value = voting history
    robot_players: List[str]  # AI's knowledge of robot identities
    human_players: List[str]  
    last_vote_outcome: str  
    current_phase: Optional[str] = None
    textual_summary: str 
