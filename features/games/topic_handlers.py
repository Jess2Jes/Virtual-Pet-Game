"""
features/topic_handlers.py

Conversation-topic handling abstractions.

Responsibilities:
- Remove `topic["type"]` branching from the Game coordinator.
- Provide handler implementations for the existing topic shapes:
  - "Music Taste"
  - "Favourite Food/Drink"

Hard constraints:
- No change to strings, prompts, branching conditions, or resulting state mutations.

Collaboration:
- `ConversationEngine` selects an unused topic and delegates the logic to a handler.
- Handlers use `UserContext` to preserve legacy `User.current_user` writes.
"""

from __future__ import annotations

from typing import Any, Dict, List, Protocol
from random import choice as ch

from utils.ports import IOPort
from utils.colorize import cyan

from .user_context import UserContext
from features.pet import VirtualPet


class TopicHandler(Protocol):
    """Handler for a single topic dictionary."""
    def handle(self, pet: VirtualPet, topic: Dict[str, Any]) -> bool: ...


class ConversationEngine:
    """
    Select-and-dispatch engine for conversation topics.

    Responsibilities:
    - Filter available topics by type.
    - Select an unused topic using the same selection semantics.
    - Delegate execution to a TopicHandler keyed by topic["type"].

    Behavior is preserved:
    - Same "all out of topics" messages are emitted by the Game layer before calling engine.
    - Selection uses the same "topics_used" list mechanics as the legacy code.
    """

    def __init__(self, io: IOPort, topics_used: List[Dict[str, Any]], handlers: Dict[str, TopicHandler]):
        self._io = io
        self._topics_used = topics_used
        self._handlers = handlers

    def _select_unused_topic(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        while True:
            random_topic = ch(questions)

            if random_topic not in self._topics_used:
                self._topics_used.append(random_topic)
                break

            if all(q in self._topics_used for q in questions):
                break

        return random_topic

    def handle_random_topic_of_type(self, pet: VirtualPet, topics: List[Dict[str, Any]], topic_type: str) -> bool:
        questions = [q for q in topics if q.get("type") == topic_type]
        random_topic = self._select_unused_topic(questions)
        handler = self._handlers.get(topic_type)
        if handler is None:
            # Preserve "no-op" safety; game currently never reaches unknown types.
            return False
        return handler.handle(pet, random_topic)


class MusicTasteTopicHandler:
    """Handler for 'Music Taste' topics (preserves original branching and writes)."""

    def __init__(self, io: IOPort, user_context: UserContext):
        self._io = io
        self._user_context = user_context

    def handle(self, pet: VirtualPet, topic: Dict[str, Any]) -> bool:
        question = topic.get("question", "")
        choose_text = topic.get("choose", "")
        ans = self._io.read(cyan(f"\n{pet.name} {pet.emoji} : {question}\n{choose_text}")).lower().strip()

        like_topic = "dislike" not in question

        if topic.get("answer") is not None:
            self._handle_answer_type(pet, topic, ans, like_topic)
        elif topic.get("option") is not None:
            self._handle_option_type(pet, topic, ans)
        else:
            self._handle_list_type(pet, ans)

        return True

    def _handle_answer_type(self, pet: VirtualPet, topic: Dict[str, Any], ans: str, like_topic: bool) -> None:
        is_valid_answer = ans in topic.get("answer", [])

        if is_valid_answer and like_topic:
            self._io.write(cyan(f"\n{pet.name} {pet.emoji} : So, that's your fav! Mine is {getattr(pet, 'music_taste', 'unknown')}."))
            self._user_context.music()["Fav_Music"] = ans
        elif is_valid_answer and not like_topic:
            self._io.write(cyan(
                f"\n{pet.name} {pet.emoji} : So, that's not your cup of tea, Mine is {getattr(pet, 'dislike_music', 'unknown')}."
            ))
            self._user_context.music()["Dislike_Music"] = ans
        else:
            self._io.write(cyan(f"\n{pet.name} {pet.emoji} : Not sure I've ever heard that genre, but thanks for telling me!"))
            key = "Fav_Music" if like_topic else "Dislike_Music"
            self._user_context.music()[key] = ans

    def _handle_option_type(self, pet: VirtualPet, topic: Dict[str, Any], ans: str) -> None:
        first_option = topic.get("option")[0]
        is_first_option = ans == first_option
        is_valid_option = ans in topic.get("option", [])

        if is_valid_option and not is_first_option:
            self._io.write(cyan(f"\n{pet.name} {pet.emoji} : You should try it now! They had added your fav music playlist there! "))
            self._user_context.music()["Have_Used_Spotify"] = True
        else:
            self._io.write(cyan(f"\n{pet.name} {pet.emoji} : Have you heard your new fav music playlist come out there?  Go check it now!"))
            self._user_context.music()["Have_Used_Spotify"] = False

    def _handle_list_type(self, pet: VirtualPet, ans: str) -> None:
        list_ans = [x.strip() for x in ans.split(",")]

        if len(list_ans) == 3:
            self._io.write(cyan(f"\n{pet.name} {pet.emoji} : Owh! Mine is {', '.join(getattr(pet, 'songs', []))}."))
            self._user_context.music()["Fav_Songs"] = list_ans
        else:
            self._io.write(cyan(f"\n{pet.name} {pet.emoji} : I agree too. That song almost break my heart."))
            self._user_context.music()["Fav_Lyrics"] = list_ans[0] if list_ans else ""


class FavouriteFoodTopicHandler:
    """Handler for 'Favourite Food/Drink' topics (preserves original branching and writes)."""

    def __init__(self, io: IOPort, user_context: UserContext):
        self._io = io
        self._user_context = user_context

    def handle(self, pet: VirtualPet, topic: Dict[str, Any]) -> bool:
        ans = self._io.read(cyan(f"\n{pet.name} {pet.emoji} : {topic.get('question', '')}\n")).lower().strip()

        if topic.get("option") is not None:
            self._handle_food_option_type(pet, topic, ans)
        else:
            self._handle_food_free_response(pet, topic, ans)

        return True

    def _handle_food_option_type(self, pet: VirtualPet, topic: Dict[str, Any], ans: str) -> None:
        first_option = topic.get("option")[0]
        is_first_option = ans == first_option
        is_valid_option = ans in topic.get("option", [])

        if not is_valid_option:
            return

        if first_option == "sweet":
            self._handle_sweet_salty_preference(pet, ans, is_first_option)
        elif first_option == "y":
            self._handle_food_origin_preference(pet, ans, is_first_option)

    def _handle_sweet_salty_preference(self, pet: VirtualPet, ans: str, is_sweet: bool) -> None:
        if is_sweet:
            self._io.write(cyan(f"\n{pet.name} {pet.emoji} : Owh, so you like sweet. I think you'd love Belgian Chocolate! "))
            self._user_context.food()["Like_Sweet_Salty"] = ans
        else:
            self._io.write(cyan(f"\n{pet.name} {pet.emoji} : Owh, so you like salty food. I think you'd love Egg and Toast!"))
            self._user_context.food()["Like_Sweet_Salty"] = ans

    def _handle_food_origin_preference(self, pet: VirtualPet, ans: str, is_traditional: bool) -> None:
        if is_traditional:
            self._io.write(cyan(f"\n{pet.name} {pet.emoji} : Our own country food is the best! I will give it a five star ⭐!"))
            self._user_context.food()["Inter_Trad_Food"] = ans
        else:
            self._io.write(cyan(f"\n{pet.name} {pet.emoji} : Well, International Food also tastes better!"))
            self._user_context.food()["Inter_Trad_Food"] = ans

    def _handle_food_free_response(self, pet: VirtualPet, topic: Dict[str, Any], ans: str) -> None:
        if "What is your favorite food?" in topic.get("question", ""):
            self._io.write(cyan(f"\n{pet.name} {pet.emoji} : That's great! My favourite food is {pet.fav_food}!"))
            self._user_context.food()["Fav_Food"] = ans
        else:
            self._io.write(cyan(f"\n{pet.name} {pet.emoji} : I'm glad to hear that! Thanks for sharing."))