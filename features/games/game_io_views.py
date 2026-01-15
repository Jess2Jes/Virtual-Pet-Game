"""
features/game_io_views.py

Presentation-only helpers for printing menus and stock listings.

Responsibilities:
- Centralize UI rendering strings and formatting.
- Keep `features.game.Game` focused on coordination rather than UI composition.

Hard constraints:
- Must not change any printed text, menu order, or numbering.
"""

from __future__ import annotations

from typing import Iterable

from constants.configs import LINE
from utils.ports import IOPort


class GameView:
    """UI rendering helper for Game menus and static blocks."""

    def __init__(self, io: IOPort):
        self._io = io

    @staticmethod
    def _render_lines(items: Iterable[str]) -> str:
        return "\n".join(items)

    def print_main_interact_menu(self) -> None:
        menu = [
            "=" * 120,
            "1. Feed",
            "2. Play",
            "3. Bath",
            "4. Give Potion",
            "5. Sleep",
            "6. Take a walk",
            "7. Talk to pet",
            "8. Exit",
            LINE,
        ]
        self._io.write(self._render_lines(menu))

    def print_talk_menu(self) -> None:
        lines = [
            "\n" + LINE,
            "Topics of Conversation: ",
            LINE,
            "1. What do you want to do today?",
            "2. What is your favourite food?",
            "3. Ask me anything",
            "4. Can you give me money?",
            "5. Tell a joke",
            "6. Goodbye",
            LINE,
        ]
        self._io.write("\n".join(lines))

    def print_conversation_menu(self) -> None:
        lines = [
            "\n" + LINE,
            "1. Music Taste",
            "2. Favourite Food",
            "3. That's enough about me",
            LINE,
        ]
        self._io.write("\n".join(lines))

    def print_potion_requirement(self, title: str) -> None:
        lines = [
            "",
            LINE,
            title,
            LINE,
            "1. Fat Burner can be used if your energy is below 50.",
            "2. Health Potion can be used if your health is below 100.",
            "3. Energizer can be used if your energy is below 100.",
            "4. Adult Potion can be used if your age is below 20.",
            LINE + "\n",
        ]
        self._io.write("\n".join(lines))