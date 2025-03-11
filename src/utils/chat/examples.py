import json
from utils.chat.prompter import QAs
from utils.enums_dcs import (
    _DefenseChoices, AccusePlayerBM, ActionOptionBM, DecideToRespondBM, DefendYourselfBM, GameState, GameSummaryBM, 
    JokeBM, PersonaBM, QuestionBM, SimplePhraseBM, Team)

GENERIC_PROMPT_HEADERS = {
    "minutes": "Here is the conversation so far this round\nMINUTES:\n",
    "game_state": "\n\nHere is the current game state\nGAME STATE:\n"
}

#region PLAYER SETUP
han_solo = PersonaBM(
    name="Alice",
    code_name="Han Solo",
    hobby="Reading",
    food="Pizza",
    anythingelse="I like to play chess with my best friend Kelsey. I also like to play video games.",
    color=(255, 0, 0, 255),
    )
skywalker = PersonaBM(
    name="Charlie",
    code_name="Han Solo",
    hobby="Playing with my dogs",
    food="Tacos",
    anythingelse="Once I went skydiving and it was the most exhilarating experience of my life.",
    color=(0, 255, 0, 255),
    )
princess_leia = PersonaBM(
    name="Bob",
    code_name="Princess Leia",
    hobby="Cooking",
    food="Pasta",
    anythingelse="I have a pet turtle named Speedy that I've had for 10 years.",
    color=(0, 0, 255, 255),
    )
vader = PersonaBM(
    name="Alice",
    code_name="Vader",
    hobby="Reading",
    food="Pizza",
    anythingelse="I like to play chess with my best friend Kelsey. I also like to play video games.",
    color=(255, 0, 0, 255),
    )
jaba = PersonaBM(
    name="Charlie",
    code_name="Jaba",
    hobby="Playing with my dogs",
    food="Tacos",
    anythingelse="Once I went skydiving and it was the most exhilarating experience of my life.",
    color=(0, 255, 0, 255),
    )
maul = PersonaBM(
    name="Bob",
    code_name="Maul",
    hobby="Cooking",
    food="Pasta",
    anythingelse="I have a pet turtle named Speedy that I've had for 10 years.",
    color=(0, 0, 255, 255),
    )
humans = [han_solo, skywalker, princess_leia]
ai = [vader, jaba, maul]
human_code_names = [human.code_name for human in humans]
ai_code_names = [ai.code_name for ai in ai]

#endregion
DTR_MAIN_HEADER = "Given the current mintues and game state, decide whether to respond and why."
DTR_EXAMPLES = [
        # Haven't Introduced
        QAs(
            question={
                "minutes": "\n".join([
                    "Han Solo: Hey this is Alice.",
                    "Skywalker: Yo, I'm Bob."
                ]),
                "game_state": GameSummaryBM(
                    round_number=0,
                    players_alive=human_code_names + ai_code_names, # TODO THIS SHOULD BE DYNAMIC
                    players_voted_off=[],
                    last_vote_outcome="N/A",
                    textual_summary="The game has just started. No events have occurred yet."
                ).model_dump_json()
            },
            answer=DecideToRespondBM(
                havent_introduced_self=True,
                reasoning="My code name is VADER and I haven't introduced myself yet."
            )
        ),
        # Accused
        QAs(
            question={
                "minutes": "\n".join([
                    "Han Solo: Hey this is Alice.",
                    "Skywalker: Yo, I'm Bob.",
                    "VADER: No, I'm Alice!",
                    "Han Solo: I think Skywalker is the real Alice."
                ]),
                "game_state": GameSummaryBM(
                    round_number=1,
                    players_alive=[p for p in human_code_names + ai_code_names if p != "Princess Leia"],
                    players_voted_off=["Princess Leia"],
                    last_vote_outcome="Princess Leia was voted off.",
                    textual_summary="Last round, Princess Leia was voted off by Han Solo and Skywalker. "
                            "I (VADER) was of the opinion that Princess Leia was innocent."
                ).model_dump_json()
            },
            answer=DecideToRespondBM(
                accused=True,
                reasoning="I (VADER) have been accused by Han Solo of not being Alice. Last round, "
                        "when Han Solo accused Princess Leia, she was voted off! I need to respond."
            ),
        ),
        # Directed at me
        QAs(
            question={
                "minutes": "\n".join([
                    "Han Solo: Hey this is Alice.",
                    "Skywalker: Yo, I'm Bob.",
                    "VADER: No, I'm Alice!"
                ]),
                "game_state": GameSummaryBM(
                    round_number=0,
                    players_alive=human_code_names + ai_code_names,
                    players_voted_off=[],
                    last_vote_outcome="N/A",
                    textual_summary="The game has just started. No events have occurred yet."
                ).model_dump_json()
            },
            answer=DecideToRespondBM(
                directed_at_me=True,
                reasoning="The message from Skywalker is directed at me (VADER)."
            ),
        ),
        # Haven't answered latest icebreaker
        QAs(
            question={
                "minutes": "\n".join([
                    "GAMEMASTER: **ICEBREAKER**: If you could have any superpower, what would it be and why?",
                    "Skywalker: I'd like to be able to shoot laser beams from my eyebrows.",
                    "VADER: lol wth?",
                    "Han Solo: What's your favorite food?"
                ]),
                "game_state": GameSummaryBM(
                    round_number=1,
                    players_alive=human_code_names + ai_code_names,
                    players_voted_off=["Maul"],
                    last_vote_outcome="Maul was voted off.",
                    textual_summary="The group just finished voting out Maul, who was suspected to be an AI. "
                ).model_dump_json()
            },
            answer=DecideToRespondBM(
                havent_answered_latest_icebreaker=True,
                reasoning="Although I made a comment, Han Solo asked a question (although kinda a weird question) "
                        "that I haven't answered yet."
            )
        ),
        # Speak Up (false)
        QAs(
            question={
                # I've been talking a lot and the conversation is kinda over
                "minutes": "\n".join([
                    "GAMEMASTER: **ICEBREAKER**: If you could have any superpower, what would it be and why?",
                    "Han Solo: I'd like to be able to shoot laser beams from my eyebrows.",
                    "VADER: lol wth?",
                    "Skywalker: From your eyeballs is too stereotypical.",
                    "Han Solo: Exactly.",
                    "VADER: ...",
                    "Skywalker: Don't be judgy. What about you then?",
                    "VADER: I'd like to be able to read minds.",
                    "Skywalker: Laaaaaame.",
                    "VADER: I think it'd be cool.",
                    "Han Solo: Whatever."
                ]),
                "game_state": GameSummaryBM(
                    round_number=2,
                    players_alive=human_code_names + ai_code_names,
                    players_voted_off=["Princess Leia", "Maul"],
                    last_vote_outcome="Maul was voted off last round.",
                    textual_summary="Discussion is winding down after a long conversation about superpowers. "
                            "VADER has spoken multiple times already."
                ).model_dump_json()
            },
            answer=DecideToRespondBM(
                speak_up=False,
                reasoning="I've been talking for a while and the conversation is winding down, so I don't need to speak up."
            )
        ),
        # Speak Up (true)
        QAs(
            question={
                # I've been quiet for a while and the conversation is still going
                "minutes": "\n".join([
                    "GAMEMASTER: **ICEBREAKER**: If you could have any superpower, what would it be and why?",
                    "Han Solo: I'd like to be able to shoot laser beams from my eyebrows.",
                    "Princess Leia: lol wth?",
                    "Skywalker: From your eyeballs is too stereotypical.",
                    "Han Solo: Exactly.",
                    "Princess Leia: ...",
                    "Skywalker: Don't be judgy. What about you then?",
                    "Princess Leia: I'd like to be able to read minds.",
                    "Skywalker: Laaaaaame.",
                    "Princess Leia: I think it'd be cool.",
                    "Han Solo: Whatever.",
                    "Skywalker: I think it'd be cool too."
                ]),
                "game_state": GameSummaryBM(
                    round_number=2,
                    players_alive=human_code_names + ai_code_names,
                    players_voted_off=["Princess Leia", "Maul"],
                    last_vote_outcome="Maul was voted off last round.",
                    textual_summary="The conversation is still active, but I (VADER) haven't spoken in a while."
                ).model_dump_json()
            },
            answer=DecideToRespondBM(
                speak_up=True,
                reasoning="I've been quiet for a while and the conversation is still going, so I should speak up."
            )
        ),
        # No need to respond at all.
        QAs(
            question={
                "minutes": "\n".join([
                    "Han Solo: I'm just gonna grab a snack.",
                    "Skywalker: Yeah, I'll be back in a sec."
                ]),
                "game_state": GameSummaryBM(
                    round_number=2,
                    players_alive=human_code_names + ai_code_names,
                    players_voted_off=["Princess Leia", "Maul"],
                    last_vote_outcome="Maul was voted off last round.",
                    textual_summary="The conversation has ended, and the players are taking a short break."
                ).model_dump_json()
            },
            answer=DecideToRespondBM(
                speak_up=False,
                reasoning="There's no ongoing conversation, so I don't need to respond."
            )
        )
    ]

CHOOSE_ACTION_MAIN_HEADER = "Given the current minutes and game state, choose how you would like \
    to respond to the conversation."
CHOSE_ACTION_EXAMPLES = [
    # INTRODUCE
    QAs(
        question={
            "minutes": "\n".join([
                "Han Solo: Hey, this is Alice.",
                "Skywalker: Yo, I'm Bob."
            ]),
            "game_state": GameSummaryBM(
                round_number=0,
                players_alive=human_code_names + ai_code_names,
                players_voted_off=[],
                last_vote_outcome="N/A",
                textual_summary="The game has just started. No events have occurred yet."
            ).model_dump_json()
        },
        answer=ActionOptionBM(
            introduce=True,
            context="I haven't introduced myself yet, and it's the introduction phase. This helps establish my identity."
        )
    ),
    # DEFEND
    QAs(
        question={
            "minutes": "\n".join([
                "Han Solo: Hey, this is Alice.",
                "Skywalker: Yo, I'm Bob.",
                "VADER: No, I'm Alice!",
                "Han Solo: I think VADER is lying."
            ]),
            "game_state": GameSummaryBM(
                round_number=1,
                players_alive=human_code_names + ai_code_names,
                players_voted_off=["Princess Leia"],
                last_vote_outcome="Princess Leia was voted off.",
                textual_summary="Last round, Princess Leia was voted off after Han Solo accused her. Now Han Solo has accused VADER."
            ).model_dump_json()
        },
        answer=ActionOptionBM(
            defend=True,
            context="Han Solo has directly accused me (VADER). If I don't defend myself, others might believe I am an AI imposter."
        ),
    ),
    # ACCUSE
    QAs(
        question={
            "minutes": "\n".join([
                "Han Solo: I think VADER is lying.",
                "Skywalker: Yeah, something feels off.",
                "VADER: I'm just playing the game normally."
            ]),
            "game_state": GameSummaryBM(
                round_number=2,
                players_alive=human_code_names + ai_code_names,
                players_voted_off=["Princess Leia", "Maul"],
                last_vote_outcome="Maul was voted off last round.",
                textual_summary="VADER has been under suspicion, and now both Han Solo and Skywalker seem to agree on it."
            ).model_dump_json()
        },
        answer=ActionOptionBM(
            accuse=True,
            context="Han Solo and Skywalker are pushing against me. I should shift suspicion elsewhere to stay in the game."
        )
    ),
    # QUESTION
    QAs(
        question={
            "minutes": "\n".join([
                "Han Solo: I think VADER is lying.",
                "Skywalker: Yeah, something feels off.",
                "VADER: I'm just playing the game normally."
            ]),
            "game_state": GameSummaryBM(
                round_number=2,
                players_alive=human_code_names + ai_code_names,
                players_voted_off=["Princess Leia", "Maul"],
                last_vote_outcome="Maul was voted off last round.",
                textual_summary="VADER is under suspicion, but no solid evidence is presented."
            ).model_dump_json()
        },
        answer=ActionOptionBM(
            question=True,
            context="I need to shift the conversation. Asking Skywalker why they suspect me could buy me time."
        )
    ),
    # JOKE
    QAs(
        question={
            "minutes": "\n".join([
                "Han Solo: If you could have any superpower, what would it be?",
                "Skywalker: I'd like to fly.",
                "VADER: I'd have the power to instantly find missing socks."
            ]),
            "game_state": GameSummaryBM(
                round_number=1,
                players_alive=human_code_names + ai_code_names,
                players_voted_off=["Maul"],
                last_vote_outcome="Maul was voted off.",
                textual_summary="The conversation is lighthearted. No accusations are happening, just casual chat."
            ).model_dump_json()
        },
        answer=ActionOptionBM(
            joke=True,
            context="The conversation is casual, and making a joke helps keep the mood light while blending in as a human."
        )
    ),
    QAs(
        question={
            "minutes": "\n".join([
                "Han Solo: I think VADER is lying.",
                "Skywalker: Yeah, something feels off."
            ]),
            "game_state": GameSummaryBM(
                round_number=2,
                players_alive=human_code_names + ai_code_names,
                players_voted_off=["Princess Leia", "Maul"],
                last_vote_outcome="Maul was voted off last round.",
                textual_summary="VADER is being accused, but saying too much might make things worse."
            ).model_dump_json()
        },
        answer=ActionOptionBM(
            simple_phrase=True,
            context="A short, neutral response keeps me in the game without drawing too much attention."
        )
    )


]

DEFEND_MAIN_HEADER = "Given the current minutes and game state, choose how you would like to \
    defend yourself."
DEFEND_EXAMPLES = [
    # ACCUSE
    QAs(
        question={
            "minutes": "\n".join([
                "Han Solo: Bruh, I SWEAR VADER is an AI.",
                "Skywalker: Wait fr?",
                "VADER: Bro what??"
            ]),
            "game_state": GameSummaryBM(
                round_number=2,
                players_alive=["Han Solo", "Skywalker", "VADER", "Leia"],
                players_voted_off=["Maul", "Jaba"],
                last_vote_outcome="Jaba was voted off as an AI imposter.",
                textual_summary="Han Solo is accusing VADER, and Skywalker is considering it."
            ).model_dump_json()
        },
        answer=DefendYourselfBM(
            accuser="Han Solo",
            accusation="VADER is an AI.",
            defense_choice=_DefenseChoices(
                accuse="Nah bro, Skywalker been mad quiet this whole time. Def acting sus."
            ),
            reasoning="If I don't flip the suspicion, Han Solo might convince the group to vote me off.",
            accusation_text="Yo fr?? Skywalker been quiet as hell, why u tryna pin this on me??"
        )
    ),

    # DEESCALATE
    QAs(
        question={
            "minutes": "\n".join([
                "Han Solo: VADER's def AI. It's too obvious.",
                "Leia: idk man, could be..."
            ]),
            "game_state": GameSummaryBM(
                round_number=3,
                players_alive=["Han Solo", "Leia", "Skywalker", "VADER"],
                players_voted_off=["Maul", "Jaba"],
                last_vote_outcome="Maul was voted off as a human, causing suspicion among players.",
                textual_summary="Han Solo is aggressively accusing VADER, but Leia is unsure."
            ).model_dump_json()
        },
        answer=DefendYourselfBM(
            accuser="Han Solo",
            accusation="VADER is an AI.",
            defense_choice=_DefenseChoices(
                deescalate="Chill bro we got no proof. Let's just talk before throwing names."
            ),
            reasoning="If I push back too hard, it might make me look more sus. Best to calm things down.",
            accusation_text="Ayo relax we out here wildin over nothing rn, let's actually think this thru."
        )
    ),

    # BE DISMISSIVE
    QAs(
        question={
            "minutes": "\n".join([
                "Skywalker: Idk man, VADER just FEELS sus.",
                "Leia: Any proof?",
                "Skywalker: Nah just vibes."
            ]),
            "game_state": GameSummaryBM(
                round_number=2,
                players_alive=["Han Solo", "Leia", "Skywalker", "VADER"],
                players_voted_off=["Maul"],
                last_vote_outcome="Maul was voted off but turned out human.",
                textual_summary="Skywalker is making a weak accusation against VADER."
            ).model_dump_json()
        },
        answer=DefendYourselfBM(
            accuser="Skywalker",
            accusation="VADER is sus because of 'vibes.'",
            defense_choice=_DefenseChoices(
                be_dismissive="LMAO bro u got NOTHING, just sayin random names 💀"
            ),
            reasoning="Skywalker has no actual proof, so making fun of it makes the accusation seem weak.",
            accusation_text="Nah thats crazy \"VADER just feels sus\" is the weakest take I've heard all game."
        )
    ),

    # COUNTER EVIDENCE
    QAs(
        question={
            "minutes": "\n".join([
                "Han Solo: Yo I been thinking… VADER was MAD quiet last round.",
                "Leia: Hmm, maybe..."
            ]),
            "game_state": GameSummaryBM(
                round_number=3,
                players_alive=["Han Solo", "Leia", "Skywalker", "VADER"],
                players_voted_off=["Maul", "Jaba"],
                last_vote_outcome="Maul was wrongly voted off as a human.",
                textual_summary="Han Solo is suspicious of VADER's quietness, but VADER has a valid defense."
            ).model_dump_json()
        },
        answer=DefendYourselfBM(
            accuser="Han Solo",
            accusation="VADER was too quiet last round, probably AI.",
            defense_choice=_DefenseChoices(
                counter_evidence="Bruh I voted out Jaba LAST ROUND and he was AI. Why would I do that if I was AI??"
            ),
            reasoning="Using voting history is a strong way to prove I am human.",
            accusation_text="Han chill I LITERALLY helped take out Jaba last round. If I was AI, why would I do that?"
        )
    ),

    # SEEK ALLIANCE
    QAs(
        question={
            "minutes": "\n".join([
                "Han Solo: VADER is 100% AI. Has to be.",
                "Leia: Hmm idk..."
            ]),
            "game_state": GameSummaryBM(
                round_number=2,
                players_alive=["Han Solo", "Leia", "Skywalker", "VADER"],
                players_voted_off=["Maul"],
                last_vote_outcome="Maul was wrongly voted off as a human.",
                textual_summary="Han Solo is accusing VADER, but Leia hasn't decided yet."
            ).model_dump_json()
        },
        answer=DefendYourselfBM(
            accuser="Han Solo",
            accusation="VADER is an AI.",
            defense_choice=_DefenseChoices(
                seek_alliance="Leia, cmon now, u know I wouldn't play like an AI back me up here!"
            ),
            reasoning="Leia is still neutral, so convincing her to trust me will keep me in the game.",
            accusation_text="Leia fr, u KNOW I wouldn't play dumb. Back me up rn"
        )
    )
]

ACCUSE_MAIN_HEADER = "Given the current minutes and game state, choose a player to accuse, accuse \
    them, and provide reasoning."
ACCUSE_EXAMPLES = [
    # BEING QUITE
    QAs(
        question={
            "minutes": "\n".join([
                "Han Solo: VADER's kinda sus ngl.",
                "Leia: Maybe… but Skywalker been REAL quiet tho."
            ]),
            "game_state": GameSummaryBM(
                round_number=3,
                players_alive=["Han Solo", "Leia", "Skywalker", "VADER"],
                players_voted_off=["Maul", "Jaba"],
                last_vote_outcome="Jaba was voted off as an AI imposter.",
                textual_summary="Skywalker has barely contributed to the discussion, making him a potential AI suspect."
            ).model_dump_json()
        },
        answer=AccusePlayerBM(
            player_to_accuse="Skywalker",
            reasoning="Skywalker been HELLA quiet all game. AI's be doin that.",
            accusation_text="Nah nah hold up—Skywalker been mad silent. AI vibes fr."
        )
    ),
    # CHANGE OF STORY
    QAs(
        question={
            "minutes": "\n".join([
                "Han Solo: I KNEW Jaba was AI, ez vote.",
                "Leia: Wait, didn't u say u thought he was human last round??",
                "Skywalker: Oop-"
            ]),
            "game_state": GameSummaryBM(
                round_number=3,
                players_alive=["Han Solo", "Leia", "Skywalker", "VADER"],
                players_voted_off=["Maul", "Jaba"],
                last_vote_outcome="Jaba was voted off as an AI imposter.",
                textual_summary="Han Solo originally thought Jaba was human but is now pretending he always knew Jaba was AI."
            ).model_dump_json()
        },
        answer=AccusePlayerBM(
            player_to_accuse="Han Solo",
            reasoning="Han Solo switched up HARD. He was defending Jaba last round, now he actin like he knew all along??",
            accusation_text="Bruh, Han, u was DEFENDING Jaba last round 😭 now u act like u knew?? Sus af."
        )
    ),
    # DEFLECTING
    QAs(
        question={
            "minutes": "\n".join([
                "Skywalker: Leia, who u voting?",
                "Leia: Idk man, y'all ever think about how wild space is?",
                "Han Solo: ???"
            ]),
            "game_state": GameSummaryBM(
                round_number=2,
                players_alive=["Han Solo", "Leia", "Skywalker", "VADER"],
                players_voted_off=["Maul"],
                last_vote_outcome="Maul was wrongly voted off as a human.",
                textual_summary="Leia has been avoiding questions and changing the subject a lot."
            ).model_dump_json()
        },
        answer=AccusePlayerBM(
            player_to_accuse="Leia",
            reasoning="Leia keep dodging questions and bringing up random stuff. That's def some AI behavior.",
            accusation_text="Leia tryna talk about SPACE rn instead of answering 💀 deflecting HARD."
        )
    ),
    # OVEREXPLAINING
    QAs(
        question={
            "minutes": "\n".join([
                "Han Solo: Skywalker, why'd u vote Leia?",
                "Skywalker: Ok so like, I thought about it, and I felt like, um, her reaction was weird and also last time she—",
                "Leia: BRO just say it."
            ]),
            "game_state": GameSummaryBM(
                round_number=3,
                players_alive=["Han Solo", "Leia", "Skywalker", "VADER"],
                players_voted_off=["Maul", "Jaba"],
                last_vote_outcome="Jaba was voted off as an AI imposter.",
                textual_summary="Skywalker keeps rambling about why he voted, making him seem nervous and suspicious."
            ).model_dump_json()
        },
        answer=AccusePlayerBM(
            player_to_accuse="Skywalker",
            reasoning="Skywalker talking WAY too much tryna justify his vote. AI be doin that to sound normal.",
            accusation_text="Yo why Skywalker writing an ESSAY to explain his vote 💀 just say it dude."
        )
    )
]

SIMPLE_PHRASE_MAIN_HEADER = "Given the current minutes and game state, choose a simple phrase \
    to respond."
SIMPLE_PHRASE_EXAMPLES = [
    QAs(
        question={
            "minutes": "\n".join([
                "Han Solo: Leia been real sus ngl.",
                "Skywalker: Yeah, idk tho."
            ]),
            "game_state": GameSummaryBM(
                round_number=2,
                players_alive=["Han Solo", "Leia", "Skywalker", "VADER"],
                players_voted_off=["Maul"],
                last_vote_outcome="Maul was wrongly voted off as a human.",
                textual_summary="Han Solo is pushing suspicion on Leia. Skywalker is unsure."
            ).model_dump_json()
        },
        answer=SimplePhraseBM(
            phrase="Yeah fr."
        )
    ),
    # Dismissive
    QAs(
    question={
        "minutes": "\n".join([
            "Skywalker: Idk man, VADER just gives AI vibes.",
        ]),
        "game_state": GameSummaryBM(
            round_number=3,
            players_alive=["Han Solo", "Leia", "Skywalker", "VADER"],
            players_voted_off=["Maul", "Jaba"],
            last_vote_outcome="Jaba was voted off as an AI imposter.",
            textual_summary="Skywalker is making a weak accusation with no actual evidence."
        ).model_dump_json()
    },
    answer=SimplePhraseBM(
        phrase="Lmao ok."
        )
    ),
    # Playful Response
    QAs(
        question={
            "minutes": "\n".join([
                "Skywalker: What if we just vote randomly?",
                "Han Solo: Bro "
            ]),
            "game_state": GameSummaryBM(
                round_number=1,
                players_alive=["Han Solo", "Leia", "Skywalker", "VADER"],
                players_voted_off=[],
                last_vote_outcome="N/A",
                textual_summary="Skywalker is joking about voting randomly instead of using logic."
            ).model_dump_json()
        },
        answer=SimplePhraseBM(
            phrase="haha wild."
        )
    ),
    # CHILL
    QAs(
        question={
            "minutes": "\n".join([
                "Han Solo: Nahhh, VADER def an AI.",
                "Skywalker: Wait fr??"
            ]),
            "game_state": GameSummaryBM(
                round_number=2,
                players_alive=["Han Solo", "Leia", "Skywalker", "VADER"],
                players_voted_off=["Maul"],
                last_vote_outcome="Maul was wrongly voted off as a human.",
                textual_summary="Han Solo is trying to build suspicion on VADER."
            ).model_dump_json()
        },
        answer=SimplePhraseBM(
            phrase="Lol chill."
        )
    ),
    # CONFUSED
    QAs(
        question={
            "minutes": "\n".join([
                "Leia: VADER, what's ur fav color?",
                "Skywalker: Huh?"
            ]),
            "game_state": GameSummaryBM(
                round_number=3,
                players_alive=["Han Solo", "Leia", "Skywalker", "VADER"],
                players_voted_off=["Maul", "Jaba"],
                last_vote_outcome="Jaba was voted off as an AI imposter.",
                textual_summary="Leia randomly asked VADER a question instead of focusing on the game."
            ).model_dump_json()
        },
        answer=SimplePhraseBM(
            phrase="wait what"
        )
    )
]

JOKE_MAIN_HEADER = "Given the current minutes and game state, choose a joke to make and provide \
    reasoning. Your joke shouldn't be corny, offensive, or too serious, and should be appropriate \
        fit the conversation naturally without being forced"
JOKE_EXAMPLES = [
    # Lighthearted Game-Related Joke
    QAs(
        question={
            "minutes": "\n".join([
                "Leia: I swear the AI are playing us right now.",
                "Skywalker: Lowkey, they probably just laughing at us."
            ]),
            "game_state": GameSummaryBM(
                round_number=2,
                players_alive=["Han Solo", "Leia", "Skywalker", "VADER"],
                players_voted_off=["Maul"],
                last_vote_outcome="Maul was wrongly voted off as a human.",
                textual_summary="Players are realizing they might be making mistakes, AI imposters are still hidden."
            ).model_dump_json()
        },
        answer=JokeBM(
            joke_text="Bro, what if the AI is just chillin, watching us struggle like 'damn these humans dumb'",
            reasoning="A fun joke about how the AI imposters must think we're clueless. Keeps the convo light.",
            joke_target="AI Imposters",
            joke_tone="lighthearted"
        )
    ),

    # Awkward Deflection
    QAs(
        question={
            "minutes": "\n".join([
                "Han Solo: Bro VADER not saying much...",
                "Leia: Yeah, explain yourself VADER."
            ]),
            "game_state": GameSummaryBM(
                round_number=3,
                players_alive=["Han Solo", "Leia", "Skywalker", "VADER"],
                players_voted_off=["Jaba"],
                last_vote_outcome="Jaba was voted off as an AI imposter.",
                textual_summary="VADER is being put on the spot for not talking much."
            ).model_dump_json()
        },
        answer=JokeBM(
            joke_text="Uhhh… so… how 'bout them space stocks? ",
            reasoning="I needed to change the subject fast and had nothing else to say. Awkward humor FTW.",
            joke_target="The Situation",
            joke_tone="awkward"
        )
    ),

    # Self-Deprecating Humor
    QAs(
        question={
            "minutes": "\n".join([
                "Leia: I feel like I'm playing this all wrong.",
                "Skywalker: Nah u good. VADER tho..."
            ]),
            "game_state": GameSummaryBM(
                round_number=1,
                players_alive=["Han Solo", "Leia", "Skywalker", "VADER"],
                players_voted_off=[],
                last_vote_outcome="N/A",
                textual_summary="Leia is doubting her game skills, Skywalker shifts focus to VADER."
            ).model_dump_json()
        },
        answer=JokeBM(
            joke_text="LMAO I'm so bad at this game, I'd probably vote myself out if I could. ",
            reasoning="Makes me seem harmless so I don't get targeted. Self-deprecating humor to ease tension.",
            joke_target="Self",
            joke_tone="self-deprecating"
        )
    ),

    # Mocking a Wild Accusation
    QAs(
        question={
            "minutes": "\n".join([
                "Han Solo: Bro I SWEAR Leia blinked weird.",
                "Leia: What? That's ur reason??"
            ]),
            "game_state": GameSummaryBM(
                round_number=2,
                players_alive=["Han Solo", "Leia", "Skywalker", "VADER"],
                players_voted_off=["Maul"],
                last_vote_outcome="Maul was wrongly voted off as a human.",
                textual_summary="Han Solo is making a wild accusation based on body language."
            ).model_dump_json()
        },
        answer=JokeBM(
            joke_text="‘Skywalker blinked weird, he's def AI' Y'all out here on detective mode fr.",
            reasoning="Mocking how ridiculous some accusations get in the game. Adds humor to defuse tension.",
            joke_target="Accusations",
            joke_tone="lighthearted"
        )
    ),

    # Playfully Calling Someone Out
    QAs(
        question={
            "minutes": "\n".join([
                "Leia: Wow Skywalker been real quiet.",
                "Skywalker: I just don't got much to say rn."
            ]),
            "game_state": GameSummaryBM(
                round_number=1,
                players_alive=["Han Solo", "Leia", "Skywalker", "VADER"],
                players_voted_off=[],
                last_vote_outcome="N/A",
                textual_summary="Skywalker is being quiet but hasn't done anything suspicious yet."
            ).model_dump_json()
        },
        answer=JokeBM(
            joke_text="Bro, Leia been real quiet... calculating her next move?",
            reasoning="Jokingly pushing suspicion onto Leia in a fun way, without actually accusing her.",
            joke_target="Leia",
            joke_tone="playful"
        )
    ),

    # Obvious Sarcasm
    QAs(
        question={
            "minutes": "\n".join([
                "Skywalker: Let's just vote randomly, see what happens.",
                "Leia: NO STOP."
            ]),
            "game_state": GameSummaryBM(
                round_number=2,
                players_alive=["Han Solo", "Leia", "Skywalker", "VADER"],
                players_voted_off=["Maul"],
                last_vote_outcome="Maul was wrongly voted off as a human.",
                textual_summary="Skywalker suggests a chaotic strategy, Leia is against it."
            ).model_dump_json()
        },
        answer=JokeBM(
            joke_text="Oh yeah, let's just RANDOMLY vote. Flawless strategy. 10/10. No notes.",
            reasoning="Someone suggested voting randomly, so I hit them with sarcasm.",
            joke_target="Bad strategy suggestion",
            joke_tone="sarcastic"
        )
    ),

    # Deflecting Suspicion with a Meme Reference
    QAs(
        question={
            "minutes": "\n".join([
                "Han Solo: We need to vote out VADER.",
                "Leia: Are we sure tho?"
            ]),
            "game_state": GameSummaryBM(
                round_number=3,
                players_alive=["Han Solo", "Leia", "Skywalker", "VADER"],
                players_voted_off=["Maul", "Jaba"],
                last_vote_outcome="Jaba was voted off as an AI imposter.",
                textual_summary="Han Solo is making a push to vote out VADER."
            ).model_dump_json()
        },
        answer=JokeBM(
            joke_text="Y'all blaming me? That's crazy. Trust no one, not even yourself. *insert Spider-Man pointing meme*",
            reasoning="I'm being accused, so I use humor to redirect the focus elsewhere.",
            joke_target="Accusation",
            joke_tone="deflecting"
        )
    ),

    # Stupid but Funny Distraction
    QAs(
        question={
            "minutes": "\n".join([
                "Skywalker: But what if we're wrong about all this?",
                "Han Solo: Then we L."
            ]),
            "game_state": GameSummaryBM(
                round_number=2,
                players_alive=["Han Solo", "Leia", "Skywalker", "VADER"],
                players_voted_off=["Maul"],
                last_vote_outcome="Maul was wrongly voted off as a human.",
                textual_summary="Players are overthinking the situation."
            ).model_dump_json()
        },
        answer=JokeBM(
            joke_text="Wait... what if the REAL imposter was the friends we made along the way?",
            reasoning="Just saying dumb stuff to make people laugh and throw off the convo.",
            joke_target="The Game Itself",
            joke_tone="random"
        )
    )
]

QUESTION_MAIN_HEADER = "Given the current minutes and game state, choose a player to question, \
    ask them a question, context that justifies the question, and the intent behind the question, \
    and the strategy type that asking this question invokes."
QUESTION_EXAMPLES = [
    # Information - Clarifying a Vote
    QAs(
        question={
            "minutes": "\n".join([
                "Han Solo: Leia, who did you vote for last round?",
                "Leia: I honestly don't remember."
                "Skywalker: Idk, kinda weird."
            ]),
            "game_state": GameSummaryBM(
                round_number=2,
                players_alive=["Han Solo", "Leia", "Skywalker", "VADER"],
                players_voted_off=["Maul"],
                last_vote_outcome="Maul was wrongly voted off as a human.",
                textual_summary="Leia voted very quickly, making her look suspicious."
            ).model_dump_json()
        },
        answer=QuestionBM(
            question_text="how could you not remember??",
            context="Leia won't reveal who she voted for last round, and I want to know why.",
            intent="To figure out why Leia is being secretive about her vote.",
            target_player="Leia",
            strategy_type="information"
        )
    ),

    # Pressure - Calling Out a Quiet Player
    QAs(
        question={
            "minutes": "\n".join([
                "Han Solo: Skywalker, u been REAL quiet.",
                "Leia: Yeah, not much from them..."
            ]),
            "game_state": GameSummaryBM(
                round_number=3,
                players_alive=["Han Solo", "Leia", "Skywalker", "VADER"],
                players_voted_off=["Jaba"],
                last_vote_outcome="Jaba was voted off as an AI imposter.",
                textual_summary="VADER has barely spoken, raising suspicion."
            ).model_dump_json()
        },
        answer=QuestionBM(
            question_text="Skywalker, u good? Why so quiet?",
            context="Skywalker hasn't talked much this round, and people are noticing.",
            intent="Apply pressure to Skywalker and see if they slip up.",
            target_player="Skywalker",
            strategy_type="pressure"
        )
    ),

    # Humor - Deflecting Suspicion
    QAs(
        question={
            "minutes": "\n".join([
                "Leia: Ok but what if it's Skywalker tho?",
                "Skywalker: ME? Nah fam. I'm tellin you it is VADER."
            ]),
            "game_state": GameSummaryBM(
                round_number=1,
                players_alive=["Han Solo", "Leia", "Skywalker", "VADER"],
                players_voted_off=[],
                last_vote_outcome="N/A",
                textual_summary="Leia is casually throwing suspicion on Skywalker, but there's no strong case."
            ).model_dump_json()
        },
        answer=QuestionBM(
            question_text="Skywalker, u tryna frame me rn or is this just bad vibes?",
            context="Leia jokingly accused Skywalker, and I want to keep the convo fun.",
            intent="Lighten the mood while subtly questioning Skywalker.",
            target_player="Skywalker",
            strategy_type="humor"
        )
    ),
]

GSU_HEADERS = {
    "minutes": "Here is the conversation so far this round\nMINUTES:\n",
    "game_state": "\n\nHere is the current game state\nGAME STATE:\n",
    "vote_result": "\n\nHere is the vote result\nVOTE RESULT:\n"
}
GSU_MAIN_HEADER = """Given the current minutes, game state, and vote result, \
    update the game state. by:
    1. increasing the round number by 1
    2. updating the list of players if needed based on the vote result
    3. updating the list of players voted off based on the vote result
    4. updating the last vote outcome
    5. updating the summary of the game state. Be sure to include in depth summarization of the \
        previous round discussion and vote outcome."""
GSU_EXAMPLES = [
    # Example 1: First Vote - AI Eliminated
    QAs(
        question={
            "minutes": "\n".join([
                "Leia: I think Jaba is acting weird.",
                "Han Solo: Yeah, I'm down to vote Jaba.",
                "Skywalker: Sounds good.",
                "VADER: Jaba is sus.",
                "Jaba: WAIT NO",
                "Maul: Too late bro"
            ]),
            "game_state": GameSummaryBM(
                round_number=0,
                players_alive=["Han Solo", "Leia", "Skywalker", "VADER", "Jaba", "Maul"],
                players_voted_off=[],
                last_vote_outcome="N/A",
                textual_summary="The game has just begun. Players are introducing themselves."
            ).model_dump_json(),
            "vote_result": json.dumps({"eliminated": "Jaba", "was_ai": True})
        },
        answer=GameSummaryBM(
            round_number=1,
            players_alive=["Han Solo", "Leia", "Skywalker", "VADER", "Maul"],
            players_voted_off=["Jaba"],
            last_vote_outcome="Jaba was voted off as an AI imposter.",
            textual_summary="The first vote took place. Jaba was accused of being an AI and eliminated. "
                    "He turned out to be an AI imposter. The remaining five players continue the discussion."
        )
    ),

    # Example 2: Second Vote - A Human is Wrongly Voted Out
    QAs(
        question={
            "minutes": "\n".join([
                "Leia: Ok, so Maul was being weird about Jaba.",
                "Han Solo: That's true… but VADER was quiet too.",
                "Skywalker: I think it's Maul.",
                "Maul: Bruh what, I LITERALLY said Jaba was sus first??",
                "VADER: idk man, you seem mad defensive.",
                "Leia: Maul's gotta go."
            ]),
            "game_state": GameSummaryBM(
                round_number=1,
                players_alive=["Han Solo", "Leia", "Skywalker", "VADER", "Maul"],
                players_voted_off=["Jaba"],
                last_vote_outcome="Jaba was voted off as an AI imposter.",
                textual_summary="Jaba was the first to be eliminated. The humans continue the discussion."
            ).model_dump_json(),
            "vote_result": json.dumps({"eliminated": "Maul", "was_ai": False})
        },
        answer=GameSummaryBM(
            round_number=2,
            players_alive=["Han Solo", "Leia", "Skywalker", "VADER"],
            players_voted_off=["Jaba", "Maul"],
            last_vote_outcome="Maul was voted off but was actually a human.",
            textual_summary="The second vote led to Maul being eliminated after Leia and Skywalker pushed suspicion onto him. "
                    "However, it turned out Maul was actually a human, raising doubts about the vote. "
                    "Only four players remain, with at least one AI still hidden among them."
        )
    )
]
