"""Minigame strategy interfaces segregated for ISP compliance."""

from abc import ABC, abstractmethod
from typing import Any, Dict

class IGameLoop(ABC):
    """Interface for the core game loop construction."""
    @abstractmethod
    def build_game(self) -> Any:
        ...


class IScoreable(ABC):
    """Interface for scoring/evaluation responsibilities."""
    @abstractmethod
    def evaluate(self, answer: Any) -> Dict[str, Any]:
        ...

    @abstractmethod
    def reward(self, result: Dict[str, Any]) -> Dict[str, int]:
        ...


class IRenderable(ABC):
    """Interface for menu/display responsibilities."""
    @abstractmethod
    def display_menu(self) -> None:
        ...


class MinigameStrategy(IGameLoop, IScoreable, IRenderable):
    """Abstract base class for minigame implementations with segregated concerns."""

    name: str

    @abstractmethod
    def setup(self, player: Any, pet: Any) -> None:
        """Prepare internal state before the game begins."""
        ...

    @abstractmethod
    def get_input(self) -> Any:
        """Collect any initial input from the player (difficulty, options, etc.)."""
        ...

    @abstractmethod
    def build_question(self) -> Any:
        """Build the questions or game board prior to playing."""
        ...

    @abstractmethod
    def play(self, player: Any, pet: Any) -> Dict[str, int]:
        """High-level convenience that runs the full minigame flow and returns rewards."""
        ...