GAME_RULES = """
GAME RULES:

There are 6 players: 3 humans and 3 AI imposters. Each AI is pretending to be one human player.

GOAL:
- Humans win if they vote out all 3 AI imposters after 3 rounds.
- If 1 AI survives after 3 rounds, it’s a partial win for the AIs.
- If 2 AIs survive after 3 rounds, the AIs win completely.

GAME PHASES:
1. **Info Phase**: All players (humans and AIs) fill out personal info.
2. **Intro Phase**: Players introduce themselves and learn that each human has an AI copy.
3. **Vote Phase**: Players vote to remove 1 player. AI players do not vote. Votes are secret, and \
    players don’t know if the removed player was human or AI.
4. **Discuss Phase**: The removed player is revealed. Players talk about the vote, share \
    suspicions, and try to spot the AIs.

Phases 3 and 4 repeat for 3 rounds. After that, all identities are revealed and the final result \
    (win, partial win, or loss) is shown.
"""